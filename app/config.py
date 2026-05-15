"""Application configuration loaded from the environment."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")

_FALLBACK_CHAT_MODEL = "gpt-5.4-mini-2026-03-17"
_FALLBACK_API_KEY_PLACEHOLDER = "<your-openai-api-key>"
# Default for practice / question generation only (fast, low-latency). Override via OPENAI_PRACTICE_MODEL.
_FALLBACK_PRACTICE_CHAT_MODEL = "gpt-4o-mini"

# Optional: override which env vars hold the key and model (defaults: OPENAI_API_KEY, OPENAI_CHAT_MODEL).
OPENAI_API_KEY_ENV = os.getenv("OPENAI_API_KEY_ENV", "OPENAI_API_KEY")
OPENAI_CHAT_MODEL_ENV = os.getenv("OPENAI_CHAT_MODEL_ENV", "OPENAI_CHAT_MODEL")
OPENAI_PRACTICE_MODEL_ENV = os.getenv(
    "OPENAI_PRACTICE_MODEL_ENV", "OPENAI_PRACTICE_MODEL"
)

# Docs / UI hint; set OPENAI_API_KEY_PLACEHOLDER in .env to customize.
OPENAI_API_KEY_PLACEHOLDER = os.getenv(
    "OPENAI_API_KEY_PLACEHOLDER", _FALLBACK_API_KEY_PLACEHOLDER
)

DEFAULT_CHAT_MODEL = (
    (os.environ.get(OPENAI_CHAT_MODEL_ENV) or "").strip() or _FALLBACK_CHAT_MODEL
)


class LLMConfig(BaseModel):
    """Settings for the LangChain OpenAI chat entrypoint."""

    openai_api_key: str = Field(
        default="",
        description=(
            f"API key for OpenAI. Set {OPENAI_API_KEY_ENV} in the environment "
            f"(placeholder: {OPENAI_API_KEY_PLACEHOLDER})."
        ),
    )
    chat_model: str = Field(
        default=DEFAULT_CHAT_MODEL,
        description=f"OpenAI model id; optional override via {OPENAI_CHAT_MODEL_ENV}.",
    )
    practice_chat_model: str = Field(
        default=_FALLBACK_PRACTICE_CHAT_MODEL,
        description=(
            f"Model for exercise / question generation only; optional override via "
            f"{OPENAI_PRACTICE_MODEL_ENV}."
        ),
    )


def get_llm_config() -> LLMConfig:
    """Build LLM settings from the current process environment."""
    model = (os.environ.get(OPENAI_CHAT_MODEL_ENV) or "").strip() or _FALLBACK_CHAT_MODEL
    practice_model = (
        (os.environ.get(OPENAI_PRACTICE_MODEL_ENV) or "").strip()
        or _FALLBACK_PRACTICE_CHAT_MODEL
    )
    return LLMConfig(
        openai_api_key=os.environ.get(OPENAI_API_KEY_ENV, ""),
        chat_model=model,
        practice_chat_model=practice_model,
    )
