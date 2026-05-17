"""Memory store access helpers."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Union

from app.config import get_database_url
from app.memory.store import InMemoryLearningStore

if TYPE_CHECKING:
    from app.memory.postgres_store import PostgresLearningStore

LearningMemoryStore = Union[InMemoryLearningStore, "PostgresLearningStore"]

_pg_store: PostgresLearningStore | None = None


@lru_cache(maxsize=1)
def _in_memory_singleton() -> InMemoryLearningStore:
    return InMemoryLearningStore()


def get_memory_store() -> LearningMemoryStore:
    """Learner progress store; uses Postgres when DATABASE_URL is set, else in-memory."""
    global _pg_store
    url = get_database_url()
    if url:
        if _pg_store is None:
            from app.memory.postgres_store import PostgresLearningStore

            _pg_store = PostgresLearningStore(url)
        return _pg_store
    return _in_memory_singleton()


def shutdown_memory_store() -> None:
    """Release DB pool on app shutdown."""
    global _pg_store
    if _pg_store is not None:
        _pg_store.close()
        _pg_store = None
