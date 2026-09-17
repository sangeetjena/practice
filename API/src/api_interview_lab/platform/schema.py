"""Explicit initial schema creation with no demo rows; not a migration framework."""
import os

from .store import Store, metadata


def main():
    url = os.environ["DATABASE_URL"]
    if os.getenv("APP_ENV") == "production" and not url.startswith("postgresql+psycopg://"):
        raise ValueError("Production schema initialization requires PostgreSQL")
    store = Store(url)
    try:
        metadata.create_all(store.engine)
    finally:
        store.engine.dispose()
    print("Initial schema created. No sample records or credentials were added.")


if __name__ == "__main__":
    main()
