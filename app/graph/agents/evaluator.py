"""Evaluator agent for user practice answers."""

from __future__ import annotations

from app.graph.agents.utils import load_prompt
from app.graph.llm_helpers import EvaluationOutput, invoke_structured, normalize_score
from app.graph.state import LearningState
from app.guardrails.input import build_evaluator_human
from app.llm import get_chat_model


def evaluator_agent(state: LearningState) -> LearningState:
    """Evaluate learner answers with the chat model."""
    system = load_prompt("evaluator_prompt.txt")
    exercises = state.get("exercises", [])
    answers = state.get("user_answers", [])

    human = build_evaluator_human(
        level=state["level"],
        target_language=state["target_language"],
        native_language=state["native_language"],
        exercises=exercises,
        answers=answers,
    )

    llm = get_chat_model()
    out = invoke_structured(llm, system=system, human=human, schema=EvaluationOutput)
    score = normalize_score(out.score)

    state["evaluation"] = {
        "score": score,
        "feedback": out.feedback,
        "needs_review": out.needs_review,
    }
    return state
