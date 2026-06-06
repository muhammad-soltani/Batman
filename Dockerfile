# syntax=docker/dockerfile:1
FROM python:3.10-slim

WORKDIR /app

# ── Environment ──────────────────────────────────────────────────────────────
# Silence pip IPv6 warnings
ENV PIP_NO_IPV6=1
# Point HuggingFace / Sentence-Transformers cache to a volume-mountable path.
# docker-compose mounts a named volume here so the model survives rebuilds.
ENV HF_HOME=/cache/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/cache/sentence_transformers

# ── System deps (curl needed for the healthcheck) ────────────────────────────
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# ── Python deps ──────────────────────────────────────────────────────────────
# Copied before source so Docker can cache this layer independently.
# Layer is only re-built when requirements.txt changes.
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Application source ───────────────────────────────────────────────────────
COPY . .

EXPOSE 8000

# Model is downloaded on first startup into the mounted volume (/cache).
# Every subsequent start — including after a full image rebuild — uses the
# cached files and skips the download entirely.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
