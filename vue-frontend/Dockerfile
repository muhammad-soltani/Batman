# syntax=docker/dockerfile:1

# ── Stage 1: build ──────────────────────────────────────────────────────────
FROM node:22-alpine AS builder
WORKDIR /app

# Enable pnpm via corepack (matches the pnpm-lock.yaml used in development)
RUN corepack enable && corepack prepare pnpm@latest --activate

# Install deps — own layer so it's only re-run when lockfile changes
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile --ignore-scripts

# Build
COPY . .
RUN pnpm run build

# ── Stage 2: serve static files ─────────────────────────────────────────────
FROM node:22-alpine
RUN npm install -g serve
COPY --from=builder /app/dist /app/dist
EXPOSE 3002
CMD ["serve", "-s", "/app/dist", "-l", "3002"]
