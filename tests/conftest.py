import hashlib
import os
import re
import sys
import threading
import time

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app  # noqa: E402
from config import Settings  # noqa: E402

_WORD = re.compile(r"\w+")


class FakeModel:
    """Deterministic stand-in for SentenceTransformer.

    Embeds a sentence as a hashed bag of words, so identical sentences get
    identical vectors, sentences sharing words are similar and sentences with
    no words in common are orthogonal (cosine 0). It also records how it is
    called, so tests can assert on batching and concurrency.
    """

    def __init__(self, dim: int = 512, delay: float = 0.0):
        self.dim = dim
        self.delay = delay
        self.calls = []
        self._lock = threading.Lock()
        self.active = 0
        self.max_active = 0

    def _vector(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dim, dtype=np.float32)
        for word in _WORD.findall(text.lower()):
            digest = hashlib.md5(word.encode("utf-8")).digest()
            vec[int.from_bytes(digest[:4], "little") % self.dim] += 1.0
        return vec

    def encode(self, texts, convert_to_numpy=True, show_progress_bar=False, **kwargs):
        with self._lock:
            self.calls.append(list(texts))
            self.active += 1
            self.max_active = max(self.max_active, self.active)
        try:
            if self.delay:
                time.sleep(self.delay)
            return np.stack([self._vector(t) for t in texts])
        finally:
            with self._lock:
                self.active -= 1


@pytest.fixture
def fake_model():
    return FakeModel()


@pytest.fixture
def settings():
    return Settings(max_text_length=2_000, cors_origins=("http://localhost:3002",))


@pytest.fixture
def client(fake_model, settings):
    from fastapi.testclient import TestClient

    app = create_app(settings=settings, model=fake_model)
    with TestClient(app) as test_client:
        yield test_client
