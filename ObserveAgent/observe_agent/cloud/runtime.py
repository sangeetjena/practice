"""Build tenant-bound graph dependencies and process one durable event.

Example: Worker.process(event_id) loads the authoritative tenant/run from PostgreSQL,
locks that incident, resumes or starts LangGraph, and commits completion before ACK.
"""

import json
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path

import chromadb
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.types import Command

from ..actions import ActionPlanner
from ..agent import ReflexionAgent
from ..config import Settings
from ..features import IncidentFeatureExtractor
from ..models import ActionDecision, Incident, IncidentFeedback
from ..providers import build_embedder, build_reasoner
from ..telemetry import PrometheusMetricSource
from .effects import DurableActionExecutor
from .knowledge import TenantKnowledge


class GraphFactory:
    def __init__(self, settings, db):
        self.settings, self.db = settings, db
        self.client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
            ssl=settings.chroma_ssl,
            headers=json.loads(settings.chroma_headers),
        )

    @contextmanager
    def open(self, tenant_id):
        tenant = self.settings.tenants[tenant_id]
        # Global execution flags cannot expand a tenant's target allowlists.
        model_settings = replace(
            Settings(),
            prometheus_url=tenant["prometheus_url"],
            action_allowlist=tuple(tenant.get("action_allowlist", [])),
            http_allowed_hosts=tuple(tenant.get("http_allowed_hosts", [])),
            github_allowed_repositories=tuple(tenant.get("github_allowed_repositories", [])),
            email_allowed_recipients=tuple(tenant.get("email_allowed_recipients", [])),
        )
        model_settings.validate()
        knowledge = TenantKnowledge(self.db, self.client, build_embedder(model_settings), tenant_id)
        # Bundled knowledge is replicated into the tenant scope by trusted server code.
        source_id = "runbook:commerce-latency"
        path = Path(__file__).resolve().parents[2] / "data/runbooks/commerce-latency.md"
        if not path.exists():
            path = Path(__file__).resolve().parents[1] / "data/runbooks/commerce-latency.md"
        if path.exists() and not knowledge.has_active_source(source_id):
            knowledge.ingest(
                source_id,
                path.read_text(),
                {
                    "tenant_scope": tenant_id,
                    "service": "all",
                    "review_status": "approved",
                    "source_type": "runbook",
                },
            )
        else:
            knowledge.sync_source(source_id)
        with PostgresSaver.from_conn_string(self.settings.checkpoint_url) as saver:
            yield ReflexionAgent(
                IncidentFeatureExtractor(PrometheusMetricSource(tenant["prometheus_url"], 5)),
                knowledge,
                reasoner=build_reasoner(model_settings),
                knowledge_limit=model_settings.knowledge_limit,
                action_planner=ActionPlanner(model_settings),
                action_executor=DurableActionExecutor(model_settings, knowledge),
                checkpointer=saver,
            )


class Worker:
    def __init__(self, db, factory, max_attempts=5):
        self.db, self.factory, self.max_attempts = db, factory, max_attempts

    def process(self, event_id):
        event = self.db.event(event_id)
        with self.db.incident_lock(event["tenant_id"], event["incident_id"]):
            event = self.db.event(event_id)
            if event["state"] in {"done", "dead"}:
                return event["state"]
            row = self.db.get(event["tenant_id"], event["incident_id"])
            if row["run_id"] != event["run_id"] or row["revision"] != event["revision"]:
                raise ValueError("event does not match the current investigation revision")
            self.db.start(event)
            try:
                with self.factory.open(event["tenant_id"]) as agent:
                    result = self._run(agent, event, row)
                self.db.finish(event, result)
                return "done"
            except (
                Exception
            ) as error:  # Persist a sanitized failure; Pub/Sub retries nonterminal work.
                if self.db.fail(event, error, self.max_attempts):
                    return "dead"
                raise

    def _run(self, agent, event, row):
        run_id = row["run_id"]
        config = {"configurable": {"thread_id": run_id}}
        snapshot = agent.graph.get_state(config)
        if event["kind"] == "feedback":
            payload = {
                k: v
                for k, v in event["payload"].items()
                if k in {"decision", "confirmed_root_cause", "resolution", "notes", "resolved"}
            }
            feedback = IncidentFeedback(**payload, reviewer=event["payload"]["subject"])
            agent.apply_feedback(run_id, feedback)
            # Feedback records learning; it does not approve pending actions.
            return event["payload"]["previous_result"] or {"status": "completed"}
        if event["kind"] == "approval":
            if snapshot.next:
                if any(task.interrupts for task in snapshot.tasks):
                    payload = event["payload"]
                    decision = ActionDecision(
                        approved=payload["approved"],
                        reviewer=payload["subject"],
                        action_ids=payload["action_ids"],
                    )
                    state = agent.graph.invoke(Command(resume=decision.model_dump()), config)
                else:
                    state = agent.graph.invoke(None, config)  # Resume a failed node after approval.
                return agent._response(state).model_dump(mode="json")
            if snapshot.values.get("report"):
                return agent._response(snapshot.values).model_dump(mode="json")
            raise ValueError("approval checkpoint missing")
        if snapshot.values:
            if snapshot.next and not any(task.interrupts for task in snapshot.tasks):
                state = agent.graph.invoke(None, config)
                return agent._response(state).model_dump(mode="json")
            if snapshot.values.get("report"):
                result = agent._response(snapshot.values).model_dump(mode="json")
                if snapshot.next:
                    result["status"] = "awaiting_approval"
                return result
        payload = row["payload"]
        history = self.db.history(row["tenant_id"], row["id"])
        recent = [m["payload"]["content"] for m in history if m["kind"] == "message"][-20:]
        prior = event["payload"].get("previous_result") or {}
        context = json.dumps(
            {"recent_messages": recent, "previous_summary": prior.get("report", {}).get("summary")}
        )[:24000]
        incident = Incident(
            id=run_id,
            tenant_id=row["tenant_id"],
            title=payload["title"],
            service=payload["service"],
            started_at=payload["started_at"],
            environment=payload["environment"],
            action_context=payload["action_context"],
            annotations={**payload["annotations"], "untrusted_session_context": context},
        )
        return agent.handle_incident(incident).model_dump(mode="json")
