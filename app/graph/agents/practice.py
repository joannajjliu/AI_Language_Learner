"""Practice generation agent."""

from __future__ import annotations

from app.graph.agents.utils import load_prompt
from app.graph.state import LearningState


def practice_agent(state: LearningState) -> LearningState:
    """Generate simple practice tasks tied to the lesson."""
    prompt_template = load_prompt("practice_prompt.txt")
    topic = state["lesson"].get("topic", "general")

    state["exercises"] = [
        {
            "id": "ex-1",
            "type": "translation",
            "question": f"Translate to {state['target_language']}: 'Good morning'",
            "topic": topic,
        },
        {
            "id": "ex-2",
            "type": "fill_blank",
            "question": "Complete: Hello, ____ are you?",
            "topic": topic,
        },
    ]
    state["lesson"]["practice_prompt_template"] = prompt_template
    return state
