# syntax=docker/dockerfile:1
FROM python:3.10-slim

WORKDIR /app
ENV PIP_NO_IPV6=1
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && python -c "\
    from sentence_transformers import SentenceTransformer; \
    SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
