/** Clamp a similarity/coverage score into [0, 1] (cosine can be negative). */
export function clampUnit(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return 0;
  return Math.min(1, Math.max(0, n));
}

/** Format a [0, 1] score as a percentage string with one decimal, e.g. "87.5". */
export function percent(value) {
  return (clampUnit(value) * 100).toFixed(1);
}

/** CSS width for a progress bar representing a [0, 1] score. */
export function barWidth(value) {
  return `${clampUnit(value) * 100}%`;
}
