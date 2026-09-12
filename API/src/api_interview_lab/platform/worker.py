"""Durable DB-backed import worker: atomic claim, expiring lease, idempotent effects."""
import json
import logging
import signal
import time
import uuid

from sqlalchemy import and_, or_, select
from sqlalchemy.exc import SQLAlchemyError

from .config import Settings
from .store import Store, jobs


def process_one(store, now=None):
    now = int(time.time()) if now is None else now
    eligible = or_(jobs.c.state == 'pending',
                   and_(jobs.c.state == 'processing', jobs.c.lease < now))
    claim = uuid.uuid4().hex
    with store.engine.begin() as conn:
        row = conn.execute(select(jobs).where(eligible).limit(1)).mappings().first()
        if not row:
            return False
        # Compare-and-swap protects competing workers without DB-specific locking syntax.
        changed = conn.execute(jobs.update().where(
            jobs.c.tenant == row['tenant'], jobs.c.id == row['id'], eligible
        ).values(state='processing', claim=claim, lease=now + 60,
                 attempts=jobs.c.attempts + 1)).rowcount
        if changed != 1:
            return False
    owned = and_(jobs.c.tenant == row['tenant'], jobs.c.id == row['id'], jobs.c.claim == claim)
    try:
        ids = []
        for i, payload in enumerate(json.loads(row['payload'])):
            item = store.create_order(row['tenant'], f"job:{row['id']}:{i}", payload)
            ids.append(item['id'])
        values = {'state': 'succeeded', 'result': json.dumps({'created_ids': ids})}
    except SQLAlchemyError:
        values = {'state': 'failed' if row['attempts'] + 1 >= 3 else 'pending',
                  'result': json.dumps({'error': 'Database operation failed'})}
    with store.engine.begin() as conn:
        conn.execute(jobs.update().where(owned).values(**values))
    return True


def main():
    logging.basicConfig(level=logging.INFO)
    store = Store(Settings().database_url)
    running = True
    def stop(*args):
        nonlocal running
        running = False
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    while running:
        try:
            if not process_one(store):
                time.sleep(1)
        except SQLAlchemyError:
            logging.getLogger(__name__).warning('Worker database unavailable; retrying after backoff')
            time.sleep(2)
    store.engine.dispose()


if __name__ == '__main__':
    main()
