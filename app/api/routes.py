"""API routes for learning graph execution."""

from __future__ import annotations

from typing import Any, Dict, List, Literal

from fastapi import APIRouter, Header
from pydantic import BaseModel, Field, model_validator

from app.auth.deps import require_matching_user
from app.graph.builder import learning_graph
from app.graph.state import LearningState
from app.memory import get_memory_store

router = APIRouter()


class LearnRequest(BaseModel):
    """Incoming request payload for the learning loop."""

    user_id: str
    level: str = Field(..., description="CEFR level such as A1, A2, B1.")
    target_language: str
    native_language: str
    user_answers: List[str] = Field(default_factory=list)
    action: Literal["full", "submit_answers", "new_exercises"] = "full"
    lesson: Dict[str, Any] = Field(default_factory=dict)
    exercises: List[Dict[str, Any]] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_action_payload(self) -> "LearnRequest":
        if self.action == "submit_answers":
            if not self.lesson:
                raise ValueError("submit_answers requires a lesson snapshot from the client")
            if not self.exercises:
                raise ValueError("submit_answers requires a non-empty exercises list")
            if len(self.user_answers) != len(self.exercises):
                raise ValueError(
                    "submit_answers requires user_answers length to match exercises",
                )
        if self.action == "new_exercises" and not self.lesson:
            raise ValueError("new_exercises requires a lesson snapshot from the client")
        return self


class LearnResponse(BaseModel):
    """Response payload returning final graph state."""

    state: Dict[str, Any]


@router.post("/learn", response_model=LearnResponse)
def learn(
    payload: LearnRequest,
    authorization: str | None = Header(default=None),
) -> LearnResponse:
    """Execute one LangGraph learning workflow for a user."""
    google_user = require_matching_user(payload.user_id, authorization)
    user_id = google_user.user_id
    store = get_memory_store()
    store.ensure_user(
        user_id,
        email=google_user.email,
        display_name=google_user.display_name,
        native_language=payload.native_language,
        target_language=payload.target_language,
        cefr_level=payload.level,
    )
    if payload.action == "full":
        lesson_snapshot: Dict[str, Any] = {}
        exercises_snapshot: List[Dict[str, Any]] = []
    elif payload.action == "new_exercises":
        lesson_snapshot = dict(payload.lesson)
        exercises_snapshot = []
    else:
        lesson_snapshot = dict(payload.lesson)
        exercises_snapshot = list(payload.exercises)

    initial_state: LearningState = {
        "user_id": user_id,
        "level": payload.level,
        "target_language": payload.target_language,
        "native_language": payload.native_language,
        "lesson": lesson_snapshot,
        "exercises": exercises_snapshot,
        "user_answers": payload.user_answers,
        "evaluation": {},
        "memory": store.get(user_id),
        "loop_count": 0,
        "request_action": payload.action,
    }

    result = dict(learning_graph.invoke(initial_state))
    result.pop("request_action", None)
    return LearnResponse(state=result)
