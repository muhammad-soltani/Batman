"""HTTP API tests (fake model; no network or model download needed)."""
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from app import create_app
from config import Settings
from tests.conftest import FakeModel

TEXT_A = "هوش مصنوعی آینده را می‌سازد. امروز هوا آفتابی است. کتاب روی میز است."
TEXT_B = "هوش مصنوعی آینده را می‌سازد. قیمت نفت کاهش یافت."

ENDPOINTS = ["/api/compare", "/api/report", "/api/diff-highlight"]


def post(client, path, a, b):
    return client.post(path, json={"text_a": a, "text_b": b})


# ── Validation ───────────────────────────────────────────────────────────────
@pytest.mark.parametrize("path", ENDPOINTS)
@pytest.mark.parametrize(
    "a, b",
    [("", "متن"), ("متن", ""), ("   \n\t", "متن"), ("متن", "  ")],
)
def test_empty_or_blank_input_is_rejected_by_every_endpoint(client, path, a, b):
    response = post(client, path, a, b)
    assert response.status_code == 400
    assert response.json()["detail"] == "Both text_a and text_b are required."


@pytest.mark.parametrize("path", ENDPOINTS)
def test_text_that_normalizes_to_nothing_is_rejected(client, path):
    response = post(client, path, "‌‌", "متن")
    assert response.status_code == 400
    assert isinstance(response.json()["detail"], str)


@pytest.mark.parametrize("path", ENDPOINTS)
def test_too_long_text_is_rejected(client, path, settings):
    response = post(client, path, "ا" * (settings.max_text_length + 1), "متن")
    assert response.status_code == 413
    assert str(settings.max_text_length) in response.json()["detail"]


@pytest.mark.parametrize("path", ENDPOINTS)
def test_text_at_the_limit_is_accepted(client, path, settings):
    text = ("جمله کوتاه. " * settings.max_text_length)[: settings.max_text_length]
    assert post(client, path, text, "جمله کوتاه.").status_code == 200


def test_oversized_body_rejected_before_parsing(client):
    response = client.post(
        "/api/compare",
        content=b'{"text_a": "' + b"a" * 200_000 + b'", "text_b": "b"}',
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 413


@pytest.mark.parametrize(
    "payload",
    [{}, {"text_a": "متن"}, {"text_a": 1, "text_b": "متن"}, {"text_a": None, "text_b": "x"}],
)
def test_malformed_payload_is_422(client, payload):
    assert client.post("/api/compare", json=payload).status_code == 422


def test_non_json_body_is_422(client):
    response = client.post("/api/compare", content=b"not json", headers={"Content-Type": "application/json"})
    assert response.status_code == 422


# ── /compare ─────────────────────────────────────────────────────────────────
def test_compare_finds_shared_sentence(client):
    response = post(client, "/api/compare", TEXT_A, TEXT_B)
    assert response.status_code == 200
    matches = response.json()["matches"]
    assert len(matches) == 1
    match = matches[0]
    assert match["a_index"] == 0 and match["b_index"] == 0
    assert match["similarity"] == 1.0 and match["exact_similarity"] == 1.0
    assert match["text_a"] == match["text_b"]


def test_compare_completely_different_texts(client):
    response = post(client, "/api/compare", "گربه روی دیوار نشست.", "بازار سهام سقوط کرد.")
    assert response.status_code == 200
    assert response.json() == {"matches": []}


def test_compare_normalizes_arabic_characters_and_half_spaces(client):
    a = "كتاب‌هاي علمي مفيد هستند."
    b = "کتاب های علمی مفید هستند."
    match = post(client, "/api/compare", a, b).json()["matches"][0]
    assert match["similarity"] == 1.0
    assert match["text_a"] == match["text_b"]


def test_compare_encodes_once_per_request(client, fake_model):
    post(client, "/api/compare", TEXT_A, TEXT_B)
    assert len(fake_model.calls) == 1


# ── /report ──────────────────────────────────────────────────────────────────
def test_report_identical_texts(client):
    body = post(client, "/api/report", TEXT_A, TEXT_A).json()
    assert body["report"]["coverage_a"] == 1.0
    assert body["report"]["coverage_b"] == 1.0
    assert body["report"]["matched_count"] == 3
    assert body["report"]["avg_semantic_similarity"] == 1.0
    assert len(body["matches"]) == 3


def test_report_counts_every_copied_sentence_of_b(client):
    # Regression: B repeats A's only sentence; coverage_b used to be 0.5.
    body = post(client, "/api/report", "جمله مشترک است.", "جمله مشترک است. جمله مشترک است.").json()
    assert body["report"]["coverage_b"] == 1.0


def test_report_partial_overlap(client):
    report = post(client, "/api/report", TEXT_A, TEXT_B).json()["report"]
    assert report["matched_count"] == 1
    assert report["coverage_a"] == pytest.approx(1 / 3, abs=1e-3)
    assert report["coverage_b"] == 0.5


def test_report_completely_different(client):
    report = post(client, "/api/report", "گربه روی دیوار نشست.", "بازار سهام سقوط کرد.").json()["report"]
    assert report["matched_count"] == 0 and report["coverage_a"] == 0.0


# ── /diff-highlight ──────────────────────────────────────────────────────────
def test_diff_identical_texts(client):
    body = post(client, "/api/diff-highlight", TEXT_A, TEXT_A).json()
    assert body["semantic_diff"] == {"semantic_similarity": 1.0, "only_in_a": [], "only_in_b": []}
    assert body["highlight"]["completely_different"] is False
    assert "diff-replace" not in body["highlight"]["a_html"]


def test_diff_partial_overlap(client):
    body = post(client, "/api/diff-highlight", TEXT_A, TEXT_B).json()
    sem = body["semantic_diff"]
    assert sem["only_in_a"] == ["امروز هوا آفتابی است.", "کتاب روی میز است."]
    assert sem["only_in_b"] == ["قیمت نفت کاهش یافت."]
    assert 0 < sem["semantic_similarity"] < 1


def test_diff_completely_different(client):
    body = post(client, "/api/diff-highlight", "گربه روی دیوار نشست.", "بازار سهام سقوط کرد.").json()
    assert body["highlight"]["completely_different"] is True
    assert body["semantic_diff"]["semantic_similarity"] == 0.0


def test_diff_escapes_html_in_user_input(client):
    a = "<script>alert(1)</script> متن مشترک است."
    b = "<img src=x onerror=alert(1)> متن مشترک است."
    highlight = post(client, "/api/diff-highlight", a, b).json()["highlight"]
    for fragment in (highlight["a_html"], highlight["b_html"]):
        assert "<script" not in fragment and "<img" not in fragment


def test_diff_encodes_once_per_request(client, fake_model):
    post(client, "/api/diff-highlight", TEXT_A, TEXT_B)
    assert len(fake_model.calls) == 1


# ── Routing, health, CORS ────────────────────────────────────────────────────
@pytest.mark.parametrize("legacy", ["/compare", "/report", "/diff-highlight"])
def test_legacy_unprefixed_routes_still_work(client, legacy):
    assert post(client, legacy, TEXT_A, TEXT_B).json() == post(client, "/api" + legacy, TEXT_A, TEXT_B).json()


def test_legacy_routes_hidden_from_openapi(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert "/api/compare" in paths and "/compare" not in paths
    assert "/api/report" in paths and "/api/diff-highlight" in paths


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}
    assert client.get("/health").json() == {"status": "ok"}


def test_cors_allows_configured_origin_only(client):
    headers = {"Origin": "http://localhost:3002", "Access-Control-Request-Method": "POST"}
    allowed = client.options("/api/compare", headers=headers)
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:3002"

    headers["Origin"] = "http://evil.example"
    denied = client.options("/api/compare", headers=headers)
    assert "access-control-allow-origin" not in denied.headers


def test_get_on_post_endpoint_is_405(client):
    assert client.get("/api/compare").status_code == 405


# ── Concurrency ──────────────────────────────────────────────────────────────
def test_concurrent_requests_are_correct_and_bounded():
    model = FakeModel(delay=0.02)
    settings = Settings(max_concurrent_inference=2)
    with TestClient(create_app(settings=settings, model=model)) as client:
        words = ["کتاب", "دانشگاه", "مدرسه", "خانه", "بازار", "دریا", "کوه", "جنگل", "شهر", "روستا"]
        sentences = [f"جمله درباره {w} است." for w in words]
        jobs = [(path, s, s) for s in sentences for path in ENDPOINTS]
        with ThreadPoolExecutor(max_workers=12) as pool:
            responses = list(pool.map(lambda job: post(client, *job), jobs))
    assert all(r.status_code == 200 for r in responses)
    for (path, a, _), response in zip(jobs, responses, strict=True):
        if path == "/api/compare":
            assert response.json()["matches"][0]["text_a"] == a
    assert model.max_active <= 2


def test_lifespan_loads_model_when_not_injected(monkeypatch):
    import app as app_module

    loaded = []

    def fake_load(settings):
        loaded.append(settings.model_name)
        return FakeModel()

    monkeypatch.setattr(app_module, "load_model", fake_load)
    application = app_module.create_app(settings=Settings(model_name="dummy"))
    with TestClient(application) as client:
        assert post(client, "/api/compare", TEXT_A, TEXT_B).status_code == 200
    assert loaded == ["dummy"]
