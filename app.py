"""FastAPI entry point for the Persian text-similarity service."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from chunker import chunk_sentences
from config import Settings
from highlight import highlight_diff
from matcher import ParagraphMatcher
from normalizer import PersianNormalizer
from report import generate_report
from semantic import semantic_diff
from similarity import Similarity

logger = logging.getLogger("batman")

# A JSON-escaped non-ASCII character ("ا") takes 6 bytes, so a body for
# two texts at the character limit can be up to ~12 bytes per allowed char.
_BYTES_PER_CHAR_UPPER_BOUND = 12
_BODY_OVERHEAD_BYTES = 4096


# ── Schemas ──────────────────────────────────────────────────────────────────
class CompareRequest(BaseModel):
    text_a: str
    text_b: str


class MatchResult(BaseModel):
    a_index: int
    b_index: int
    similarity: float
    exact_similarity: Optional[float] = None
    text_a: str
    text_b: str


class CompareResponse(BaseModel):
    matches: List[MatchResult]


class ReportStats(BaseModel):
    matched_count: int
    coverage_a: float
    coverage_b: float
    avg_semantic_similarity: float
    avg_exact_similarity: float


class ReportResponse(BaseModel):
    report: ReportStats
    matches: List[MatchResult]


class SemanticDiff(BaseModel):
    semantic_similarity: float
    only_in_a: List[str]
    only_in_b: List[str]


class Highlight(BaseModel):
    a_html: str
    b_html: str
    completely_different: bool


class DiffResponse(BaseModel):
    semantic_diff: SemanticDiff
    highlight: Highlight


class HealthResponse(BaseModel):
    status: str


ERROR_RESPONSES = {
    400: {"description": "Both texts are required and must contain analyzable text"},
    413: {"description": "Input text exceeds the configured maximum length"},
}


# ── Services ─────────────────────────────────────────────────────────────────
@dataclass
class Services:
    settings: Settings
    normalizer: PersianNormalizer
    matcher: ParagraphMatcher


def load_model(settings: Settings):
    """Load the SentenceTransformer model (downloads it on first use)."""
    import torch
    from sentence_transformers import SentenceTransformer

    device = settings.device or ("cuda" if torch.cuda.is_available() else "cpu")
    logger.info("Loading model %s on %s", settings.model_name, device)
    model = SentenceTransformer(settings.model_name, device=device)
    model.eval()
    return model


def build_services(settings: Settings, model) -> Services:
    return Services(
        settings=settings,
        normalizer=PersianNormalizer(),
        matcher=ParagraphMatcher(
            model,
            similarity=Similarity(),
            max_concurrent_inference=settings.max_concurrent_inference,
        ),
    )


def _services(request: Request) -> Services:
    services = getattr(request.app.state, "services", None)
    if services is None:  # only possible if lifespan did not run
        raise HTTPException(status_code=503, detail="Model is not loaded yet.")
    return services


def _prepare(
    payload: CompareRequest, services: Services
) -> Tuple[str, str, List[str], List[str]]:
    """Validate inputs, then return normalized texts and their sentences."""
    if not payload.text_a.strip() or not payload.text_b.strip():
        raise HTTPException(status_code=400, detail="Both text_a and text_b are required.")
    limit = services.settings.max_text_length
    if len(payload.text_a) > limit or len(payload.text_b) > limit:
        raise HTTPException(
            status_code=413,
            detail=f"Each text must be at most {limit} characters long.",
        )
    norm_a = services.normalizer.normalize(payload.text_a)
    norm_b = services.normalizer.normalize(payload.text_b)
    sentences_a = chunk_sentences(norm_a)
    sentences_b = chunk_sentences(norm_b)
    if not sentences_a or not sentences_b:
        raise HTTPException(
            status_code=400,
            detail="Both text_a and text_b must contain analyzable text.",
        )
    return norm_a, norm_b, sentences_a, sentences_b


# ── Routes ───────────────────────────────────────────────────────────────────
# Endpoints are plain ``def`` (not ``async def``): model inference is CPU-bound
# and blocking, so FastAPI runs them in its worker thread pool, keeping the
# event loop responsive.
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> dict:
    return {"status": "ok"}


def _align(payload: CompareRequest, request: Request):
    """Shared pipeline: validate, normalize, split, embed once, align."""
    services = _services(request)
    settings = services.settings
    norm_a, norm_b, sentences_a, sentences_b = _prepare(payload, services)
    alignment = services.matcher.align(
        sentences_a,
        sentences_b,
        threshold=settings.similarity_threshold,
        lexical_threshold=settings.lexical_match_threshold,
    )
    return settings, norm_a, norm_b, alignment


@router.post("/compare", response_model=CompareResponse, responses=ERROR_RESPONSES)
def compare_texts(payload: CompareRequest, request: Request) -> dict:
    _, _, _, alignment = _align(payload, request)
    return {"matches": alignment.matches()}


@router.post("/report", response_model=ReportResponse, responses=ERROR_RESPONSES)
def plagiarism_report(payload: CompareRequest, request: Request) -> dict:
    _, _, _, alignment = _align(payload, request)
    matches = alignment.matches()
    report = generate_report(
        matches,
        len(alignment.sentences_a),
        len(alignment.sentences_b),
        np.flatnonzero(alignment.b_matched).tolist(),
    )
    return {"report": report, "matches": matches}


@router.post("/diff-highlight", response_model=DiffResponse, responses=ERROR_RESPONSES)
def diff_and_highlight(payload: CompareRequest, request: Request) -> dict:
    settings, norm_a, norm_b, alignment = _align(payload, request)
    sem_diff = semantic_diff(alignment)
    highlight = highlight_diff(
        norm_a,
        norm_b,
        semantic_similarity=sem_diff["semantic_similarity"],
        threshold=settings.diff_semantic_threshold,
        text_overlap_threshold=settings.diff_text_overlap_threshold,
    )
    return {"semantic_diff": sem_diff, "highlight": highlight}


# ── Application factory ──────────────────────────────────────────────────────
def create_app(settings: Optional[Settings] = None, model=None) -> FastAPI:
    """Build the FastAPI app.

    ``model`` may be injected (e.g. a lightweight fake in tests); otherwise the
    real SentenceTransformer is loaded once during application startup.
    """
    settings = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if getattr(app.state, "services", None) is None:
            app.state.services = build_services(settings, load_model(settings))
        yield

    app = FastAPI(title="Persian Text Similarity API", lifespan=lifespan)
    if model is not None:
        app.state.services = build_services(settings, model)

    max_body_bytes = settings.max_text_length * _BYTES_PER_CHAR_UPPER_BOUND + _BODY_OVERHEAD_BYTES

    @app.middleware("http")
    async def limit_body_size(request: Request, call_next):
        # Reject oversized bodies before they are read and parsed into memory.
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                too_large = int(content_length) > max_body_bytes
            except ValueError:
                return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length header."})
            if too_large:
                return JSONResponse(status_code=413, content={"detail": "Request body is too large."})
        return await call_next(request)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    app.include_router(router, prefix="/api")
    # Backwards-compatible aliases for the original unprefixed routes.
    app.include_router(router, include_in_schema=False)
    return app


app = create_app()
