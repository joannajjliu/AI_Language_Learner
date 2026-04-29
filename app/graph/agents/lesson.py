"""Lesson generation agent."""

from __future__ import annotations

from app.graph.agents.utils import load_prompt
from app.graph.state import LearningState


def lesson_agent(state: LearningState) -> LearningState:
    """Generate a mock lesson from the planner output."""
    prompt_template = load_prompt("lesson_prompt.txt")
    topic = state["lesson"].get("topic", "introduction")

    state["lesson"] = {
        **state["lesson"],
        "content": (
            f"Lesson topic: {topic}. "
            f"Key phrase in {state['target_language']}: 'Hello, how are you?'"
        ),
        "examples": [
            {
                "target": "Hello, how are you?",
                "native": "Hello, how are you?",
            }
        ],
        "prompt_template": prompt_template,
    }
    return state
