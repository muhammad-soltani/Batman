/**
 * Maximum characters per text. Must match the backend's MAX_TEXT_LENGTH
 * (default 50000); override at build time with VITE_MAX_TEXT_LENGTH.
 */
const configured = Number.parseInt(import.meta.env.VITE_MAX_TEXT_LENGTH ?? "", 10);
export const MAX_TEXT_LENGTH = Number.isFinite(configured) && configured > 0 ? configured : 50000;

/**
 * Base URL of the backend API. Empty (default) = same origin: a reverse proxy
 * (the server's nginx, or Vite's dev proxy) routes /api/* to the backend.
 * Set VITE_API_BASE_URL (e.g. "http://localhost:8000") at build time to call
 * the backend directly instead; it must then be allowed in CORS_ORIGINS.
 */
export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/+$/, "");

/** Request timeout. Long texts on a CPU-only server can take a while. */
export const REQUEST_TIMEOUT_MS = 5 * 60 * 1000;
