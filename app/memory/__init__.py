"""Memory store access helpers."""

from __future__ import annotations

from functools import lru_cache

from app.memory.store import InMemoryLearningStore


@lru_cache(maxsize=1)
def get_memory_store() -> InMemoryLearningStore:
    """Return a singleton-like store instance for app lifetime."""
    return InMemoryLearningStore()
