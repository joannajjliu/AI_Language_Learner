"""Memory update agent."""

from __future__ import annotations

from app.graph.state import LearningState
from app.memory import get_memory_store


def memory_agent(state: LearningState) -> LearningState:
    """Update learner memory from evaluation and lesson outcome."""
    store = get_memory_store()
    user_id = state["user_id"]
    current_memory = store.get(user_id)

    topic = state.get("lesson", {}).get("topic")
    if topic and topic not in current_memory["completed_topics"]:
        current_memory["completed_topics"].append(topic)

    if state.get("evaluation", {}).get("needs_review", False):
        current_memory["mistakes"].append(
            {
                "topic": topic,
                "reason": state["evaluation"].get("feedback", "Needs more practice."),
            }
        )
    else:
        current_memory["known_vocab"].append("hello")

    store.set(user_id, current_memory)
    state["memory"] = current_memory
    state["loop_count"] = state.get("loop_count", 0) + 1
    return state
