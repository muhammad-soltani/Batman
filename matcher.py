from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

SIMILARITY_THRESHOLD = 0.5

class ParagraphMatcher:
    def __init__(self, model: SentenceTransformer, similarity=None):
        self.model = model
        self.similarity = similarity

    def embed(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

    def align(self, sentences_a: List[str], sentences_b: List[str]) -> List[Dict[str, Any]]:
        if not sentences_a or not sentences_b:
            return []
        emb_a = self.embed(sentences_a)
        emb_b = self.embed(sentences_b)
        sim_matrix = cosine_similarity(emb_a, emb_b)
        results = []
        for i, row in enumerate(sim_matrix):
            best_j = int(np.argmax(row))
            result = {
                "a_index": i,
                "b_index": best_j,
                "similarity": round(float(row[best_j]), 4),
                "text_a": sentences_a[i],
                "text_b": sentences_b[best_j],
            }
            if self.similarity is not None:
                result["exact_similarity"] = round(self.similarity.exact(sentences_a[i], sentences_b[best_j]), 4)
            results.append(result)
        return results

    def multi_document_match(self, documents: List[List[str]]) -> List[Dict[str, Any]]:
        results = []
        n = len(documents)
        for i in range(n):
            for j in range(i + 1, n):
                matches = self.align(documents[i], documents[j])
                results.append({"doc_a": i, "doc_b": j, "matches": matches})
        return results

    def match(self, sentences_a: List[str], sentences_b: List[str], with_exact: bool = False) -> List[Dict[str, Any]]:
        if not sentences_a or not sentences_b:
            return []
        emb_a = self.embed(sentences_a)
        emb_b = self.embed(sentences_b)
        sim_matrix = cosine_similarity(emb_a, emb_b)
        matches = []
        for i, row in enumerate(sim_matrix):
            best_j = int(np.argmax(row))
            best_score = float(row[best_j])
            if best_score > SIMILARITY_THRESHOLD:
                match: Dict[str, Any] = {
                    "a_index": i,
                    "b_index": best_j,
                    "similarity": round(best_score, 4),
                    "text_a": sentences_a[i],
                    "text_b": sentences_b[best_j],
                }
                if with_exact and self.similarity is not None:
                    match["exact_similarity"] = round(self.similarity.exact(sentences_a[i], sentences_b[best_j]), 4)
                matches.append(match)
        return matches