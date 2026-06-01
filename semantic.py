from hazm import sent_tokenize
from sklearn.metrics.pairwise import cosine_similarity

class SemanticSimilarity:
    def __init__(self, model=None):
        self.model = model

    def compute(self, text_a: str, text_b: str) -> float:
        if self.model is None:
            return 0.0
        emb = self.model.encode([text_a, text_b], convert_to_numpy=True)
        return float(cosine_similarity([emb[0]], [emb[1]])[0][0])

    def diff(self, text_a: str, text_b: str) -> dict:
        sim = self.compute(text_a, text_b)
        set_a = set(sent_tokenize(text_a))
        set_b = set(sent_tokenize(text_b))
        return {
            "semantic_similarity": round(sim, 4),
            "only_in_a": list(set_a - set_b),
            "only_in_b": list(set_b - set_a),
        }