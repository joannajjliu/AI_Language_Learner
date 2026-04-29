"""Evaluator agent for user practice answers."""

from __future__ import annotations

from app.graph.agents.utils import load_prompt
from app.graph.state import LearningState


def evaluator_agent(state: LearningState) -> LearningState:
    """Evaluate answers with lightweight placeholder scoring."""
    prompt_template = load_prompt("evaluator_prompt.txt")
    exercises_count = len(state.get("exercises", []))
    answers_count = len(state.get("user_answers", []))
    score = 0.0 if exercises_count == 0 else min(answers_count / exercises_count, 1.0)

    feedback = (
        "Great attempt. Keep practicing sentence structure."
        if score >= 0.5
        else "Try again with focus on key vocabulary."
    )
    state["evaluation"] = {
        "score": round(score, 2),
        "feedback": feedback,
        "needs_review": score < 0.7,
        "prompt_template": prompt_template,
    }
    return state
