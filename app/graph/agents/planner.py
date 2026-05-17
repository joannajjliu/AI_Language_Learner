"""Planner agent for deciding lesson focus."""

from __future__ import annotations

import json

from app.graph.agents.utils import load_prompt
from app.graph.llm_helpers import PlannerOutput, invoke_structured
from app.graph.state import LearningState
from app.llm import get_chat_model


def planner_agent(state: LearningState) -> LearningState:
    """Create a lesson plan from learner level and memory using the chat model."""
    system = load_prompt("planner_prompt.txt")
    memory = state.get("memory", {})

    human = f"""Learner profile:
- CEFR level: {state["level"]}
- Target language: {state["target_language"]}
- Native language: {state["native_language"]}
- Completed topics: {json.dumps(memory.get("completed_topics", []), ensure_ascii=True)}
- Known vocabulary: {json.dumps(memory.get("known_vocab", [])[-20:], ensure_ascii=True)}
- Recent mistakes: {json.dumps(memory.get("mistakes", [])[-5:], ensure_ascii=True)}
"""

    llm = get_chat_model()
    out = invoke_structured(llm, system=system, human=human, schema=PlannerOutput)

    state["lesson"] = {
        "topic": out.topic,
        "objective": out.objective,
        "difficulty": out.difficulty,
        "prompt_template": system,
    }
    return state
