"""End-to-end tests against the real Sentence-BERT model.

Skipped automatically when the model is not available in the local
Hugging Face cache (these tests never download it). Run them after the model
has been downloaded once, e.g. by starting the backend.
"""
import pytest
from fastapi.testclient import TestClient

from app import create_app
from config import Settings

pytestmark = pytest.mark.model


@pytest.fixture(scope="module")
def client():
    settings = Settings()
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(settings.model_name, device="cpu", local_files_only=True)
    except Exception as exc:  # noqa: BLE001 - any load failure means "not available"
        pytest.skip(f"model {settings.model_name} not available locally: {exc}")
    with TestClient(create_app(settings=settings, model=model)) as test_client:
        yield test_client


def post(client, path, a, b):
    response = client.post(path, json={"text_a": a, "text_b": b})
    assert response.status_code == 200, response.text
    return response.json()


PARA_A = "هوش مصنوعی به ماشین‌ها این توانایی را می‌دهد که از تجربه یاد بگیرند."
PARA_B = "هوش مصنوعی قابلیت یادگیری از تجربه را به سیستم‌های کامپیوتری می‌دهد."


def test_paraphrase_is_matched_semantically_but_not_lexically(client):
    match = post(client, "/api/compare", PARA_A, PARA_B)["matches"][0]
    assert match["similarity"] > 0.8
    assert match["exact_similarity"] < match["similarity"]


def test_unrelated_sentences_are_not_matched(client):
    body = post(client, "/api/compare", "امروز هوا بسیار آفتابی و گرم است.", "قیمت نفت در بازارهای جهانی کاهش یافت.")
    assert body["matches"] == []


def test_arabic_letter_variants_are_identical_after_normalization(client):
    match = post(client, "/api/compare", "كتابخانه ملي ايران بزرگ است.", "کتابخانه ملی ایران بزرگ است.")["matches"][0]
    assert match["similarity"] == pytest.approx(1.0, abs=1e-4)
    assert match["exact_similarity"] == 1.0


def test_paraphrase_is_not_listed_as_semantic_difference(client):
    sem = post(client, "/api/diff-highlight", PARA_A, PARA_B)["semantic_diff"]
    assert sem["only_in_a"] == [] and sem["only_in_b"] == []
    assert sem["semantic_similarity"] > 0.8


def test_long_texts_are_compared_beyond_the_model_token_limit(client):
    # Regression: the whole text used to be embedded at once and truncated at
    # 128 tokens, so texts sharing only their opening scored 1.0.
    head = "این یک متن طولانی درباره تاریخ ایران باستان و سلسله‌های پادشاهی آن است. " * 12
    a = head + "اقتصاد جهانی در حال تحول است و بازارهای مالی نوسان دارند. " * 10
    b = head + "ورزش فوتبال در جهان محبوبیت زیادی دارد و تیم‌ها رقابت می‌کنند. " * 10
    sem = post(client, "/api/diff-highlight", a, b)["semantic_diff"]
    assert sem["semantic_similarity"] < 0.9
    assert sem["only_in_a"] and sem["only_in_b"]


def test_completely_different_texts_report(client):
    body = post(
        client, "/api/report",
        "گربه روی دیوار نشسته است. پرندگان در آسمان پرواز می‌کنند.",
        "قیمت نفت در بازارهای جهانی کاهش یافت. بانک مرکزی نرخ بهره را افزایش داد.",
    )
    assert body["report"]["coverage_a"] == 0.0
    assert body["report"]["coverage_b"] == 0.0


def test_identical_texts_report_full_coverage(client):
    text = "جمله اول درباره علم است. جمله دوم درباره هنر است. جمله سوم درباره ورزش است."
    report = post(client, "/api/report", text, text)["report"]
    assert report["coverage_a"] == report["coverage_b"] == 1.0
    assert report["avg_exact_similarity"] == 1.0
