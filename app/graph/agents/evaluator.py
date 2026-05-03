"""Evaluator agent for user practice answers."""

from __future__ import annotations

from app.graph.agents.utils import load_prompt
from app.graph.llm_helpers import EvaluationOutput, invoke_structured, normalize_score
from app.graph.state import LearningState
from app.llm import get_chat_model


def evaluator_agent(state: LearningState) -> LearningState:
    """Evaluate learner answers with the chat model."""
    system = load_prompt("evaluator_prompt.txt")
    exercises = state.get("exercises", [])
    answers = state.get("user_answers", [])

    qa_blocks: list[str] = []
    for i, ex in enumerate(exercises):
        q = ex.get("question", "")
        t = ex.get("type", "question")
        a = answers[i] if i < len(answers) else "(no answer)"
        qa_blocks.append(f"Exercise {i + 1} ({t}):\nQuestion: {q}\nLearner answer: {a}")

    qa_text = "\n\n".join(qa_blocks) if qa_blocks else "(no exercises submitted)"

    human = f"""{qa_text}

Context:
- CEFR level: {state["level"]}
- Target language: {state["target_language"]}
- Native language: {state["native_language"]}
"""

    llm = get_chat_model()
    out = invoke_structured(llm, system=system, human=human, schema=EvaluationOutput)
    score = normalize_score(out.score)

    state["evaluation"] = {
        "score": score,
        "feedback": out.feedback,
        "needs_review": out.needs_review,
        "prompt_template": system,
    }
    return state
