"""State definitions for the language tutor graph."""

from __future__ import annotations

from typing import Any, Dict, List, TypedDict


class LearningState(TypedDict):
    """Shared state flowing through LangGraph nodes."""

    user_id: str
    level: str
    target_language: str
    native_language: str
    lesson: Dict[str, Any]
    exercises: List[Dict[str, Any]]
    user_answers: List[str]
    evaluation: Dict[str, Any]
    memory: Dict[str, Any]
    loop_count: int
