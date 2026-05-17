"""Remove server-internal fields from graph state before API responses."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

_INTERNAL_KEYS = frozenset({"prompt_template", "practice_prompt_template"})


def strip_internal_fields(state: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of graph state without system prompt templates."""
    out = deepcopy(state)
    _strip_recursive(out)
    return out


def _strip_recursive(obj: Any) -> None:
    if isinstance(obj, dict):
        for key in list(obj.keys()):
            if key in _INTERNAL_KEYS:
                del obj[key]
            else:
                _strip_recursive(obj[key])
    elif isinstance(obj, list):
        for item in obj:
            _strip_recursive(item)
