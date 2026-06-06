# syntax=docker/dockerfile:1

# ── Stage 1: build ──────────────────────────────────────────────────────────
FROM node:22-alpine AS builder
WORKDIR /app

# Install deps — own layer so it's only re-run when package.json changes
COPY package.json package-lock.json ./
RUN npm ci

# Build
COPY . .
RUN npm run build

# ── Stage 2: serve static files ─────────────────────────────────────────────
FROM node:22-alpine
RUN npm install -g serve
COPY --from=builder /app/dist /app/dist
EXPOSE 3002
CMD ["serve", "-s", "/app/dist", "-l", "3002"]
