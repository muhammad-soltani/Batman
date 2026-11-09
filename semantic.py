"""Document-level semantic similarity and semantic sentence diff.

Both work on the sentence alignment computed once per request
(see ``ParagraphMatcher.align``), so embeddings are shared with the other
analyses and every view applies the same matching rule.

Why not embed the whole text at once? The Sentence-BERT model truncates its
input at ``max_seq_length`` (128 tokens for
paraphrase-multilingual-mpnet-base-v2). Any content past that limit is
silently ignored, so two long texts that share an opening paragraph would
score 1.0 even if everything after it differs. Aggregating sentence-level
scores covers the full text.
"""
from typing import Dict, List

import numpy as np

from matcher import Alignment


def document_similarity(sim_matrix: np.ndarray) -> float:
    """Symmetric best-match similarity of two documents, in [0, 1].

    For every sentence, take the score of its closest counterpart in the other
    document (negative cosines count as 0: "unrelated" is the floor), average
    per side, then average both directions:

        0.5 * (mean_i max(0, max_j S[i, j]) + mean_j max(0, max_i S[i, j]))

    For two single-sentence texts this equals their cosine similarity.
    Returns 0.0 when either side has no sentences.
    """
    if sim_matrix.size == 0:
        return 0.0
    a_to_b = float(np.mean(np.clip(np.max(sim_matrix, axis=1), 0.0, 1.0)))
    b_to_a = float(np.mean(np.clip(np.max(sim_matrix, axis=0), 0.0, 1.0)))
    return (a_to_b + b_to_a) / 2.0


def _unmatched(sentences: List[str], matched: np.ndarray) -> List[str]:
    """Sentences without a counterpart; keeps document order, drops repeats."""
    return list(dict.fromkeys(s for s, ok in zip(sentences, matched, strict=True) if not ok))


def semantic_diff(alignment: Alignment) -> Dict[str, object]:
    """Overall similarity plus the sentences that have no equivalent.

    A sentence is "only in A" when it has no counterpart in B under the same
    rule ``/compare`` uses (semantically similar or near-verbatim copy), so
    the views never disagree. Paraphrased sentences are therefore *not*
    reported as differences.
    """
    return {
        "semantic_similarity": round(document_similarity(alignment.sim_matrix), 4),
        "only_in_a": _unmatched(alignment.sentences_a, alignment.a_matched),
        "only_in_b": _unmatched(alignment.sentences_b, alignment.b_matched),
    }
