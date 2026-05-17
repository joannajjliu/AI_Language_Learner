"""Lesson generation agent."""

from __future__ import annotations

from app.graph.agents.utils import load_prompt
from app.graph.llm_helpers import LessonOutput, invoke_structured
from app.graph.state import LearningState
from app.llm import get_chat_model


def lesson_agent(state: LearningState) -> LearningState:
    """Generate lesson content from the planner output using the chat model."""
    system = load_prompt("lesson_prompt.txt")
    plan = state.get("lesson", {})

    human = f"""Lesson plan:
- Topic: {plan.get("topic", "general")}
- Objective: {plan.get("objective", "")}
- Difficulty (CEFR): {plan.get("difficulty", state["level"])}
- Target language: {state["target_language"]}
- Native language: {state["native_language"]}
- Learner CEFR level: {state["level"]}

Ground the lesson in the topic and objective above. Include at least two examples."""

    llm = get_chat_model()
    out = invoke_structured(llm, system=system, human=human, schema=LessonOutput)

    state["lesson"] = {
        **plan,
        "title": out.title,
        "content": out.content,
        "examples": [ex.model_dump() for ex in out.examples],
    }
    return state
