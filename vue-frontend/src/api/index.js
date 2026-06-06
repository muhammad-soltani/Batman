import axios from "axios";

const api = axios.create({ baseURL: "" });

/**
 * Generic helper — all endpoints accept the same { text_a, text_b } payload.
 * @param {string} endpoint  e.g. "/compare"
 * @param {string} text_a
 * @param {string} text_b
 */
export const postTexts = (endpoint, text_a, text_b) =>
  api.post(endpoint, { text_a, text_b });

// Named convenience wrappers kept for clarity at the call-site
export const compareTexts = (text_a, text_b) =>
  postTexts("/compare", text_a, text_b);
export const getReport = (text_a, text_b) =>
  postTexts("/report", text_a, text_b);
export const getDiffHighlight = (text_a, text_b) =>
  postTexts("/diff-highlight", text_a, text_b);
