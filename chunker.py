import re
from typing import List

from hazm import sent_tokenize

# A fragment must contain at least one letter or digit to carry meaning.
# Punctuation-, symbol- or ZWNJ-only fragments (e.g. "...", "!!!") would
# otherwise be embedded and could produce spurious matches.
_HAS_WORD_CHAR = re.compile(r"\w")


def chunk_sentences(text: str) -> List[str]:
    """Split (normalized) Persian text into stripped, meaningful sentences."""
    sentences = (s.strip() for s in sent_tokenize(text))
    return [s for s in sentences if s and _HAS_WORD_CHAR.search(s)]
