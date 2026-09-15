import pytest

from api_interview_lab.platform.config import Settings


def test_production_rejects_sqlite_and_fault_injection(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    cfg = Settings(jwt_secret="j" * 40, cursor_secret="c" * 40,
                   database_url="sqlite://", credentials={"user": {}})
    with pytest.raises(ValueError, match="PostgreSQL"):
        cfg.validate()
    cfg.database_url = "postgresql+psycopg://user:password@db/app"
    cfg.fault_fail = True
    with pytest.raises(ValueError, match="Fault injection"):
        cfg.validate()
    cfg.fault_fail = False
    cfg.validate()


def test_initial_schema_does_not_seed_demo_records(tmp_path, monkeypatch):
    from sqlalchemy import func, select

    from api_interview_lab.platform import schema
    from api_interview_lab.platform.store import Store, jobs, records

    monkeypatch.delenv("APP_ENV", raising=False)
    url = "sqlite:///" + str(tmp_path / "schema.db")
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("JWT_SECRET", "j" * 40)
    monkeypatch.setenv("CURSOR_SECRET", "c" * 40)
    schema.main()
    schema.main()
    store = Store(url)
    with store.engine.connect() as connection:
        assert connection.scalar(select(func.count()).select_from(records)) == 0
        assert connection.scalar(select(func.count()).select_from(jobs)) == 0
    store.engine.dispose()
