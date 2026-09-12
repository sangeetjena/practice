"""Run once per service database before starting replicas."""
from .config import Settings
from .store import Store

if __name__ == "__main__":
    cfg = Settings()
    cfg.validate()
    store = Store(cfg.database_url)
    store.initialize(cfg.service)
    store.engine.dispose()
