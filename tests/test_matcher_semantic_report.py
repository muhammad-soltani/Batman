"""Matching, document-level similarity, semantic diff and report statistics."""
import threading

import numpy as np
import pytest

from matcher import ParagraphMatcher
from report import generate_report
from semantic import document_similarity, semantic_diff
from similarity import Similarity
from tests.conftest import FakeModel


@pytest.fixture
def matcher(fake_model):
    return ParagraphMatcher(fake_model, similarity=Similarity())


# ── ParagraphMatcher ─────────────────────────────────────────────────────────
def test_match_empty_inputs_do_not_call_model(matcher, fake_model):
    assert matcher.match([], ["الف"]) == []
    assert matcher.match(["الف"], []) == []
    assert fake_model.calls == []


def test_match_encodes_both_sides_in_one_batch(matcher, fake_model):
    matcher.match(["الف ب", "ج د"], ["الف ب"])
    assert fake_model.calls == [["الف ب", "ج د", "الف ب"]]


def test_identical_sentences_match_with_full_score(matcher):
    matches = matcher.match(["گربه روی دیوار است."], ["گربه روی دیوار است."], with_exact=True)
    assert len(matches) == 1
    assert matches[0]["similarity"] == 1.0
    assert matches[0]["exact_similarity"] == 1.0


def test_unrelated_sentences_are_not_matched(matcher):
    assert matcher.match(["گربه روی دیوار"], ["بازار سهام سقوط کرد"]) == []


def test_exact_similarity_only_when_requested(matcher):
    matches = matcher.match(["الف ب"], ["الف ب"])
    assert "exact_similarity" not in matches[0]


def test_matches_sorted_by_similarity_desc(matcher):
    a = ["یک دو سه چهار", "پنج شش هفت هشت"]
    b = ["پنج شش هفت هشت", "یک دو سه نه"]
    matches = matcher.match(a, b)
    scores = [m["similarity"] for m in matches]
    assert scores == sorted(scores, reverse=True)
    assert matches[0]["a_index"] == 1 and matches[0]["b_index"] == 0


def test_threshold_is_exclusive(matcher):
    sim = np.array([[0.5], [0.5001]])
    alignment = matcher.align(["a", "b"], ["c"], threshold=0.5, lexical_threshold=None, sim_matrix=sim)
    assert [m["a_index"] for m in alignment.matches()] == [1]


def test_default_threshold_rejects_same_topic_sentences(matcher):
    # 0.59 is what "students study in the library" vs "professors teach at the
    # university" scores with the real model: same topic, not the same content.
    sim = np.array([[0.59]])
    alignment = matcher.align(["دانشجویان درس می‌خوانند"], ["استادان تدریس می‌کنند"], sim_matrix=sim)
    assert alignment.matches() == []


def test_near_verbatim_copy_matches_despite_low_semantic_score(matcher):
    # One flipped word changes the meaning (low cosine) but the text is copied.
    a, b = ["قیمت طلا امروز در بازار افزایش یافت"], ["قیمت طلا امروز در بازار کاهش یافت"]
    alignment = matcher.align(a, b, sim_matrix=np.array([[0.53]]))
    matches = alignment.matches()
    assert len(matches) == 1 and matches[0]["exact_similarity"] >= 0.8
    assert alignment.b_matched.tolist() == [True]


def test_lexical_rule_can_be_disabled(matcher):
    a, b = ["قیمت طلا امروز در بازار افزایش یافت"], ["قیمت طلا امروز در بازار کاهش یافت"]
    alignment = matcher.align(a, b, lexical_threshold=None, sim_matrix=np.array([[0.53]]))
    assert alignment.matches() == []


def test_lexical_rule_needs_a_lexical_scorer(fake_model):
    m = ParagraphMatcher(fake_model)  # no Similarity → semantic rule only
    alignment = m.align(["الف ب"], ["الف ب"], sim_matrix=np.array([[0.53]]))
    assert alignment.matches() == []


def test_b_coverage_uses_best_a_counterpart(matcher):
    # Both B sentences copy A's single sentence; A can only point at one of them.
    sim = np.array([[0.95, 0.95]])
    alignment = matcher.align(["الف"], ["الف", "الف"], sim_matrix=sim)
    assert alignment.b_matched.tolist() == [True, True]
    assert len(alignment.matches()) == 1


def test_similarity_matrix_is_clipped(matcher):
    class OverflowModel:
        def encode(self, texts, **kwargs):
            return np.ones((len(texts), 4), dtype=np.float32) * 1e6

    m = ParagraphMatcher(OverflowModel())
    sim = m.similarity_matrix(["a"], ["a"])
    assert sim.max() <= 1.0


def test_zero_vector_sentences_do_not_produce_nan(matcher):
    # Punctuation-only text embeds to a zero vector in the fake model.
    sim = matcher.similarity_matrix(["...", "الف"], ["!!!"])
    assert not np.isnan(sim).any()


def test_multi_document_match_keeps_every_pair(matcher):
    results = matcher.multi_document_match([["الف"], ["ب"], ["ج"]])
    assert [(r["doc_a"], r["doc_b"]) for r in results] == [(0, 1), (0, 2), (1, 2)]
    # Unrelated sentences (cosine 0) are still reported when every pair is kept.
    assert all(len(r["matches"]) == 1 for r in results)


def test_inference_concurrency_is_bounded():
    model = FakeModel(delay=0.05)
    m = ParagraphMatcher(model, max_concurrent_inference=2)
    threads = [threading.Thread(target=m.match, args=(["الف"], ["ب"])) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(model.calls) == 8
    assert model.max_active <= 2


# ── semantic ─────────────────────────────────────────────────────────────────
def test_document_similarity_single_pair_equals_cosine():
    assert document_similarity(np.array([[0.73]])) == pytest.approx(0.73)


def test_document_similarity_is_symmetric():
    sim = np.array([[0.9, 0.1, 0.2], [0.3, 0.4, 0.8]])
    assert document_similarity(sim) == pytest.approx(document_similarity(sim.T))


def test_document_similarity_reflects_partially_different_documents():
    # Two shared sentences, two unrelated ones: the score must drop well below 1.
    sim = np.array([[1.0, 0.0], [0.0, 0.0]])
    assert document_similarity(sim) == pytest.approx(0.5)


def test_document_similarity_empty_matrix():
    assert document_similarity(np.zeros((0, 3))) == 0.0


def test_document_similarity_ignores_negative_cosines():
    # Unrelated sentences can have slightly negative cosine; they count as 0.
    assert document_similarity(np.array([[-0.12]])) == 0.0
    assert document_similarity(np.array([[1.0, -0.3], [-0.3, -0.2]])) == pytest.approx(0.5)


def _diff(matcher, a, b, sim, **kwargs):
    return semantic_diff(matcher.align(a, b, sim_matrix=np.array(sim), **kwargs))


def test_semantic_diff_reports_unmatched_sentences_in_order(matcher):
    a = ["مشترک", "فقط الف دوم", "فقط الف اول"]
    b = ["مشترک", "فقط ب"]
    result = _diff(matcher, a, b, [[1.0, 0.0], [0.1, 0.2], [0.0, 0.3]], lexical_threshold=None)
    assert result["only_in_a"] == ["فقط الف دوم", "فقط الف اول"]
    assert result["only_in_b"] == ["فقط ب"]


def test_semantic_diff_paraphrase_is_not_a_difference(matcher):
    # paraphrase: different wording, same meaning
    result = _diff(matcher, ["الف"], ["ب"], [[0.93]])
    assert result["only_in_a"] == [] and result["only_in_b"] == []


def test_semantic_diff_deduplicates_repeated_sentences(matcher):
    result = _diff(matcher, ["تکرار", "تکرار"], ["دیگر"], [[0.0], [0.0]])
    assert result["only_in_a"] == ["تکرار"]


def test_semantic_diff_identical_texts(matcher):
    result = _diff(matcher, ["الف", "ب"], ["الف", "ب"], np.eye(2))
    assert result == {"semantic_similarity": 1.0, "only_in_a": [], "only_in_b": []}


def test_semantic_diff_empty_side(matcher):
    result = semantic_diff(matcher.align([], ["الف"], sim_matrix=np.zeros((0, 1))))
    assert result["semantic_similarity"] == 0.0
    assert result["only_in_b"] == ["الف"]


# ── report ───────────────────────────────────────────────────────────────────
def _m(a, b, sim, exact=None):
    entry = {"a_index": a, "b_index": b, "similarity": sim, "text_a": "", "text_b": ""}
    if exact is not None:
        entry["exact_similarity"] = exact
    return entry


def test_report_no_matches():
    assert generate_report([], 3, 4) == {
        "matched_count": 0,
        "coverage_a": 0.0,
        "coverage_b": 0.0,
        "avg_semantic_similarity": 0.0,
        "avg_exact_similarity": 0.0,
    }


def test_report_zero_totals_do_not_divide_by_zero():
    assert generate_report([], 0, 0)["coverage_a"] == 0.0


def test_report_averages_and_coverage():
    report = generate_report([_m(0, 0, 0.9, 0.8), _m(1, 0, 0.7, 0.4)], 4, 2)
    assert report["matched_count"] == 2
    assert report["coverage_a"] == 0.5
    assert report["coverage_b"] == 0.5  # derived from matches when indices not given
    assert report["avg_semantic_similarity"] == 0.8
    assert report["avg_exact_similarity"] == 0.6


def test_report_uses_explicit_b_coverage():
    # B = "x. x." copied from A = "x.": both B sentences are covered even though
    # A's single sentence can only point at one of them.
    report = generate_report([_m(0, 0, 1.0, 1.0)], 1, 2, matched_b_indices=[0, 1])
    assert report["coverage_b"] == 1.0


def test_report_missing_exact_similarity_counts_as_zero():
    report = generate_report([_m(0, 0, 0.9), _m(1, 1, 0.9, 1.0)], 2, 2)
    assert report["avg_exact_similarity"] == 0.5
