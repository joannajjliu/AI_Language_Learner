"""Simple in-memory store for learner memory snapshots."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


class InMemoryLearningStore:
    """Store learner progress in process memory."""

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, Any]] = {}

    def get(self, user_id: str) -> Dict[str, Any]:
        """Return memory for a user or initialize a default profile."""
        if user_id not in self._store:
            self._store[user_id] = {
                "known_vocab": [],
                "mistakes": [],
                "completed_topics": [],
            }
        return deepcopy(self._store[user_id])

    def set(self, user_id: str, memory: Dict[str, Any]) -> None:
        """Persist the full memory object for a user."""
        self._store[user_id] = deepcopy(memory)
