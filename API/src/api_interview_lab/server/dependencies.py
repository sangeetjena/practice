from functools import lru_cache

from api_interview_lab.config import get_settings
from api_interview_lab.data.sqlite_repository import SQLiteOrderRepository


@lru_cache
def get_repository() -> SQLiteOrderRepository:
    return SQLiteOrderRepository(get_settings().database_path)

