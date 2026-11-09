from hazm import Normalizer as HazmNormalizer


class PersianNormalizer:
    """Thin wrapper around Hazm's normalizer.

    Unifies Arabic/Persian letter variants (ي→ی, ك→ک), digits, punctuation
    spacing and half-spaces (ZWNJ) so equivalent texts compare as equal.
    """

    def __init__(self):
        self.normalizer = HazmNormalizer()

    def normalize(self, text: str) -> str:
        return self.normalizer.normalize(text)
