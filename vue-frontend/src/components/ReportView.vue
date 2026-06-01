<template>
  <div class="card">
    <div class="card-title">
      <span class="card-title-icon">📊</span>
      گزارش سرقت ادبی
    </div>

    <div class="inputs-grid">
      <div class="input-wrap">
        <label class="input-label" for="repA">📄 متن اول</label>
        <textarea
          id="repA"
          v-model="textA"
          placeholder="متن اول را اینجا وارد کنید..."
          rows="8"
        />
      </div>
      <div class="input-wrap">
        <label class="input-label" for="repB">📄 متن دوم</label>
        <textarea
          id="repB"
          v-model="textB"
          placeholder="متن دوم را اینجا وارد کنید..."
          rows="8"
        />
      </div>
    </div>

    <div class="action-bar">
      <button class="btn-primary" :disabled="loading" @click="fetchReport">
        <span v-if="loading" class="spinner"></span>
        <span v-else>📊</span>
        {{ loading ? "در حال پردازش..." : "دریافت گزارش" }}
      </button>
    </div>

    <div v-if="error" class="alert-error">⚠️ {{ error }}</div>

    <template v-if="report">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ report.matched_count }}</div>
          <div class="stat-label">تعداد جملات تطبیق‌یافته</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" :style="coverageColor(report.coverage_a)">
            {{ (report.coverage_a * 100).toFixed(1) }}%
          </div>
          <div class="stat-label">پوشش متن اول</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" :style="coverageColor(report.coverage_b)">
            {{ (report.coverage_b * 100).toFixed(1) }}%
          </div>
          <div class="stat-label">پوشش متن دوم</div>
        </div>
        <div class="stat-card">
          <div
            class="stat-value"
            :style="coverageColor(report.avg_semantic_similarity)"
          >
            {{ (report.avg_semantic_similarity * 100).toFixed(1) }}%
          </div>
          <div class="stat-label">میانگین شباهت معنایی</div>
        </div>
        <div class="stat-card">
          <div
            class="stat-value"
            :style="coverageColor(report.avg_exact_similarity)"
          >
            {{ (report.avg_exact_similarity * 100).toFixed(1) }}%
          </div>
          <div class="stat-label">میانگین شباهت دقیق</div>
        </div>
      </div>

      <div class="plagiarism-verdict" :class="verdictClass(report.coverage_a)">
        <span class="verdict-icon">{{ verdictIcon(report.coverage_a) }}</span>
        <div>
          <div class="verdict-title">{{ verdictText(report.coverage_a) }}</div>
          <div class="verdict-sub">
            بر اساس پوشش {{ (report.coverage_a * 100).toFixed(1) }}٪ از متن اول
          </div>
        </div>
      </div>
    </template>

    <div v-else-if="!loading && !error" class="empty-state">
      <div class="empty-icon">📊</div>
      <div>دو متن را وارد کرده و گزارش را دریافت کنید</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { getReport } from "../api";

const textA = ref("");
const textB = ref("");
const report = ref(null);
const loading = ref(false);
const error = ref("");

async function fetchReport() {
  error.value = "";
  report.value = null;
  loading.value = true;
  try {
    const res = await getReport(textA.value, textB.value);
    report.value = res.data.report;
  } catch (e) {
    error.value = e.response?.data?.detail || "خطا در ارتباط با سرور";
  } finally {
    loading.value = false;
  }
}

function coverageColor(val) {
  if (val >= 0.7) return "color:#ef4444";
  if (val >= 0.4) return "color:#f59e0b";
  return "color:#10b981";
}

function verdictClass(val) {
  if (val >= 0.7) return "verdict-high";
  if (val >= 0.4) return "verdict-medium";
  return "verdict-low";
}

function verdictIcon(val) {
  if (val >= 0.7) return "🚨";
  if (val >= 0.4) return "⚠️";
  return "✅";
}

function verdictText(val) {
  if (val >= 0.7) return "احتمال بالای سرقت ادبی";
  if (val >= 0.4) return "شباهت متوسط — بررسی بیشتر توصیه می‌شود";
  return "متون مشابهت قابل‌توجهی ندارند";
}
</script>

<style scoped>
.plagiarism-verdict {
  display: flex;
  align-items: center;
  gap: 16px;
  border-radius: 12px;
  padding: 18px 22px;
  border: 2px solid;
  margin-top: 8px;
}

.verdict-high {
  background: #fef2f2;
  border-color: #fecaca;
}
.verdict-medium {
  background: #fffbeb;
  border-color: #fde68a;
}
.verdict-low {
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.verdict-icon {
  font-size: 2rem;
}

.verdict-title {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 4px;
}

.verdict-high .verdict-title {
  color: #b91c1c;
}
.verdict-medium .verdict-title {
  color: #b45309;
}
.verdict-low .verdict-title {
  color: #15803d;
}

.verdict-sub {
  font-size: 0.82rem;
  color: var(--text-muted);
}
</style>
