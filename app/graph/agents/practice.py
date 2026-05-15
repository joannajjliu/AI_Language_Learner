"""Practice generation agent."""

from __future__ import annotations

import json

from app.graph.agents.utils import load_prompt
from app.graph.llm_helpers import PracticeOutput, invoke_structured
from app.graph.state import LearningState
from app.llm import get_practice_chat_model


def practice_agent(state: LearningState) -> LearningState:
    """Generate practice tasks from the lesson using the chat model."""
    system = load_prompt("practice_prompt.txt")
    lesson = state.get("lesson", {})
    topic = lesson.get("topic", "general")

    human = f"""Lesson context:
- Topic: {topic}
- Objective: {lesson.get("objective", "")}
- Content: {lesson.get("content", "")}
- Examples: {json.dumps(lesson.get("examples", []), ensure_ascii=True)}
- CEFR level: {state["level"]}
- Target language: {state["target_language"]}
- Native language: {state["native_language"]}

Produce 2–4 varied exercises (e.g. translation, fill_blank, short_answer). Each needs a unique id."""

    llm = get_practice_chat_model()
    out = invoke_structured(llm, system=system, human=human, schema=PracticeOutput)

    exercises: list[dict] = [{**ex.model_dump(), "topic": topic} for ex in out.exercises]
    if not exercises:
        exercises = [
            {
                "id": "ex-fallback-1",
                "type": "translation",
                "question": f"Translate to {state['target_language']}: 'Good morning'",
                "topic": topic,
            }
        ]

    state["exercises"] = exercises
    state["lesson"]["practice_prompt_template"] = system
    return state
