import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from matcher import ParagraphMatcher
from chunker import chunk_sentences
from normalizer import PersianNormalizer
from similarity import Similarity
from semantic import SemanticSimilarity
from highlight import highlight_diff
from report import generate_report

MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer(MODEL_NAME, device=device)
similarity = Similarity()
matcher = ParagraphMatcher(model, similarity=similarity)
normalizer = PersianNormalizer()
semantic = SemanticSimilarity(model=model)

app = FastAPI(title="Persian Text Similarity API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3002"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/compare", response_model=CompareResponse, responses={400: {"description": "Both texts are required"}})
def compare_texts(request: CompareRequest):
    if not request.text_a or not request.text_b:
        raise HTTPException(status_code=400, detail="Both text_a and text_b are required.")
    sentences_a = chunk_sentences(normalizer.normalize(request.text_a))
    sentences_b = chunk_sentences(normalizer.normalize(request.text_b))
    matches = matcher.match(sentences_a, sentences_b, with_exact=True)
    return {"matches": matches}

@app.post("/report")
def plagiarism_report(request: CompareRequest):
    sentences_a = chunk_sentences(normalizer.normalize(request.text_a))
    sentences_b = chunk_sentences(normalizer.normalize(request.text_b))
    matches = matcher.match(sentences_a, sentences_b, with_exact=True)
    report = generate_report(matches, len(sentences_a), len(sentences_b))
    return {"report": report, "matches": matches}

@app.post("/diff-highlight")
def diff_and_highlight(request: CompareRequest):
    norm_a = normalizer.normalize(request.text_a)
    norm_b = normalizer.normalize(request.text_b)
    sem_diff = semantic.diff(norm_a, norm_b)
    sem_score = sem_diff["semantic_similarity"]
    return {
        "semantic_diff": sem_diff,
        "highlight": highlight_diff(norm_a, norm_b, semantic_similarity=sem_score),
    }