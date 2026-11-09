# syntax=docker/dockerfile:1
FROM python:3.13-slim

# Build-time proxy: HTTP_PROXY / HTTPS_PROXY / NO_PROXY are predefined Docker
# build args. Pass them with --build-arg (or via docker-compose, which reads
# them from the environment / .env). They are available to RUN steps but are
# not stored in the image or its history.

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HF_HOME=/opt/hf-cache \
    SENTENCE_TRANSFORMERS_HOME=/opt/hf-cache/sentence_transformers

WORKDIR /app

COPY requirements.txt ./
# Install CPU-only PyTorch first to avoid downloading the ~2GB CUDA binaries
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install torch==2.12.0 --index-url https://download.pytorch.org/whl/cpu && \
    pip install -r requirements.txt

# Bake the model into the image: startup does not depend on network access and
# this layer stays cached until requirements or the model change.
ARG MODEL_NAME=paraphrase-multilingual-mpnet-base-v2
ENV MODEL_NAME=${MODEL_NAME}
RUN python -c "import os; from sentence_transformers import SentenceTransformer; SentenceTransformer(os.environ['MODEL_NAME'], device='cpu')"

RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin app && \
    chown -R app:app /opt/hf-cache

# Source files only (see .dockerignore allow-list)
COPY --chown=app:app . .

# Runtime never reaches the Hugging Face Hub; the model comes from the image.
ENV HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1

USER app
EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=5s --start-period=120s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
