"""Shared helpers for graph agents."""

from __future__ import annotations

from pathlib import Path


def load_prompt(filename: str) -> str:
    """Load a prompt template by filename from the prompts directory."""
    prompts_dir = Path(__file__).resolve().parent.parent / "prompts"
    return (prompts_dir / filename).read_text(encoding="utf-8")
