"""Lexical (surface) similarity between two sentences.

The score compares *words*, not characters. A character-level edit ratio
gives unrelated Persian sentences ~40% similarity, because spaces and the
most frequent letters (ا، ی، ن، ر، ...) always line up; spacing, half-space
and punctuation differences also lowered the score of identical sentences.

Algorithm: an order-aware longest-common-subsequence over word sequences in
which two words count as matching when their character similarity is at
least ``WORD_MATCH_THRESHOLD`` (credit = that similarity). This gives
partial credit to inflected forms (کتاب / کتاب‌ها) while unrelated words
score nothing. Result in [0, 1]:  2 * LCS / (len(a) + len(b)).
"""
import re
import unicodedata
from typing import List

import numpy as np
from rapidfuzz import process
from rapidfuzz.distance import Indel

# Two words match when their character similarity reaches this value.
WORD_MATCH_THRESHOLD = 0.8

# Above this many word pairs the fuzzy DP (pure Python, O(n·m)) is replaced by
# an exact word-level LCS computed in C — only hit by "sentences" of hundreds
# of words without punctuation.
_MAX_FUZZY_CELLS = 250_000

# Arabic diacritics (harakat), superscript alef and tatweel carry no lexical
# meaning for comparison purposes.
_IGNORED = re.compile(r"[ً-ٰٟـ]")
_FOLD = str.maketrans({"ي": "ی", "ى": "ی", "ك": "ک"})


def _is_separator(char: str) -> bool:
    # Whitespace (Z*), punctuation (P*), symbols (S*) and control/format
    # characters (C*: newline, ZWNJ, RLM/LRM, ...) all separate words, so
    # "هوش مصنوعی", "هوش‌مصنوعی" and "هوش  مصنوعی ،" compare as equal.
    return unicodedata.category(char)[0] in "ZPSC"


def comparison_words(text: str) -> List[str]:
    """Words of ``text`` reduced to a form suitable for comparison."""
    text = _IGNORED.sub("", text).translate(_FOLD).lower()
    return "".join(" " if _is_separator(c) else c for c in text).split()


def word_sequence_similarity(
    words_a: List[str],
    words_b: List[str],
    word_threshold: float = WORD_MATCH_THRESHOLD,
) -> float:
    """Fuzzy word-level LCS similarity of two word sequences, in [0, 1]."""
    if not words_a and not words_b:
        return 1.0
    if not words_a or not words_b:
        return 0.0
    n, m = len(words_a), len(words_b)
    if n * m > _MAX_FUZZY_CELLS:
        return float(Indel.normalized_similarity(words_a, words_b))

    # Pairwise word similarities computed in C. The threshold is applied here
    # rather than via ``score_cutoff``, which rounds internally and drops
    # scores exactly at the threshold (e.g. کتاب / کتابها = 0.8).
    scores = process.cdist(words_a, words_b, scorer=Indel.normalized_similarity, dtype=np.float64)
    scores[scores < word_threshold - 1e-9] = 0.0
    scores = scores.tolist()

    prev = [0.0] * (m + 1)
    for row in scores:
        cur = [0.0] * (m + 1)
        for j, score in enumerate(row):
            best = prev[j + 1] if prev[j + 1] > cur[j] else cur[j]
            if score:
                diag = prev[j] + score
                if diag > best:
                    best = diag
            cur[j + 1] = best
        prev = cur
    return min(1.0, 2.0 * prev[m] / (n + m))


class Similarity:
    """Lexical similarity of two texts (see module docstring)."""

    def exact(self, text_a: str, text_b: str) -> float:
        """Word-level lexical similarity in [0, 1] (1.0 = same words, same order)."""
        return word_sequence_similarity(comparison_words(text_a), comparison_words(text_b))
