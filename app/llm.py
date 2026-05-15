"""Single LangChain entrypoint for chat models."""

from __future__ import annotations

from functools import lru_cache

from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel

from app.config import LLMConfig, get_llm_config


def _build_chat_model(cfg: LLMConfig) -> BaseChatModel:
    api_key = cfg.openai_api_key.strip() or None
    return init_chat_model(
        cfg.chat_model,
        model_provider="openai",
        api_key=api_key,
    )


@lru_cache(maxsize=1)
def _default_chat_model() -> BaseChatModel:
    return _build_chat_model(get_llm_config())


@lru_cache(maxsize=1)
def _practice_chat_model() -> BaseChatModel:
    cfg = get_llm_config()
    return _build_chat_model(
        LLMConfig(
            openai_api_key=cfg.openai_api_key,
            chat_model=cfg.practice_chat_model,
        ),
    )


def get_chat_model(*, config: LLMConfig | None = None) -> BaseChatModel:
    """Return the configured OpenAI chat model via LangChain's unified initializer.

    If ``openai_api_key`` is empty in config, the OpenAI client may still resolve
    the key from the ``OPENAI_API_KEY`` environment variable.

    The default model is cached for a process so LangGraph nodes reuse one client.
    Pass ``config`` to bypass the cache (e.g. tests).
    """
    if config is not None:
        return _build_chat_model(config)
    return _default_chat_model()


def get_practice_chat_model(*, config: LLMConfig | None = None) -> BaseChatModel:
    """Chat model used only for practice-question generation (typically smaller / faster)."""
    if config is not None:
        return _build_chat_model(
            LLMConfig(
                openai_api_key=config.openai_api_key,
                chat_model=config.practice_chat_model,
            ),
        )
    return _practice_chat_model()
