from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

SIMILARITY_THRESHOLD = 0.5

class ParagraphMatcher:
    def __init__(self, model: SentenceTransformer, similarity=None):
        self.model = model
        self.similarity = similarity

    def match(
        self,
        sentences_a: List[str],
        sentences_b: List[str],
        *,
        with_exact: bool = False,
        threshold: float = SIMILARITY_THRESHOLD,
    ) -> List[Dict[str, Any]]:
        """
        Find the best-matching sentence in B for every sentence in A.

        Args:
            sentences_a: Sentences from the first document.
            sentences_b: Sentences from the second document.
            with_exact: Also compute RapidFuzz exact similarity when True.
            threshold: Only keep matches whose semantic similarity exceeds
                       this value. Pass 0.0 (or a negative number) to keep
                       every pair (equivalent to the old ``align`` behaviour).

        Returns:
            A list of match dicts sorted by descending semantic similarity.
        """
        if not sentences_a or not sentences_b:
            return []

        # Encode both sides in a single batched call where possible
        all_texts = sentences_a + sentences_b
        all_embs = self.model.encode(
            all_texts, convert_to_numpy=True, show_progress_bar=False
        )
        emb_a = all_embs[: len(sentences_a)]
        emb_b = all_embs[len(sentences_a) :]

        sim_matrix = cosine_similarity(emb_a, emb_b)

        matches: List[Dict[str, Any]] = []
        for i, row in enumerate(sim_matrix):
            best_j = int(np.argmax(row))
            best_score = float(row[best_j])
            if best_score <= threshold:
                continue
            entry: Dict[str, Any] = {
                "a_index": i,
                "b_index": best_j,
                "similarity": round(best_score, 4),
                "text_a": sentences_a[i],
                "text_b": sentences_b[best_j],
            }
            if with_exact and self.similarity is not None:
                entry["exact_similarity"] = round(
                    self.similarity.exact(sentences_a[i], sentences_b[best_j]), 4
                )
            matches.append(entry)

        # Return highest-similarity matches first
        matches.sort(key=lambda m: m["similarity"], reverse=True)
        return matches

    def multi_document_match(self, documents: List[List[str]]) -> List[Dict[str, Any]]:
        """Compare every document pair and return per-pair match lists."""
        results = []
        n = len(documents)
        for i in range(n):
            for j in range(i + 1, n):
                matches = self.match(documents[i], documents[j], threshold=0.0)
                results.append({"doc_a": i, "doc_b": j, "matches": matches})
        return results