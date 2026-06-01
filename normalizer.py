from typing import List
from hazm import Normalizer as HazmNormalizer

class PersianNormalizer:
    def __init__(self):
        self.normalizer = HazmNormalizer()

    def normalize(self, text: str) -> str:
        return self.normalizer.normalize(text)

    def normalize_list(self, texts: List[str]) -> List[str]:
        return [self.normalize(t) for t in texts]