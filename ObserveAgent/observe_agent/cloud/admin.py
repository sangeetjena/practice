"""One-shot schema initialization, outbox publication and index repair commands.

Example: python -m observe_agent.cloud.admin migrate runs SQL/graph migrations
before deploying workers. Reindex takes an explicit tenant so maintenance cannot
accidentally mix customer embedding profiles.
"""

import argparse

from langgraph.checkpoint.postgres import PostgresSaver

from .config import CloudSettings
from .database import Database, metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["migrate", "publish", "reindex", "drain"])
    parser.add_argument("--tenant")
    args = parser.parse_args()
    settings = CloudSettings.from_env()
    db = Database(settings.database_url)
    if args.command == "migrate":
        metadata.create_all(db.engine)
        with PostgresSaver.from_conn_string(settings.checkpoint_url) as saver:
            saver.setup()
        print("Schema initialized; rerunning is safe for this schema version.")
    elif args.command == "publish":
        from .transport import OutboxPublisher

        print({"published": OutboxPublisher(db, settings.topic).publish()})
    else:
        from .runtime import GraphFactory, Worker

        factory = GraphFactory(settings, db)
        if args.command == "reindex":
            if args.tenant not in settings.tenants:
                parser.error("--tenant must name a configured tenant")
            with factory.open(args.tenant) as agent:
                print({"reindexed": agent.knowledge.reindex()})
        else:
            worker = Worker(db, factory)
            for event in db.pending():
                print({"event_id": event["id"], "state": worker.process(event["id"])})
    db.engine.dispose()


if __name__ == "__main__":
    main()
