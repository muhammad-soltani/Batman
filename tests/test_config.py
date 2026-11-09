import pytest

from config import DEFAULT_CORS_ORIGINS, DEFAULT_MAX_TEXT_LENGTH, Settings

ENV_VARS = [
    "MODEL_NAME", "DEVICE", "SIMILARITY_THRESHOLD", "LEXICAL_MATCH_THRESHOLD", "DIFF_SEMANTIC_THRESHOLD",
    "DIFF_TEXT_OVERLAP_THRESHOLD", "MAX_TEXT_LENGTH", "MAX_CONCURRENT_INFERENCE", "CORS_ORIGINS",
]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)


def test_defaults():
    s = Settings.from_env()
    assert s.model_name == "paraphrase-multilingual-mpnet-base-v2"
    assert s.device is None
    assert s.similarity_threshold == 0.7
    assert s.lexical_match_threshold == 0.8
    assert s.max_text_length == DEFAULT_MAX_TEXT_LENGTH
    assert s.cors_origins == DEFAULT_CORS_ORIGINS


def test_overrides(monkeypatch):
    monkeypatch.setenv("SIMILARITY_THRESHOLD", "0.6")
    monkeypatch.setenv("MAX_TEXT_LENGTH", "1000")
    monkeypatch.setenv("DEVICE", "cpu")
    monkeypatch.setenv("CORS_ORIGINS", " https://a.example , https://b.example ,")
    s = Settings.from_env()
    assert s.similarity_threshold == 0.6
    assert s.max_text_length == 1000
    assert s.device == "cpu"
    assert s.cors_origins == ("https://a.example", "https://b.example")


def test_blank_values_fall_back_to_defaults(monkeypatch):
    monkeypatch.setenv("MAX_TEXT_LENGTH", "  ")
    assert Settings.from_env().max_text_length == DEFAULT_MAX_TEXT_LENGTH


@pytest.mark.parametrize(
    "name, value",
    [
        ("SIMILARITY_THRESHOLD", "abc"),
        ("SIMILARITY_THRESHOLD", "1.5"),
        ("MAX_TEXT_LENGTH", "0"),
        ("MAX_TEXT_LENGTH", "-5"),
        ("MAX_CONCURRENT_INFERENCE", "two"),
    ],
)
def test_invalid_values_fail_fast(monkeypatch, name, value):
    monkeypatch.setenv(name, value)
    with pytest.raises(ValueError, match=name):
        Settings.from_env()
