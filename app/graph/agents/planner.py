"""Planner agent for deciding lesson focus."""

from __future__ import annotations

from app.graph.agents.utils import load_prompt
from app.graph.state import LearningState


def planner_agent(state: LearningState) -> LearningState:
    """Create a simple plan based on learner level and memory."""
    prompt_template = load_prompt("planner_prompt.txt")
    memory = state.get("memory", {})
    completed_topics = memory.get("completed_topics", [])

    next_topic = "greetings" if not completed_topics else "daily_routine"
    state["lesson"] = {
        "topic": next_topic,
        "objective": f"Practice {next_topic} in {state['target_language']}.",
        "difficulty": state["level"],
        "prompt_template": prompt_template,
    }
    return state
