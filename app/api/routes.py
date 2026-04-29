"""API routes for learning graph execution."""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

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


class LearnResponse(BaseModel):
    """Response payload returning final graph state."""

    state: Dict[str, Any]


@router.post("/learn", response_model=LearnResponse)
def learn(payload: LearnRequest) -> LearnResponse:
    """Execute one LangGraph learning workflow for a user."""
    store = get_memory_store()
    initial_state: LearningState = {
        "user_id": payload.user_id,
        "level": payload.level,
        "target_language": payload.target_language,
        "native_language": payload.native_language,
        "lesson": {},
        "exercises": [],
        "user_answers": payload.user_answers,
        "evaluation": {},
        "memory": store.get(payload.user_id),
        "loop_count": 0,
    }

    result = learning_graph.invoke(initial_state)
    return LearnResponse(state=result)
