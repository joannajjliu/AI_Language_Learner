"""Memory update agent."""

from __future__ import annotations

from app.graph.state import LearningState
from app.memory import get_memory_store


def memory_agent(state: LearningState) -> LearningState:
    """Update learner memory from evaluation and lesson outcome."""
    store = get_memory_store()
    current_memory = store.apply_session(state)
    state["memory"] = current_memory
    state["loop_count"] = state.get("loop_count", 0) + 1
    return state
