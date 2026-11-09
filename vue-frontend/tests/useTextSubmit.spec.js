import { describe, expect, it, vi } from "vitest";
import { useTextSubmit } from "../src/composables/useTextSubmit";
import { MAX_TEXT_LENGTH } from "../src/config";

function deferred() {
  let resolve, reject;
  const promise = new Promise((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

describe("useTextSubmit", () => {
  it("rejects empty or whitespace-only input without calling the API", async () => {
    const api = vi.fn();
    const s = useTextSubmit(api);
    s.textA.value = "   ";
    s.textB.value = "متن";
    await s.submit();
    expect(api).not.toHaveBeenCalled();
    expect(s.error.value).toBe("لطفاً هر دو متن را وارد کنید.");
  });

  it("rejects text longer than the limit without calling the API", async () => {
    const api = vi.fn();
    const s = useTextSubmit(api);
    s.textA.value = "ا".repeat(MAX_TEXT_LENGTH + 1);
    s.textB.value = "متن";
    await s.submit();
    expect(api).not.toHaveBeenCalled();
    expect(s.error.value).toMatch(/حداکثر/);
  });

  it("toggles loading and stores the transformed result", async () => {
    const d = deferred();
    const api = vi.fn(() => d.promise);
    const s = useTextSubmit(api, (data) => data.matches);
    s.textA.value = "الف";
    s.textB.value = "ب";
    const pending = s.submit();
    expect(s.loading.value).toBe(true);
    expect(api).toHaveBeenCalledWith("الف", "ب");
    d.resolve({ data: { matches: [1, 2] } });
    await pending;
    expect(s.loading.value).toBe(false);
    expect(s.result.value).toEqual([1, 2]);
    expect(s.error.value).toBe("");
  });

  it("ignores a second submit while a request is in flight", async () => {
    const first = deferred();
    const api = vi.fn(() => first.promise);
    const s = useTextSubmit(api);
    s.textA.value = "الف";
    s.textB.value = "ب";
    const p1 = s.submit();
    await s.submit();
    expect(api).toHaveBeenCalledTimes(1);
    first.resolve({ data: "first" });
    await p1;
    expect(s.result.value).toBe("first");
  });

  it("maps API errors to a message and clears the previous result", async () => {
    const api = vi
      .fn()
      .mockResolvedValueOnce({ data: "ok" })
      .mockRejectedValueOnce({ response: { status: 413, data: { detail: "too long" } } });
    const s = useTextSubmit(api);
    s.textA.value = "الف";
    s.textB.value = "ب";
    await s.submit();
    expect(s.result.value).toBe("ok");
    await s.submit();
    expect(s.result.value).toBeNull();
    expect(s.error.value).toMatch(/طولانی/);
    expect(s.loading.value).toBe(false);
  });
});
