from rapidfuzz.fuzz import ratio

class Similarity:
    def __init__(self):
        # No state needed; RapidFuzz functions are stateless
        pass

    def exact(self, text_a: str, text_b: str) -> float:
        return ratio(text_a, text_b) / 100.0