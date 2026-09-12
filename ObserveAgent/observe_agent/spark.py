"""Catalog-driven Spark configuration investigation and reviewable GitHub patches.

This intentionally supports flat JSON Spark configuration only. Runtime evidence is
supplied by the operator/collector; a remembered fix alone never authorizes a patch.
"""

import base64
import difflib
import hashlib
import json
import re
from pathlib import Path
from typing import TypedDict

import httpx
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt


class SparkState(TypedDict, total=False):
    incident_id: str
    tenant_id: str
    job_id: str
    deployed_commit: str
    evidence: dict
    job: dict
    source: str
    blob_sha: str
    patch: str
    updated_source: str
    branch: str
    status: str
    result: dict


class GitHubRepository:
    def __init__(self, token, allowed_repositories, client=None):
        self.allowed = set(allowed_repositories)
        self.client = client or httpx.Client(
            base_url="https://api.github.com",
            timeout=10,
            follow_redirects=False,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
        )

    def request(self, method, repository, path, **kwargs):
        if repository not in self.allowed or not re.fullmatch(r"[\w.-]+/[\w.-]+", repository):
            raise ValueError("repository not allowed")
        response = self.client.request(method, f"/repos/{repository}/{path}", **kwargs)
        response.raise_for_status()
        return response.json()

    def read(self, job, commit):
        if not re.fullmatch(r"[a-fA-F0-9]{40}", commit):
            raise ValueError("a full deployed commit SHA is required")
        path = job["configuration_path"]
        if path.startswith("/") or ".." in path.split("/") or not path.endswith(".json"):
            raise ValueError("catalog must select a relative JSON configuration path")
        data = self.request("GET", job["repository"], f"contents/{path}", params={"ref": commit})
        return base64.b64decode(data["content"]).decode(), data["sha"]

    def publish(self, state):
        job = state["job"]
        repo = job["repository"]
        base = job.get("base", "master")
        current = self.request("GET", repo, f"git/ref/heads/{base}")["object"]["sha"]
        if current != state["deployed_commit"]:
            raise ValueError("base moved or differs from deployed commit; reinvestigate before PR")
        branch = state["branch"]
        # An existing branch is deliberately not overwritten on replay.
        self.request("POST", repo, "git/refs", json={"ref": f"refs/heads/{branch}", "sha": current})
        self.request(
            "PUT",
            repo,
            f"contents/{job['configuration_path']}",
            json={
                "message": f"Propose Spark memory fix for {state['incident_id']}",
                "branch": branch,
                "sha": state["blob_sha"],
                "content": base64.b64encode(state["updated_source"].encode()).decode(),
            },
        )
        return self.request(
            "POST",
            repo,
            "pulls",
            json={
                "head": branch,
                "base": base,
                "draft": True,
                "title": f"Spark memory proposal: {state['incident_id']}",
                "body": "Evidence-backed configuration proposal. Human approval recorded.\n\n"
                + json.dumps(state["evidence"], indent=2)
                + "\n\n```diff\n"
                + state["patch"]
                + "\n```\n"
                + "Validate on a canary run; revert this commit if recovery is not confirmed.",
            },
        )


def build_spark_graph(catalog_path, repository, checkpointer, *, execute=False):
    catalog = json.loads(Path(catalog_path).read_text())

    def discover(state):
        job = catalog[state["job_id"]]
        if job["tenant_id"] != state["tenant_id"]:
            raise ValueError("job belongs to another tenant")
        return {"job": job}

    def inspect(state):
        source, sha = repository.read(state["job"], state["deployed_commit"])
        return {"source": source, "blob_sha": sha}

    def propose(state):
        evidence = state["evidence"]
        config = json.loads(state["source"])
        key = "spark.executor.memory"
        # These required observations must come from runtime diagnostics, not similarity score.
        required = ("executor_heap_oom", "skew_ruled_out", "overrides_ruled_out")
        if any(evidence.get(k) is not True for k in required):
            return {"status": "needs_evidence"}
        old = config.get(key)
        new = evidence.get("proposed_executor_memory")
        if evidence.get("effective_executor_memory") != old:
            return {"status": "configuration_drift"}
        if not all(isinstance(v, str) and re.fullmatch(r"[1-9][0-9]*g", v) for v in [old, new]):
            raise ValueError("memory must be an integer GiB value such as 4g")
        if not int(old[:-1]) < int(new[:-1]) <= state["job"]["max_executor_memory_gib"]:
            raise ValueError("proposed memory exceeds catalog budget or is not an increase")
        config[key] = new
        updated = json.dumps(config, indent=2) + "\n"
        patch = "".join(
            difflib.unified_diff(
                state["source"].splitlines(True),
                updated.splitlines(True),
                fromfile=state["job"]["configuration_path"],
                tofile=state["job"]["configuration_path"],
            )
        )
        branch_id = hashlib.sha256(
            (state["incident_id"] + state["deployed_commit"] + updated).encode()
        ).hexdigest()[:16]
        return {
            "updated_source": updated,
            "patch": patch,
            "branch": f"observe-fix/{branch_id}",
            "status": "awaiting_approval",
        }

    def approve(state):
        decision = interrupt(
            {
                "patch": state["patch"],
                "repository": state["job"]["repository"],
                "evidence": state["evidence"],
            }
        )
        if not isinstance(decision, dict) or not decision.get("reviewer"):
            raise ValueError("reviewer is required")
        if decision.get("approved") is not True:
            return {"status": "rejected"}
        if not execute:
            return {"status": "dry_run"}
        return {"result": repository.publish(state), "status": "pr_opened"}

    graph = StateGraph(SparkState)
    for name, node in [
        ("discover", discover),
        ("inspect", inspect),
        ("propose", propose),
        ("approve", approve),
    ]:
        graph.add_node(name, node)
    graph.add_edge(START, "discover")
    graph.add_edge("discover", "inspect")
    graph.add_edge("inspect", "propose")
    graph.add_conditional_edges(
        "propose",
        lambda s: "approve" if s["status"] == "awaiting_approval" else END,
        {"approve": "approve", END: END},
    )
    graph.add_edge("approve", END)
    return graph.compile(checkpointer=checkpointer)
