<script setup>
import { getReport } from "../api";
import { useTextSubmit } from "../composables/useTextSubmit";
import TextInputsGrid from "./TextInputsGrid.vue";
import { barWidth, percent } from "../utils/format";

const {
  textA,
  textB,
  result: report,
  loading,
  error,
  submit: fetchReport,
} = useTextSubmit(getReport, (data) => data.report);

function statColor(val) {
  if (val >= 0.7) return "#fca5a5";
  if (val >= 0.4) return "#fde047";
  return "#86efac";
}

function verdictClass(val) {
  if (val >= 0.7) return "verdict-high";
  if (val >= 0.4) return "verdict-medium";
  return "verdict-low";
}

function verdictText(val) {
  if (val >= 0.7) return "احتمال بالای سرقت ادبی";
  if (val >= 0.4) return "شباهت متوسط — بررسی بیشتر توصیه می‌شود";
  return "متون مشابهت قابل‌توجهی ندارند";
}
</script>

<template>
  <div class="card">
    <div class="card-header">
      <div class="card-title">گزارش سرقت ادبی</div>
    </div>

    <TextInputsGrid
      v-model:modelA="textA"
      v-model:modelB="textB"
      id-a="repA"
      id-b="repB"
    />

    <div class="action-bar">
      <button class="btn-primary" :disabled="loading" @click="fetchReport">
        <span v-if="loading" class="spinner"></span>
        {{ loading ? "در حال پردازش..." : "دریافت گزارش" }}
      </button>
    </div>

    <div v-if="error" class="alert-error">{{ error }}</div>

    <template v-if="report">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ report.matched_count }}</div>
          <div class="stat-label">جملات تطبیق‌یافته</div>
        </div>
        <div class="stat-card">
          <div
            class="stat-value"
            :style="{ color: statColor(report.coverage_a) }"
          >
            {{ percent(report.coverage_a) }}%
          </div>
          <div class="stat-label">پوشش متن اول</div>
          <div class="stat-bar">
            <div
              class="stat-bar-fill"
              :style="{
                width: barWidth(report.coverage_a),
                background: statColor(report.coverage_a),
              }"
            ></div>
          </div>
        </div>
        <div class="stat-card">
          <div
            class="stat-value"
            :style="{ color: statColor(report.coverage_b) }"
          >
            {{ percent(report.coverage_b) }}%
          </div>
          <div class="stat-label">پوشش متن دوم</div>
          <div class="stat-bar">
            <div
              class="stat-bar-fill"
              :style="{
                width: barWidth(report.coverage_b),
                background: statColor(report.coverage_b),
              }"
            ></div>
          </div>
        </div>
        <div class="stat-card">
          <div
            class="stat-value"
            :style="{ color: statColor(report.avg_semantic_similarity) }"
          >
            {{ percent(report.avg_semantic_similarity) }}%
          </div>
          <div class="stat-label">میانگین شباهت معنایی</div>
          <div class="stat-bar">
            <div
              class="stat-bar-fill"
              :style="{
                width: barWidth(report.avg_semantic_similarity),
                background: statColor(report.avg_semantic_similarity),
              }"
            ></div>
          </div>
        </div>
        <div class="stat-card">
          <div
            class="stat-value"
            :style="{ color: statColor(report.avg_exact_similarity) }"
          >
            {{ percent(report.avg_exact_similarity) }}%
          </div>
          <div class="stat-label">میانگین شباهت لفظی</div>
          <div class="stat-bar">
            <div
              class="stat-bar-fill"
              :style="{
                width: barWidth(report.avg_exact_similarity),
                background: statColor(report.avg_exact_similarity),
              }"
            ></div>
          </div>
        </div>
      </div>

      <div class="plagiarism-verdict" :class="verdictClass(report.coverage_a)">
        <div class="verdict-title">{{ verdictText(report.coverage_a) }}</div>
        <div class="verdict-sub">
          بر اساس پوشش {{ percent(report.coverage_a) }}٪ از متن اول
        </div>
      </div>
    </template>

    <div v-else-if="!loading && !error" class="empty-state">
      دو متن را وارد کرده و گزارش را دریافت کنید
    </div>
  </div>
</template>
