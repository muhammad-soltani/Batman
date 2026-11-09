import { beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";

vi.mock("../src/api", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    compareTexts: vi.fn(),
    getReport: vi.fn(),
    getDiffHighlight: vi.fn(),
  };
});

import * as api from "../src/api";
import App from "../src/App.vue";
import CompareView from "../src/components/CompareView.vue";
import DiffView from "../src/components/DiffView.vue";
import ReportView from "../src/components/ReportView.vue";
import TextInputsGrid from "../src/components/TextInputsGrid.vue";

async function fillAndSubmit(wrapper, a = "متن اول.", b = "متن دوم.") {
  const areas = wrapper.findAll("textarea");
  await areas[0].setValue(a);
  await areas[1].setValue(b);
  await wrapper.find("button.btn-primary").trigger("click");
  await flushPromises();
}

beforeEach(() => {
  vi.mocked(api.compareTexts).mockReset();
  vi.mocked(api.getReport).mockReset();
  vi.mocked(api.getDiffHighlight).mockReset();
});

describe("TextInputsGrid", () => {
  it("emits v-model updates and flags text over the limit", async () => {
    const wrapper = mount(TextInputsGrid, { props: { modelA: "", modelB: "", maxLength: 5 } });
    await wrapper.findAll("textarea")[0].setValue("سلام");
    expect(wrapper.emitted("update:modelA")[0]).toEqual(["سلام"]);

    await wrapper.setProps({ modelB: "خیلی طولانی" });
    const areaB = wrapper.findAll("textarea")[1];
    expect(areaB.classes()).toContain("textarea-over");
    expect(areaB.attributes("aria-invalid")).toBe("true");
    expect(wrapper.findAll(".input-counter")[1].classes()).toContain("input-counter-over");
  });

  it("links labels to textareas", () => {
    const wrapper = mount(TextInputsGrid, { props: { idA: "x1", idB: "x2" } });
    expect(wrapper.find('label[for="x1"]').exists()).toBe(true);
    expect(wrapper.find("textarea#x2").exists()).toBe(true);
  });
});

describe("CompareView", () => {
  it("shows the initial empty state", () => {
    const wrapper = mount(CompareView);
    expect(wrapper.find(".empty-state").text()).toContain("دو متن را وارد کرده");
  });

  it("validates empty input on the client", async () => {
    const wrapper = mount(CompareView);
    await wrapper.find("button.btn-primary").trigger("click");
    expect(api.compareTexts).not.toHaveBeenCalled();
    expect(wrapper.find(".alert-error").text()).toContain("هر دو متن");
  });

  it("renders matches with clamped percentages", async () => {
    vi.mocked(api.compareTexts).mockResolvedValue({
      data: {
        matches: [
          { a_index: 0, b_index: 1, similarity: 0.95, exact_similarity: 0.5, text_a: "الف", text_b: "ب" },
          { a_index: 2, b_index: 0, similarity: 0.72, exact_similarity: null, text_a: "<b>ج</b>", text_b: "د" },
        ],
      },
    });
    const wrapper = mount(CompareView);
    await fillAndSubmit(wrapper);

    const rows = wrapper.findAll("tbody tr");
    expect(rows).toHaveLength(2);
    expect(rows[0].classes()).toContain("high");
    expect(rows[0].text()).toContain("95.0%");
    expect(rows[1].classes()).toContain("medium");
    expect(rows[1].text()).toContain("—"); // missing exact similarity
    // Text is rendered as text, not HTML.
    expect(rows[1].find("b").exists()).toBe(false);
    expect(rows[1].text()).toContain("<b>ج</b>");
    expect(wrapper.find(".badge").text()).toContain("2");
  });

  it("shows a dedicated message when no sentence matches", async () => {
    vi.mocked(api.compareTexts).mockResolvedValue({ data: { matches: [] } });
    const wrapper = mount(CompareView);
    await fillAndSubmit(wrapper);
    expect(wrapper.find("table").exists()).toBe(false);
    expect(wrapper.find(".empty-state").text()).toContain("هیچ جمله‌ی مشابهی");
  });

  it("shows server errors as text", async () => {
    vi.mocked(api.compareTexts).mockRejectedValue({ response: { status: 500, data: {} } });
    const wrapper = mount(CompareView);
    await fillAndSubmit(wrapper);
    expect(wrapper.find(".alert-error").text()).toContain("خطای داخلی");
    expect(wrapper.find("button.btn-primary").attributes("disabled")).toBeUndefined();
  });

  it("disables the button and shows a spinner while loading", async () => {
    let resolve;
    vi.mocked(api.compareTexts).mockReturnValue(new Promise((r) => (resolve = r)));
    const wrapper = mount(CompareView);
    const areas = wrapper.findAll("textarea");
    await areas[0].setValue("الف");
    await areas[1].setValue("ب");
    await wrapper.find("button.btn-primary").trigger("click");
    expect(wrapper.find("button.btn-primary").attributes("disabled")).toBeDefined();
    expect(wrapper.find(".spinner").exists()).toBe(true);
    resolve({ data: { matches: [] } });
    await flushPromises();
    expect(wrapper.find(".spinner").exists()).toBe(false);
  });
});

describe("ReportView", () => {
  const report = (coverage_a) => ({
    data: {
      report: {
        matched_count: 3,
        coverage_a,
        coverage_b: 0.5,
        avg_semantic_similarity: 0.9,
        avg_exact_similarity: 0.4,
      },
      matches: [],
    },
  });

  it.each([
    [0.8, "verdict-high", "احتمال بالای سرقت ادبی"],
    [0.5, "verdict-medium", "شباهت متوسط"],
    [0.1, "verdict-low", "مشابهت قابل‌توجهی ندارند"],
  ])("coverage %s → %s", async (coverage, cls, text) => {
    vi.mocked(api.getReport).mockResolvedValue(report(coverage));
    const wrapper = mount(ReportView);
    await fillAndSubmit(wrapper);
    const verdict = wrapper.find(".plagiarism-verdict");
    expect(verdict.classes()).toContain(cls);
    expect(verdict.text()).toContain(text);
    expect(wrapper.findAll(".stat-card")).toHaveLength(5);
  });
});

describe("DiffView", () => {
  const diff = (overrides = {}) => ({
    data: {
      semantic_diff: { semantic_similarity: 0.8, only_in_a: ["جمله الف"], only_in_b: [], ...overrides.semantic },
      highlight: {
        a_html: '<span class="diff-equal">مشترک</span> <span class="diff-del">حذف</span>',
        b_html: '<span class="diff-equal">مشترک</span>',
        completely_different: false,
        ...overrides.highlight,
      },
    },
  });

  it("renders semantic lists and highlighted html", async () => {
    vi.mocked(api.getDiffHighlight).mockResolvedValue(diff());
    const wrapper = mount(DiffView);
    await fillAndSubmit(wrapper);
    expect(wrapper.find(".diff-meta-score").text()).toBe("80.0%");
    const lists = wrapper.findAll(".diff-list");
    expect(lists[0].text()).toContain("جمله الف");
    expect(lists[1].text()).toContain("موردی یافت نشد");
    expect(wrapper.findAll(".highlight-box")[0].find(".diff-del").text()).toBe("حذف");
    expect(wrapper.find(".alert-completely-different").exists()).toBe(false);
  });

  it("shows the completely-different notice and never a negative score", async () => {
    vi.mocked(api.getDiffHighlight).mockResolvedValue(
      diff({ semantic: { semantic_similarity: -0.12 }, highlight: { completely_different: true } }),
    );
    const wrapper = mount(DiffView);
    await fillAndSubmit(wrapper);
    expect(wrapper.find(".alert-completely-different").exists()).toBe(true);
    expect(wrapper.find(".diff-meta-score").text()).toBe("0.0%");
  });
});

describe("App", () => {
  it("switches tabs and keeps each tab's state (keep-alive)", async () => {
    const wrapper = mount(App);
    const tabs = wrapper.findAll(".tab-btn");
    expect(tabs).toHaveLength(3);
    expect(tabs[0].attributes("aria-selected")).toBe("true");

    await wrapper.find("textarea").setValue("متن نگه‌داشته‌شده");
    await tabs[1].trigger("click");
    await flushPromises();
    expect(wrapper.find(".card-title").text()).toBe("گزارش سرقت ادبی");
    expect(tabs[1].attributes("aria-selected")).toBe("true");

    await tabs[0].trigger("click");
    await flushPromises();
    expect(wrapper.find("textarea").element.value).toBe("متن نگه‌داشته‌شده");
  });

  it("does not duplicate the #app id", () => {
    const wrapper = mount(App);
    expect(wrapper.find("#app").exists()).toBe(false);
    expect(wrapper.classes()).toContain("app-shell");
  });
});
