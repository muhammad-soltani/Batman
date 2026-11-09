"""Normalization, sentence chunking and exact similarity on Persian edge cases."""
import pytest

from chunker import chunk_sentences
from normalizer import PersianNormalizer
from similarity import Similarity

ZWNJ = "‌"


@pytest.fixture(scope="module")
def normalizer():
    return PersianNormalizer()


def test_arabic_letters_are_unified_to_persian(normalizer):
    assert normalizer.normalize("كتاب يك علي") == "کتاب یک علی"


def test_arabic_and_persian_variants_normalize_identically(normalizer):
    assert normalizer.normalize("كتابخانه ملي") == normalizer.normalize("کتابخانه ملی")


def test_half_space_and_plain_space_variants_converge(normalizer):
    with_zwnj = normalizer.normalize(f"می{ZWNJ}روم به خانه{ZWNJ}ها")
    with_space = normalizer.normalize("می روم به خانه ها")
    assert with_zwnj == with_space
    assert ZWNJ in with_zwnj


def test_digits_are_unified(normalizer):
    assert normalizer.normalize("1403") == normalizer.normalize("١٤٠٣") == "۱۴۰۳"


def test_empty_and_whitespace_input(normalizer):
    assert normalizer.normalize("") == ""
    assert chunk_sentences(normalizer.normalize("   \n\t ")) == []


def test_chunker_splits_on_persian_and_latin_punctuation(normalizer):
    text = normalizer.normalize("سلام. حالت چطوره؟ من خوبم! ممنون")
    assert chunk_sentences(text) == ["سلام.", "حالت چطوره؟", "من خوبم!", "ممنون"]


def test_chunker_paragraph_breaks_split_sentences(normalizer):
    text = normalizer.normalize("خط اول\n\nخط دوم")
    assert chunk_sentences(text) == ["خط اول", "خط دوم"]


def test_chunker_drops_empty_fragments():
    assert chunk_sentences("") == []
    assert all(s.strip() for s in chunk_sentences("جمله اول.   \n\n   . جمله دوم."))


def test_chunker_drops_fragments_without_letters_or_digits(normalizer):
    assert chunk_sentences(normalizer.normalize("...!!!؟؟")) == []
    assert chunk_sentences(normalizer.normalize("‌‌")) == []
    assert chunk_sentences(normalizer.normalize("سلام. ... !!! خداحافظ.")) == ["سلام.", "خداحافظ."]


def test_repeated_letters_are_collapsed_by_hazm(normalizer):
    # Hazm reduces elongated letters (3+ repeats), restoring known words.
    assert normalizer.normalize("خیلییییی خوب") == "خیلی خوب"
    assert normalizer.normalize("ببب") == "بب"


def test_chunker_handles_very_long_text(normalizer):
    text = normalizer.normalize("این یک جمله آزمایشی است. " * 3000)
    assert len(chunk_sentences(text)) == 3000


@pytest.mark.parametrize(
    "a, b, expected",
    [
        ("سلام دنیا", "سلام دنیا", 1.0),
        ("سلام   دنیا\n", " سلام دنیا", 1.0),  # whitespace-insensitive
        ("abc", "xyz", 0.0),
        ("", "", 1.0),
    ],
)
def test_exact_similarity_bounds(a, b, expected):
    assert Similarity().exact(a, b) == pytest.approx(expected)


def test_exact_similarity_partial_overlap_is_between_zero_and_one():
    score = Similarity().exact("هوش مصنوعی آینده است", "هوش مصنوعی گذشته بود")
    assert 0.0 < score < 1.0


# ── Lexical similarity: formatting must not affect the score ─────────────────
@pytest.mark.parametrize(
    "a, b",
    [
        ("هوش مصنوعی   آینده‌ی جهان را تغییر می‌دهد .", "هوش‌مصنوعی آینده ی جهان را تغییر می دهد"),  # spaces / ZWNJ
        ("دانشجویان، در کتابخانه درس می‌خوانند!", "دانشجویان در کتابخانه درس می‌خوانند."),  # punctuation
        ("كتابخانه ملي ايران", "کتابخانه ملی ایران"),  # Arabic letters
        ("عِلم بهتر از ثروت است", "علم بهتر از ثروت است"),  # diacritics
        ("ســـلام دوست من", "سلام دوست من"),  # tatweel
        ("«نقل قول» (پرانتز) - خط", "نقل قول پرانتز خط"),  # symbols
    ],
)
def test_formatting_differences_do_not_lower_lexical_similarity(a, b):
    assert Similarity().exact(a, b) == pytest.approx(1.0)


@pytest.mark.parametrize(
    "a, b",
    [
        ("امروز هوا بسیار آفتابی و گرم است.", "قیمت نفت در بازارهای جهانی کاهش یافت."),
        ("کتاب را روی میز گذاشتم.", "فوتبال محبوب‌ترین ورزش جهان شده."),
        ("مادرم دیشب غذای خوشمزه‌ای پخت.", "دولت قانون جدید مالیات را تصویب کرد."),
    ],
)
def test_unrelated_sentences_have_zero_lexical_similarity(a, b):
    # Regression: the old character-level ratio gave these ~36–44% because
    # spaces and common Persian letters always line up.
    assert Similarity().exact(a, b) == pytest.approx(0.0)


def test_one_changed_word_scores_high_but_not_full():
    score = Similarity().exact(
        "دانشجویان هر روز در کتابخانه دانشگاه درس می‌خوانند.",
        "دانشجویان هر روز در کتابخانه مدرسه درس می‌خوانند.",
    )
    assert 0.8 < score < 1.0


def test_inflected_word_gets_partial_credit():
    exact_word = Similarity().exact("کتاب خوب", "کتاب خوب")
    inflected = Similarity().exact("کتاب خوب", "کتابها خوب")
    unrelated = Similarity().exact("کتاب خوب", "دفتر خوب")
    assert exact_word > inflected > unrelated


def test_word_order_matters():
    same = Similarity().exact("الف ب ج د", "الف ب ج د")
    reordered = Similarity().exact("الف ب ج د", "د ج ب الف")
    assert reordered < same


def test_lexical_similarity_is_symmetric():
    a, b = "هوش مصنوعی آینده است", "آینده هوش مصنوعی روشن است"
    assert Similarity().exact(a, b) == pytest.approx(Similarity().exact(b, a))


def test_very_long_sentences_use_fast_path():
    import time

    a = " ".join(f"واژه{i}" for i in range(3000))
    b = " ".join(f"واژه{i}" for i in range(0, 3000, 2))
    start = time.perf_counter()
    score = Similarity().exact(a, b)
    assert time.perf_counter() - start < 5
    assert score == pytest.approx(2 * 1500 / 4500)
