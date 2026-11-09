import threading
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Minimum cosine similarity for two sentences to count as the same content.
# Calibrated on Persian pairs with paraphrase-multilingual-mpnet-base-v2:
# paraphrases / partial copies score 0.75–0.99, while sentences that merely
# share a topic score 0.26–0.59 (they were false matches at the old 0.5).
SIMILARITY_THRESHOLD = 0.7

# Near-verbatim copies also count as matches even when one changed word flips
# the meaning (e.g. "افزایش یافت" → "کاهش یافت", cosine ≈ 0.53).
LEXICAL_MATCH_THRESHOLD = 0.8


@dataclass
class Alignment:
    """Sentence alignment between two texts.

    ``best_b[i]`` is the B sentence most semantically similar to A sentence
    ``i`` (and ``best_a[j]`` vice versa). A sentence is *matched* when that
    counterpart is semantically similar (cosine > threshold) or a
    near-verbatim lexical copy (lexical >= lexical_threshold).
    """

    sentences_a: List[str]
    sentences_b: List[str]
    sim_matrix: np.ndarray
    best_b: np.ndarray
    best_a: np.ndarray
    lexical_a: List[Optional[float]]
    a_matched: np.ndarray
    b_matched: np.ndarray

    def matches(self) -> List[Dict[str, Any]]:
        """Matched A sentences with their counterpart, highest similarity first."""
        matches: List[Dict[str, Any]] = []
        for i in np.flatnonzero(self.a_matched):
            i = int(i)
            j = int(self.best_b[i])
            entry: Dict[str, Any] = {
                "a_index": i,
                "b_index": j,
                "similarity": round(float(self.sim_matrix[i, j]), 4),
                "text_a": self.sentences_a[i],
                "text_b": self.sentences_b[j],
            }
            if self.lexical_a[i] is not None:
                entry["exact_similarity"] = round(self.lexical_a[i], 4)
            matches.append(entry)
        # Stable sort: ties keep document order.
        matches.sort(key=lambda m: m["similarity"], reverse=True)
        return matches


class ParagraphMatcher:
    """Sentence-level semantic matcher built on a SentenceTransformer model.

    ``model`` only needs an ``encode(texts, convert_to_numpy=True, ...)`` method,
    which keeps the class easy to test with a lightweight fake model.
    ``similarity`` (lexical scorer with an ``exact(a, b)`` method) is optional;
    without it no lexical scores are reported and only the semantic rule applies.
    """

    def __init__(self, model, similarity=None, max_concurrent_inference: Optional[int] = None):
        self.model = model
        self.similarity = similarity
        # Bounds the number of simultaneous encode() calls. Requests run in
        # FastAPI's thread pool; without a bound, a burst of large requests
        # makes every request slow and multiplies peak memory usage.
        self._inference_slots = (
            threading.BoundedSemaphore(max_concurrent_inference)
            if max_concurrent_inference
            else None
        )

    def _encode(self, texts: List[str]) -> np.ndarray:
        if self._inference_slots is None:
            return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        with self._inference_slots:
            return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

    def similarity_matrix(self, sentences_a: List[str], sentences_b: List[str]) -> np.ndarray:
        """Return the ``len(a) x len(b)`` cosine-similarity matrix.

        Both sides are encoded in a single batched call. Values are clipped to
        [-1, 1] to remove floating-point noise (e.g. 1.0000001 for identical
        sentences).
        """
        if not sentences_a or not sentences_b:
            return np.zeros((len(sentences_a), len(sentences_b)), dtype=np.float32)
        all_embs = self._encode(sentences_a + sentences_b)
        emb_a = all_embs[: len(sentences_a)]
        emb_b = all_embs[len(sentences_a):]
        return np.clip(cosine_similarity(emb_a, emb_b), -1.0, 1.0)

    def _lexical(self, a: str, b: str) -> Optional[float]:
        return None if self.similarity is None else float(self.similarity.exact(a, b))

    def align(
        self,
        sentences_a: List[str],
        sentences_b: List[str],
        *,
        threshold: float = SIMILARITY_THRESHOLD,
        lexical_threshold: Optional[float] = LEXICAL_MATCH_THRESHOLD,
        sim_matrix: Optional[np.ndarray] = None,
    ) -> Alignment:
        """Align both texts and decide which sentences have a counterpart.

        Pass ``lexical_threshold=None`` to use the semantic rule only.
        """
        if sim_matrix is None:
            sim_matrix = self.similarity_matrix(sentences_a, sentences_b)
        n_a, n_b = len(sentences_a), len(sentences_b)
        if n_a == 0 or n_b == 0:
            # Nothing can match; best_* are placeholders that are never read.
            return Alignment(
                sentences_a, sentences_b, sim_matrix,
                best_b=np.zeros(n_a, dtype=int), best_a=np.zeros(n_b, dtype=int),
                lexical_a=[None] * n_a,
                a_matched=np.zeros(n_a, dtype=bool), b_matched=np.zeros(n_b, dtype=bool),
            )

        best_b = np.argmax(sim_matrix, axis=1)
        best_a = np.argmax(sim_matrix, axis=0)
        a_semantic = sim_matrix[np.arange(n_a), best_b] > threshold
        b_semantic = sim_matrix[best_a, np.arange(n_b)] > threshold

        lexical_a = [self._lexical(sentences_a[i], sentences_b[best_b[i]]) for i in range(n_a)]
        use_lexical = lexical_threshold is not None and self.similarity is not None

        def lexical_hit(score: Optional[float]) -> bool:
            return use_lexical and score is not None and score >= lexical_threshold

        a_matched = np.array([a_semantic[i] or lexical_hit(lexical_a[i]) for i in range(n_a)], dtype=bool)
        if use_lexical:
            b_matched = np.array(
                [
                    b_semantic[j]
                    or lexical_hit(self._lexical(sentences_a[best_a[j]], sentences_b[j]))
                    for j in range(n_b)
                ],
                dtype=bool,
            )
        else:
            b_matched = b_semantic.astype(bool)
        return Alignment(
            sentences_a, sentences_b, sim_matrix, best_b, best_a, lexical_a, a_matched, b_matched
        )

    def match(
        self,
        sentences_a: List[str],
        sentences_b: List[str],
        *,
        with_exact: bool = False,
        threshold: float = SIMILARITY_THRESHOLD,
        lexical_threshold: Optional[float] = LEXICAL_MATCH_THRESHOLD,
    ) -> List[Dict[str, Any]]:
        """
        Find the best-matching sentence in B for every sentence in A.

        Args:
            sentences_a: Sentences from the first document.
            sentences_b: Sentences from the second document.
            with_exact: Include the lexical ``exact_similarity`` in each match.
            threshold: Semantic similarity a match must exceed. Pass a value
                       below -1 (and ``lexical_threshold=None``) to keep every pair.
            lexical_threshold: Lexical score that also qualifies as a match
                       (near-verbatim copy); ``None`` disables the rule.

        Returns:
            A list of match dicts sorted by descending semantic similarity.
        """
        if not sentences_a or not sentences_b:
            return []
        matches = self.align(
            sentences_a, sentences_b, threshold=threshold, lexical_threshold=lexical_threshold
        ).matches()
        if not with_exact:
            for m in matches:
                m.pop("exact_similarity", None)
        return matches

    def multi_document_match(self, documents: List[List[str]]) -> List[Dict[str, Any]]:
        """Compare every document pair and return per-pair match lists (all pairs kept)."""
        results = []
        n = len(documents)
        for i in range(n):
            for j in range(i + 1, n):
                matches = self.match(documents[i], documents[j], threshold=-2.0, lexical_threshold=None)
                results.append({"doc_a": i, "doc_b": j, "matches": matches})
        return results
