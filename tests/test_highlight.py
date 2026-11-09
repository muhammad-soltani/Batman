import re

from highlight import highlight_diff


def _text(html_fragment: str) -> str:
    """Strip tags and <sup> markers to recover the visible words."""
    without_sup = re.sub(r"<sup>.*?</sup>", "", html_fragment)
    return " ".join(re.sub(r"<[^>]+>", " ", without_sup).split())


def test_identical_texts_are_all_equal():
    result = highlight_diff("سلام دنیا زیبا", "سلام دنیا زیبا")
    assert result["completely_different"] is False
    assert result["a_html"] == '<span class="diff-equal">سلام دنیا زیبا</span>'
    assert result["a_html"] == result["b_html"]


def test_single_word_replacement_is_one_numbered_change():
    result = highlight_diff("من به مدرسه رفتم", "من به دانشگاه رفتم")
    assert result["a_html"].count("<sup>①</sup>") == 1
    assert "diff-replace-del" in result["a_html"] and "مدرسه" in result["a_html"]
    assert "diff-replace-ins" in result["b_html"] and "دانشگاه" in result["b_html"]
    assert "②" not in result["a_html"]


def test_contiguous_replaced_phrase_gets_a_single_marker():
    # Regression: whitespace used to be diffed as tokens, so the shared spaces
    # split one changed phrase into several numbered replacements.
    result = highlight_diff("اول الف ب ج آخر", "اول ی ک ل آخر")
    assert result["a_html"].count("<sup>") == 1
    assert "diff-equal" in result["a_html"]


def test_insert_and_delete():
    result = highlight_diff("یک دو سه چهار", "یک دو چهار پنج")
    assert '<span class="diff-del">سه</span>' in result["a_html"]
    assert '<span class="diff-ins">پنج</span>' in result["b_html"]


def test_visible_text_is_preserved():
    a = "متن اول با   فاصله‌های\nزیاد و تغییرات"
    b = "متن دوم با فاصله‌های زیاد و تغییرات بیشتر"
    result = highlight_diff(a, b)
    assert _text(result["a_html"]) == " ".join(a.split())
    assert _text(result["b_html"]) == " ".join(b.split())


def test_html_is_escaped():
    a = '<script>alert("x")</script> & متن'
    b = '<img src=x onerror=alert(1)> & متن'
    result = highlight_diff(a, b)
    for fragment in (result["a_html"], result["b_html"]):
        assert "<script" not in fragment
        assert "<img" not in fragment
        assert "&lt;" in fragment
        assert "&amp;" in fragment


def test_html_is_escaped_when_completely_different():
    result = highlight_diff("<b>bold</b>", "<i>x</i>", semantic_similarity=0.0, threshold=0.5)
    assert result["completely_different"] is True
    assert "<b>" not in result["a_html"] and "&lt;b&gt;" in result["a_html"]


def test_low_semantic_similarity_short_circuits():
    result = highlight_diff("سلام دنیا", "سلام دنیا", semantic_similarity=0.05, threshold=0.10)
    assert result["completely_different"] is True
    assert "diff-completely-different" in result["a_html"]


def test_semantic_similarity_none_skips_semantic_gate():
    result = highlight_diff("سلام دنیا", "سلام دنیا", semantic_similarity=None)
    assert result["completely_different"] is False


def test_low_word_overlap_is_completely_different():
    result = highlight_diff(
        "گربه روی دیوار نشست", "بازار سهام امروز سقوط کرد",
        semantic_similarity=0.9, text_overlap_threshold=0.25,
    )
    assert result["completely_different"] is True


def test_one_side_empty():
    result = highlight_diff("", "متن")
    assert result["completely_different"] is True
    assert "متن" in result["b_html"]


def test_more_than_twenty_replacements_use_parenthesized_numbers():
    a = " ".join(f"ثابت{i} الف{i}" for i in range(25))
    b = " ".join(f"ثابت{i} ب{i}" for i in range(25))
    result = highlight_diff(a, b)
    assert "⑳" in result["a_html"]
    assert "(21)" in result["a_html"] and "(25)" in result["b_html"]


def test_long_texts_complete_quickly():
    import time

    words = [f"واژه{i % 500}" for i in range(8000)]
    a = " ".join(words)
    b = " ".join(w if i % 50 else "تغییر" for i, w in enumerate(words))
    start = time.perf_counter()
    result = highlight_diff(a, b)
    assert time.perf_counter() - start < 10
    assert result["completely_different"] is False


def test_punctuation_and_half_space_differences_are_not_changes():
    result = highlight_diff("علم، بهتر از ثروت است.", "علم بهتر از ثروت است")
    assert "diff-replace" not in result["a_html"] and "diff-del" not in result["a_html"]
    assert "diff-ins" not in result["b_html"]
    # The text is still shown exactly as written.
    assert "علم،" in result["a_html"] and "است." in result["a_html"]


def test_standalone_punctuation_is_attached_to_previous_word():
    result = highlight_diff("سلام ، دنیا", "سلام دنیا")
    assert result["a_html"] == '<span class="diff-equal">سلام ، دنیا</span>'
