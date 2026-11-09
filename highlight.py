import html
from difflib import SequenceMatcher
from typing import List, Optional, Tuple

from similarity import comparison_words

# Minimum semantic (cosine) similarity required to attempt word-level diff.
DIFF_SEMANTIC_THRESHOLD = 0.10

# Minimum SequenceMatcher text-overlap ratio required to show word-level diff.
# Even if semantic similarity passes, texts with very few common tokens are
# treated as completely different.
DIFF_TEXT_OVERLAP_THRESHOLD = 0.10

_CIRCLED_NUMBERS = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"


def _marker(n: int) -> str:
    return _CIRCLED_NUMBERS[n - 1] if n <= len(_CIRCLED_NUMBERS) else f"({n})"


def _span(css_class: str, words: List[str], suffix: str = "") -> str:
    # Every piece of user text is HTML-escaped here; the frontend renders this
    # markup with v-html, so this escaping is the XSS boundary.
    return f'<span class="{css_class}">{html.escape(" ".join(words))}{suffix}</span>'


def _units(text: str) -> Tuple[List[str], List[str]]:
    """Split text into display words and their comparison keys.

    Keys ignore punctuation, half-spaces, diacritics and Arabic letter
    variants, so "است." and "است" or "هوش‌مصنوعی" and "هوش مصنوعی"-style
    differences are not reported as changes. Punctuation-only tokens are
    attached to the preceding word for display.
    """
    display: List[str] = []
    keys: List[str] = []
    for word in text.split():
        key = "".join(comparison_words(word))
        if not key and display:
            display[-1] = f"{display[-1]} {word}"
            continue
        display.append(word)
        keys.append(key)
    return display, keys


def highlight_diff(
    text_a: str,
    text_b: str,
    semantic_similarity: Optional[float] = None,
    threshold: float = DIFF_SEMANTIC_THRESHOLD,
    text_overlap_threshold: float = DIFF_TEXT_OVERLAP_THRESHOLD,
) -> dict:
    """Return HTML-annotated word-level diff of two texts.

    The diff is computed over words. Whitespace is not part of the alignment,
    otherwise the shared spaces between words would anchor the matcher and
    split a single changed phrase into many separately numbered replacements.
    Words are compared by a normalized key (see ``_units``), but shown as
    written.

    A pair is declared *completely different* (no word-level diff) when:
      • semantic_similarity is provided and is below ``threshold``, OR
      • the word-overlap ratio (SequenceMatcher.ratio) is below
        ``text_overlap_threshold`` — catches unrelated texts that still score
        moderately on cosine similarity due to superficial structure.
    """
    words_a, keys_a = _units(text_a)
    words_b, keys_b = _units(text_b)

    def _completely_different() -> dict:
        return {
            "a_html": _span("diff-del diff-completely-different", words_a),
            "b_html": _span("diff-ins diff-completely-different", words_b),
            "completely_different": True,
        }

    # ── Gate 1: semantic similarity check ────────────────────────────────────
    if semantic_similarity is not None and semantic_similarity < threshold:
        return _completely_different()

    # ── Gate 2: word-overlap ratio check ─────────────────────────────────────
    seq = SequenceMatcher(None, keys_a, keys_b, autojunk=False)
    if seq.ratio() < text_overlap_threshold:
        return _completely_different()

    a_html: List[str] = []
    b_html: List[str] = []
    replace_counter = 0

    for tag, i1, i2, j1, j2 in seq.get_opcodes():
        if tag == "equal":
            a_html.append(_span("diff-equal", words_a[i1:i2]))
            b_html.append(_span("diff-equal", words_b[j1:j2]))
        elif tag == "replace":
            replace_counter += 1
            sup = f"<sup>{_marker(replace_counter)}</sup>"
            a_html.append(_span("diff-replace diff-replace-del", words_a[i1:i2], sup))
            b_html.append(_span("diff-replace diff-replace-ins", words_b[j1:j2], sup))
        elif tag == "delete":
            a_html.append(_span("diff-del", words_a[i1:i2]))
        elif tag == "insert":
            b_html.append(_span("diff-ins", words_b[j1:j2]))

    return {"a_html": " ".join(a_html), "b_html": " ".join(b_html), "completely_different": False}
