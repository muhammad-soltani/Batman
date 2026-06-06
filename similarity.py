import re
from rapidfuzz.fuzz import ratio

def _normalize_whitespace(text: str) -> str:
    """Collapse multiple spaces/newlines and strip leading/trailing whitespace."""
    return re.sub(r'\s+', ' ', text).strip()

class Similarity:
    def __init__(self):
        # No state needed; RapidFuzz functions are stateless
        pass

    def exact(self, text_a: str, text_b: str) -> float:
        a = _normalize_whitespace(text_a)
        b = _normalize_whitespace(text_b)
        return ratio(a, b) / 100.0