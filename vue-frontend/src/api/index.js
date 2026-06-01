import axios from "axios";

const api = axios.create({ baseURL: "" });

export const compareTexts = (text_a, text_b) =>
  api.post("/compare", { text_a, text_b });

export const getReport = (text_a, text_b) =>
  api.post("/report", { text_a, text_b });

export const getDiffHighlight = (text_a, text_b) =>
  api.post("/diff-highlight", { text_a, text_b });
