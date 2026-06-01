from typing import List, Dict, Any

def generate_report(matches: List[Dict[str, Any]], total_a: int, total_b: int) -> dict:
    matched_a = {m['a_index'] for m in matches}
    matched_b = {m['b_index'] for m in matches}
    coverage_a = len(matched_a) / total_a if total_a else 0.0
    coverage_b = len(matched_b) / total_b if total_b else 0.0
    avg_similarity = sum(m['similarity'] for m in matches) / len(matches) if matches else 0.0
    avg_exact = sum(m.get('exact_similarity', 0.0) for m in matches) / len(matches) if matches else 0.0
    return {
        'matched_count': len(matches),
        'coverage_a': round(coverage_a, 3),
        'coverage_b': round(coverage_b, 3),
        'avg_semantic_similarity': round(avg_similarity, 3),
        'avg_exact_similarity': round(avg_exact, 3),
    }
