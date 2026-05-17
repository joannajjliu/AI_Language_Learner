"""PostgreSQL-backed learner memory across normalized tables."""

from __future__ import annotations

from typing import Any, Dict

from app.db import ensure_schema
from app.graph.state import LearningState
from app.memory.repository import PostgresMemoryRepository
from app.memory.updates import merge_session_into_memory


class PostgresLearningStore:
    """Persist learner profile, vocab SRS state, reviews, and topic/mistake snapshots."""

    def __init__(self, conninfo: str) -> None:
        self._conninfo = conninfo
        ensure_schema(conninfo)
        self._repo = PostgresMemoryRepository(conninfo)

    def close(self) -> None:
        """Reserved for future pooling; no persistent connections are held."""
        pass

    def ensure_user(
        self,
        user_id: str,
        *,
        native_language: str,
        target_language: str,
        cefr_level: str,
    ) -> None:
        self._repo.ensure_user(
            user_id,
            native_language=native_language,
            target_language=target_language,
            cefr_level=cefr_level,
        )

    def get(self, user_id: str) -> Dict[str, Any]:
        return self._repo.load_memory(user_id)

    def set(
        self,
        user_id: str,
        memory: Dict[str, Any],
        *,
        state: LearningState | None = None,
    ) -> None:
        target_language = (state or {}).get("target_language", "")
        lesson = (state or {}).get("lesson")
        evaluation = (state or {}).get("evaluation")
        self._repo.save_memory(
            user_id,
            memory,
            target_language=target_language,
            lesson=lesson,
            evaluation=evaluation,
        )

    def apply_session(self, state: LearningState) -> Dict[str, Any]:
        """Merge graph outcomes into storage and return the updated snapshot."""
        user_id = state["user_id"]
        self.ensure_user(
            user_id,
            native_language=state["native_language"],
            target_language=state["target_language"],
            cefr_level=state["level"],
        )
        current = self.get(user_id)
        updated = merge_session_into_memory(current, state)
        self.set(user_id, updated, state=state)
        return updated
