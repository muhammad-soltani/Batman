FROM python:3.13-slim

WORKDIR /app

# Build-time proxy — available to all RUN steps, not stored in the final image
ARG HTTP_PROXY=http://127.0.0.1:9815
ARG HTTPS_PROXY=http://127.0.0.1:9815

ENV CI=true
ENV PIP_NO_IPV6=1 \
    HF_HOME=/cache/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/cache/sentence_transformers

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
