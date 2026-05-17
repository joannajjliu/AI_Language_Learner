"""Simple in-memory store for learner memory snapshots."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from app.graph.state import LearningState
from app.memory.constants import DEFAULT_MEMORY
from app.memory.updates import merge_session_into_memory


class InMemoryLearningStore:
    """Store learner progress in process memory."""

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, Any]] = {}

    def ensure_user(
        self,
        user_id: str,
        *,
        email: str,
        display_name: str,
        native_language: str,
        target_language: str,
        cefr_level: str,
    ) -> None:
        """No-op for the in-process store (profile lives on each request)."""
        del (
            user_id,
            email,
            display_name,
            native_language,
            target_language,
            cefr_level,
        )

    def get(self, user_id: str) -> Dict[str, Any]:
        """Return memory for a user or initialize a default profile."""
        if user_id not in self._store:
            self._store[user_id] = deepcopy(DEFAULT_MEMORY)
        return deepcopy(self._store[user_id])

    def set(
        self,
        user_id: str,
        memory: Dict[str, Any],
        *,
        state: LearningState | None = None,
    ) -> None:
        """Persist the full memory object for a user."""
        del state
        self._store[user_id] = deepcopy(memory)

    def apply_session(self, state: LearningState) -> Dict[str, Any]:
        """Merge graph outcomes into storage and return the updated snapshot."""
        user_id = state["user_id"]
        updated = merge_session_into_memory(self.get(user_id), state)
        self.set(user_id, updated)
        return updated
