from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from api_interview_lab.domain.models import Order, OrderStatus


class SQLiteOrderRepository:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)
        if self.database_path != ":memory:":
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    product TEXT NOT NULL,
                    quantity INTEGER NOT NULL CHECK (quantity > 0),
                    unit_price REAL NOT NULL CHECK (unit_price >= 0),
                    status TEXT NOT NULL
                )
                """
            )

    @staticmethod
    def _to_order(row: sqlite3.Row) -> Order:
        return Order(
            id=row["id"], customer_id=row["customer_id"], product=row["product"],
            quantity=row["quantity"], unit_price=row["unit_price"],
            status=OrderStatus(row["status"]),
        )

    def list(self, *, offset: int, limit: int) -> tuple[list[Order], int]:
        with self._connection() as connection:
            total = connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
            rows = connection.execute(
                "SELECT * FROM orders ORDER BY id LIMIT ? OFFSET ?", (limit, offset)
            ).fetchall()
        return [self._to_order(row) for row in rows], total

    def get(self, order_id: str) -> Order | None:
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        return self._to_order(row) if row else None

    def create(self, order: Order) -> Order:
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)",
                (order.id, order.customer_id, order.product, order.quantity,
                 order.unit_price, order.status.value),
            )
        return order

    def healthcheck(self) -> bool:
        try:
            with self._connection() as connection:
                return connection.execute("SELECT 1").fetchone()[0] == 1
        except sqlite3.Error:
            return False

