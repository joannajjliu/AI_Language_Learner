"""Shared learner memory shape used by graph agents and stores."""

from __future__ import annotations

from typing import Any, Dict

DEFAULT_MEMORY: Dict[str, Any] = {
    "known_vocab": [],
    "mistakes": [],
    "completed_topics": [],
}
