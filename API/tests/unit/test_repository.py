from api_interview_lab.data.sqlite_repository import SQLiteOrderRepository


def test_repository_paginates(repository: SQLiteOrderRepository) -> None:
    rows, total = repository.list(offset=2, limit=2)
    assert total == 6
    assert [row.id for row in rows] == ["ORD-3", "ORD-4"]


def test_repository_returns_none_for_missing(repository: SQLiteOrderRepository) -> None:
    assert repository.get("missing") is None

