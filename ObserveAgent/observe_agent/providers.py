"""Provider factories keep model and secret selection outside business logic."""

from __future__ import annotations

from .config import Settings
from .knowledge import EmbeddingProvider, HashEmbedding, OpenAIEmbedding
from .reasoner import OpenAIReasoner, Reasoner, RuleBasedReasoner


def build_embedder(settings: Settings) -> EmbeddingProvider:
    if settings.embedding_provider == "hash":
        return HashEmbedding(settings.embedding_dimensions)
    return OpenAIEmbedding(
        settings.embedding_model,
        settings.embedding_api_key or "",
        base_url=settings.embedding_base_url,
        dimensions=settings.embedding_dimensions,
    )


def build_reasoner(settings: Settings) -> Reasoner:
    if settings.llm_provider == "rule":
        return RuleBasedReasoner()
    return OpenAIReasoner(
        settings.llm_model,
        settings.llm_api_key or "",
        base_url=settings.llm_base_url,
        max_output_tokens=settings.llm_max_output_tokens,
        temperature=settings.llm_temperature,
    )
