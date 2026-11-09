# syntax=docker/dockerfile:1

# ── Stage 1: build ──────────────────────────────────────────────────────────
FROM node:22-alpine AS builder
WORKDIR /app

# Install deps — own layer so it's only re-run when the lockfile changes
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

# Build (keep VITE_MAX_TEXT_LENGTH in sync with the backend's MAX_TEXT_LENGTH)
ARG VITE_MAX_TEXT_LENGTH=50000
# Empty = same origin (/api/* routed by the server's nginx).
# e.g. http://localhost:8000 = browser calls the backend directly (local use).
ARG VITE_API_BASE_URL=
ENV VITE_MAX_TEXT_LENGTH=${VITE_MAX_TEXT_LENGTH} \
    VITE_API_BASE_URL=${VITE_API_BASE_URL}
COPY . .
RUN npm run build

# ── Stage 2: serve static files ─────────────────────────────────────────────
# Only serves the SPA. The server's own reverse proxy (nginx) routes /api/* to
# the backend — see "استقرار پشت Nginx سرور" in the README.
FROM node:22-alpine
RUN npm install -g serve@14.2.6 && npm cache clean --force
COPY --from=builder --chown=node:node /app/dist /app/dist
USER node
EXPOSE 3002
CMD ["serve", "-s", "/app/dist", "-l", "tcp://0.0.0.0:3002", "--no-clipboard"]
