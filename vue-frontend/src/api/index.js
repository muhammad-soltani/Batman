import axios from "axios";
import { API_BASE_URL, REQUEST_TIMEOUT_MS } from "../config";

const api = axios.create({ baseURL: API_BASE_URL, timeout: REQUEST_TIMEOUT_MS });

export const INVALID_RESPONSE = "INVALID_RESPONSE";

/**
 * Reject successful responses that are not JSON objects. If /api/* is not
 * routed to the backend, a static/SPA server answers with index.html and
 * status 200 — without this check the UI silently shows empty results.
 */
export function ensureJsonResponse(response) {
  const data = response?.data;
  if (data === null || typeof data !== "object") {
    const error = new Error("API returned a non-JSON response");
    error.code = INVALID_RESPONSE;
    error.response = response;
    throw error;
  }
  return response;
}

api.interceptors.response.use(ensureJsonResponse);

/**
 * Generic helper — all endpoints accept the same { text_a, text_b } payload.
 * @param {string} endpoint  e.g. "/api/compare"
 * @param {string} text_a
 * @param {string} text_b
 */
export const postTexts = (endpoint, text_a, text_b) =>
  api.post(endpoint, { text_a, text_b });

// Named convenience wrappers kept for clarity at the call-site
export const compareTexts = (text_a, text_b) =>
  postTexts("/api/compare", text_a, text_b);
export const getReport = (text_a, text_b) =>
  postTexts("/api/report", text_a, text_b);
export const getDiffHighlight = (text_a, text_b) =>
  postTexts("/api/diff-highlight", text_a, text_b);

const STATUS_MESSAGES = {
  400: "لطفاً در هر دو کادر، متن معتبر وارد کنید.",
  413: "متن واردشده بیش از حد طولانی است.",
  422: "درخواست ارسالی نامعتبر است.",
  429: "تعداد درخواست‌ها زیاد است؛ لطفاً کمی بعد دوباره تلاش کنید.",
  503: "سرویس هنوز آماده نیست (احتمالاً مدل در حال بارگذاری است)؛ لطفاً کمی بعد تلاش کنید.",
  504: "پاسخ سرور بیش از حد طول کشید؛ لطفاً متن کوتاه‌تری امتحان کنید.",
};

/**
 * Turn an axios error into a user-facing Persian message.
 * Never returns a non-string (FastAPI validation errors carry an array
 * `detail`, which used to be rendered as "[object Object]").
 */
export function errorMessage(error) {
  if (error?.code === "ECONNABORTED" || error?.code === "ETIMEDOUT") {
    return "زمان انتظار برای پاسخ سرور به پایان رسید؛ لطفاً متن کوتاه‌تری امتحان کنید.";
  }
  if (error?.code === INVALID_RESPONSE) {
    return "پاسخ نامعتبر از سرور: مسیر ‎/api‎ به Backend متصل نیست (تنظیمات proxy را بررسی کنید).";
  }
  const response = error?.response;
  if (!response) return "خطا در ارتباط با سرور";
  if (STATUS_MESSAGES[response.status]) return STATUS_MESSAGES[response.status];
  if (response.status >= 500) return "خطای داخلی سرور؛ لطفاً دوباره تلاش کنید.";
  const detail = response.data?.detail;
  return typeof detail === "string" && detail ? detail : "خطا در ارتباط با سرور";
}
