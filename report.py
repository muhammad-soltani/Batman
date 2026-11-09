from typing import Any, Collection, Dict, List, Optional


def generate_report(
    matches: List[Dict[str, Any]],
    total_a: int,
    total_b: int,
    matched_b_indices: Optional[Collection[int]] = None,
) -> dict:
    """Aggregate statistics for the plagiarism report.

    Args:
        matches: Output of ``ParagraphMatcher.match`` (best B match per A sentence).
        total_a / total_b: Number of sentences in each text.
        matched_b_indices: Indices of B sentences that have a semantic
            equivalent in A. Matches only record the *best* B sentence for each
            A sentence, so deriving B's coverage from them under-counts B
            whenever several B sentences correspond to the same A sentence.
            When omitted, falls back to the B indices found in ``matches``.
    """
    matched_a = {m["a_index"] for m in matches}
    matched_b = (
        set(matched_b_indices) if matched_b_indices is not None else {m["b_index"] for m in matches}
    )
    coverage_a = len(matched_a) / total_a if total_a else 0.0
    coverage_b = len(matched_b) / total_b if total_b else 0.0
    avg_similarity = sum(m["similarity"] for m in matches) / len(matches) if matches else 0.0
    avg_exact = (
        sum(m.get("exact_similarity") or 0.0 for m in matches) / len(matches) if matches else 0.0
    )
    return {
        "matched_count": len(matches),
        "coverage_a": round(coverage_a, 3),
        "coverage_b": round(coverage_b, 3),
        "avg_semantic_similarity": round(avg_similarity, 3),
        "avg_exact_similarity": round(avg_exact, 3),
    }
