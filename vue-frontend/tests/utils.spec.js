import { describe, expect, it } from "vitest";
import { ensureJsonResponse, errorMessage, INVALID_RESPONSE } from "../src/api";
import { barWidth, clampUnit, percent } from "../src/utils/format";

describe("format helpers", () => {
  it("clamps scores into [0, 1]", () => {
    expect(clampUnit(0.42)).toBe(0.42);
    expect(clampUnit(-0.12)).toBe(0);
    expect(clampUnit(1.0000001)).toBe(1);
    expect(clampUnit(undefined)).toBe(0);
    expect(clampUnit(NaN)).toBe(0);
  });

  it("formats percentages and bar widths", () => {
    expect(percent(0.8766)).toBe("87.7");
    expect(percent(-0.124)).toBe("0.0");
    expect(barWidth(0.5)).toBe("50%");
    expect(barWidth(2)).toBe("100%");
  });
});

describe("errorMessage", () => {
  const httpError = (status, data) => ({ response: { status, data } });

  it("handles network errors and timeouts", () => {
    expect(errorMessage(new Error("Network Error"))).toBe("خطا در ارتباط با سرور");
    expect(errorMessage({ code: "ECONNABORTED" })).toMatch(/زمان انتظار/);
  });

  it("maps known statuses to Persian messages", () => {
    expect(errorMessage(httpError(400, { detail: "Both text_a and text_b are required." }))).toMatch(/متن معتبر/);
    expect(errorMessage(httpError(413, { detail: "too long" }))).toMatch(/طولانی/);
    expect(errorMessage(httpError(503, {}))).toMatch(/آماده نیست/);
    expect(errorMessage(httpError(500, {}))).toMatch(/خطای داخلی/);
  });

  it("never returns a non-string for array validation details", () => {
    const msg = errorMessage(httpError(418, { detail: [{ msg: "x", loc: ["body"] }] }));
    expect(typeof msg).toBe("string");
    expect(msg).not.toContain("[object Object]");
  });

  it("explains an HTML/non-JSON response (API not routed to the backend)", () => {
    expect(errorMessage({ code: INVALID_RESPONSE })).toMatch(/Backend/);
  });

  it("falls back to a string detail for unmapped statuses", () => {
    expect(errorMessage(httpError(409, { detail: "conflict" }))).toBe("conflict");
  });
});

describe("ensureJsonResponse", () => {
  it("passes JSON object responses through", () => {
    const response = { status: 200, data: { matches: [] } };
    expect(ensureJsonResponse(response)).toBe(response);
  });

  it.each([["<!doctype html><div id=app></div>"], [""], [null]])(
    "rejects non-JSON body %j served with status 200",
    (data) => {
      expect(() => ensureJsonResponse({ status: 200, data })).toThrow(
        expect.objectContaining({ code: INVALID_RESPONSE }),
      );
    },
  );
});
