"""Structured LLM calls shared by graph agents."""

from __future__ import annotations

from typing import TypeVar, cast

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

T = TypeVar("T", bound=BaseModel)


class PlannerOutput(BaseModel):
    topic: str
    objective: str
    difficulty: str


class LessonExample(BaseModel):
    target: str
    native: str


class LessonOutput(BaseModel):
    title: str
    content: str
    examples: list[LessonExample] = Field(default_factory=list)


class ExerciseSpec(BaseModel):
    id: str
    type: str
    question: str


class PracticeOutput(BaseModel):
    exercises: list[ExerciseSpec] = Field(default_factory=list)


class EvaluationOutput(BaseModel):
    score: float = Field(description="Overall score from 0.0 to 1.0 (use decimals, not 0-100).")
    feedback: str
    needs_review: bool


def invoke_structured(
    llm: BaseChatModel,
    *,
    system: str,
    human: str,
    schema: type[T],
) -> T:
    structured = llm.with_structured_output(schema)
    result = structured.invoke(
        [SystemMessage(content=system), HumanMessage(content=human)]
    )
    return cast(T, result)


def normalize_score(raw: float) -> float:
    """Map model output to [0, 1] if it used a 0-100 scale."""
    score = float(raw)
    if score > 1.0:
        score = score / 100.0
    return max(0.0, min(1.0, round(score, 2)))
