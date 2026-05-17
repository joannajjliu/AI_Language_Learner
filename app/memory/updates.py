"""Pure helpers to merge a graph session into the in-memory snapshot dict."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

from app.graph.state import LearningState
from app.memory.constants import DEFAULT_MEMORY


def _dedupe_strings(items: List[str]) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for item in items:
        key = item.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def extract_vocab_from_lesson(lesson: Dict[str, Any]) -> List[Dict[str, str]]:
    """Pull target lemmas (and optional translations) from lesson examples."""
    entries: List[Dict[str, str]] = []
    for ex in lesson.get("examples", []):
        if isinstance(ex, dict):
            lemma = (ex.get("target") or "").strip()
            if not lemma:
                continue
            entries.append(
                {
                    "lemma": lemma,
                    "translation": (ex.get("native") or "").strip() or lemma,
                }
            )
        elif isinstance(ex, str):
            lemma = ex.strip()
            if lemma:
                entries.append({"lemma": lemma, "translation": lemma})
    return entries


def merge_session_into_memory(
    memory: Dict[str, Any],
    state: LearningState,
) -> Dict[str, Any]:
    """Apply lesson and evaluation outcomes to a learner memory snapshot."""
    current = deepcopy(memory) if memory else deepcopy(DEFAULT_MEMORY)
    for key in DEFAULT_MEMORY:
        current.setdefault(key, deepcopy(DEFAULT_MEMORY[key]))

    lesson = state.get("lesson", {})
    topic = lesson.get("topic")
    if topic and topic not in current["completed_topics"]:
        current["completed_topics"].append(topic)

    evaluation = state.get("evaluation", {})
    if evaluation.get("needs_review", False):
        current["mistakes"].append(
            {
                "topic": topic,
                "reason": evaluation.get("feedback", "Needs more practice."),
            }
        )
    else:
        for entry in extract_vocab_from_lesson(lesson):
            lemma = entry["lemma"]
            if lemma not in current["known_vocab"]:
                current["known_vocab"].append(lemma)

    current["known_vocab"] = _dedupe_strings(current["known_vocab"])
    return current
