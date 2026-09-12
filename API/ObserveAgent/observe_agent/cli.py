"""Commands for knowledge ingestion and local incident exercises."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .api import build_agent
from .config import Settings
from .models import Incident, IncidentFeedback


def main() -> None:
    parser = argparse.ArgumentParser(description="ObserveAgent local operations")
    subparsers = parser.add_subparsers(dest="command", required=True)
    ingest = subparsers.add_parser("ingest", help="Chunk, embed, and index a Markdown document")
    ingest.add_argument("path", type=Path)
    ingest.add_argument("--source-id")
    ingest.add_argument("--service", default="all")
    incident = subparsers.add_parser("incident", help="Run one incident JSON through the agent")
    incident.add_argument("path", type=Path)
    feedback = subparsers.add_parser("feedback", help="Apply reviewed incident feedback JSON")
    feedback.add_argument("incident_id")
    feedback.add_argument("path", type=Path)
    args = parser.parse_args()

    agent = build_agent(Settings())
    if args.command == "ingest":
        source_id = args.source_id or args.path.name
        chunk_ids = agent.knowledge.ingest(
            source_id,
            args.path.read_text(encoding="utf-8"),
            {
                "source_type": "runbook",
                "review_status": "approved",
                "tenant_scope": "global",
                "service": args.service,
            },
        )
        print(json.dumps({"source_id": source_id, "chunks": chunk_ids}, indent=2))
    elif args.command == "incident":
        payload = Incident.model_validate_json(args.path.read_text(encoding="utf-8"))
        print(agent.handle_incident(payload).model_dump_json(indent=2))
    else:
        payload = IncidentFeedback.model_validate_json(args.path.read_text(encoding="utf-8"))
        print(json.dumps({"chunks": agent.apply_feedback(args.incident_id, payload)}, indent=2))


if __name__ == "__main__":
    main()
