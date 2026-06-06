from difflib import SequenceMatcher
import html
import re
from typing import Optional

# Minimum semantic (cosine) similarity required to attempt word-level diff.
DIFF_SEMANTIC_THRESHOLD = 0.55

# Minimum SequenceMatcher text-overlap ratio required to show word-level diff.
# Even if semantic similarity passes, texts with very few common tokens are
# treated as completely different.
DIFF_TEXT_OVERLAP_THRESHOLD = 0.25

def _normalize_whitespace(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()

def _tokenize(text: str):
    """Split text into word+space tokens for readable diffs."""
    return re.findall(r'\S+|\s+', text)

def highlight_diff(
    text_a: str,
    text_b: str,
    semantic_similarity: Optional[float] = None,
    threshold: float = DIFF_SEMANTIC_THRESHOLD,
    text_overlap_threshold: float = DIFF_TEXT_OVERLAP_THRESHOLD,
) -> dict:
    """Return HTML-annotated diff of two texts.

    A pair is declared *completely different* (no word-level diff) when:
      • semantic_similarity is provided and is below ``threshold``, OR
      • the actual token-overlap ratio (SequenceMatcher.ratio) is below
        ``text_overlap_threshold`` — catches unrelated texts that still score
        moderately on cosine similarity due to superficial structure.
    """
    # Normalise whitespace so stray spaces don't pollute the diff
    norm_a = _normalize_whitespace(text_a)
    norm_b = _normalize_whitespace(text_b)

    def _completely_different() -> dict:
        return {
            "a_html": f'<span class="diff-del diff-completely-different">{html.escape(norm_a)}</span>',
            "b_html": f'<span class="diff-ins diff-completely-different">{html.escape(norm_b)}</span>',
            "completely_different": True,
        }

    # ── Gate 1: semantic similarity check ────────────────────────────────────
    if semantic_similarity is not None and semantic_similarity < threshold:
        return _completely_different()

    tokens_a = _tokenize(norm_a)
    tokens_b = _tokenize(norm_b)
    seq = SequenceMatcher(None, tokens_a, tokens_b, autojunk=False)

    # ── Gate 2: actual text-overlap ratio check ───────────────────────────────
    # Filter out whitespace-only tokens before measuring overlap so that shared
    # punctuation / spacing doesn't inflate the ratio.
    words_a = [t for t in tokens_a if t.strip()]
    words_b = [t for t in tokens_b if t.strip()]
    word_seq = SequenceMatcher(None, words_a, words_b, autojunk=False)
    if word_seq.ratio() < text_overlap_threshold:
        return _completely_different()

    a_html: list = []
    b_html: list = []
    replace_counter = 0

    def _num(n):
        circles = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"
        return circles[n - 1] if n <= len(circles) else f"({n})"

    for tag, i1, i2, j1, j2 in seq.get_opcodes():
        chunk_a = html.escape("".join(tokens_a[i1:i2]))
        chunk_b = html.escape("".join(tokens_b[j1:j2]))
        if tag == "equal":
            a_html.append(f'<span class="diff-equal">{chunk_a}</span>')
            b_html.append(f'<span class="diff-equal">{chunk_b}</span>')
        elif tag == "replace":
            replace_counter += 1
            num = _num(replace_counter)
            a_html.append(
                f'<span class="diff-replace diff-replace-del">'
                f'{chunk_a}<sup>{num}</sup>'
                f'</span>'
            )
            b_html.append(
                f'<span class="diff-replace diff-replace-ins">'
                f'{chunk_b}<sup>{num}</sup>'
                f'</span>'
            )
        elif tag == "delete":
            a_html.append(f'<span class="diff-del">{chunk_a}</span>')
        elif tag == "insert":
            b_html.append(f'<span class="diff-ins">{chunk_b}</span>')
    return {"a_html": "".join(a_html), "b_html": "".join(b_html), "completely_different": False}
