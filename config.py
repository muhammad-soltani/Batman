"""Runtime configuration, read from environment variables.

Every value has a sensible default so the service runs with no configuration.
Invalid values fail fast at startup with a clear error message instead of
surfacing later as confusing runtime behaviour.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable, Optional, Tuple, TypeVar

from highlight import DIFF_SEMANTIC_THRESHOLD, DIFF_TEXT_OVERLAP_THRESHOLD
from matcher import LEXICAL_MATCH_THRESHOLD, SIMILARITY_THRESHOLD

DEFAULT_MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
DEFAULT_MAX_TEXT_LENGTH = 50_000
DEFAULT_MAX_CONCURRENT_INFERENCE = 2
DEFAULT_CORS_ORIGINS: Tuple[str, ...] = (
    "http://localhost:3002",
    "http://127.0.0.1:3002",
)

T = TypeVar("T")


def _env(name: str, parse: Callable[[str], T], default: T) -> T:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return parse(raw.strip())
    except ValueError as exc:
        raise ValueError(f"Invalid value for environment variable {name}={raw!r}: {exc}") from exc


def _unit_interval(raw: str) -> float:
    value = float(raw)
    if not -1.0 <= value <= 1.0:
        raise ValueError("must be between -1 and 1")
    return value


def _positive_int(raw: str) -> int:
    value = int(raw)
    if value <= 0:
        raise ValueError("must be a positive integer")
    return value


def _origins(raw: str) -> Tuple[str, ...]:
    return tuple(o.strip() for o in raw.split(",") if o.strip())


@dataclass(frozen=True)
class Settings:
    model_name: str = DEFAULT_MODEL_NAME
    # None = auto-detect (CUDA when available, otherwise CPU)
    device: Optional[str] = None
    similarity_threshold: float = SIMILARITY_THRESHOLD
    # Lexical score that also counts as a match (near-verbatim copy).
    lexical_match_threshold: float = LEXICAL_MATCH_THRESHOLD
    diff_semantic_threshold: float = DIFF_SEMANTIC_THRESHOLD
    diff_text_overlap_threshold: float = DIFF_TEXT_OVERLAP_THRESHOLD
    # Maximum number of characters accepted for *each* of text_a / text_b.
    max_text_length: int = DEFAULT_MAX_TEXT_LENGTH
    # Upper bound on simultaneous model.encode() calls (protects CPU/RAM).
    max_concurrent_inference: int = DEFAULT_MAX_CONCURRENT_INFERENCE
    cors_origins: Tuple[str, ...] = field(default=DEFAULT_CORS_ORIGINS)

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            model_name=_env("MODEL_NAME", str, DEFAULT_MODEL_NAME),
            device=_env("DEVICE", str, None),
            similarity_threshold=_env("SIMILARITY_THRESHOLD", _unit_interval, SIMILARITY_THRESHOLD),
            lexical_match_threshold=_env(
                "LEXICAL_MATCH_THRESHOLD", _unit_interval, LEXICAL_MATCH_THRESHOLD
            ),
            diff_semantic_threshold=_env("DIFF_SEMANTIC_THRESHOLD", _unit_interval, DIFF_SEMANTIC_THRESHOLD),
            diff_text_overlap_threshold=_env(
                "DIFF_TEXT_OVERLAP_THRESHOLD", _unit_interval, DIFF_TEXT_OVERLAP_THRESHOLD
            ),
            max_text_length=_env("MAX_TEXT_LENGTH", _positive_int, DEFAULT_MAX_TEXT_LENGTH),
            max_concurrent_inference=_env(
                "MAX_CONCURRENT_INFERENCE", _positive_int, DEFAULT_MAX_CONCURRENT_INFERENCE
            ),
            cors_origins=_env("CORS_ORIGINS", _origins, DEFAULT_CORS_ORIGINS),
        )
