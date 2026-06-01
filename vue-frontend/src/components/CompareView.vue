<template>
  <div class="card">
    <div class="card-title">
      <span class="card-title-icon">⚖️</span>
      مقایسه جملات دو متن
    </div>

    <div class="inputs-grid">
      <div class="input-wrap">
        <label class="input-label" for="textA">📄 متن اول</label>
        <textarea
          id="textA"
          v-model="textA"
          placeholder="متن اول را اینجا وارد کنید..."
          rows="8"
        />
      </div>
      <div class="input-wrap">
        <label class="input-label" for="textB">📄 متن دوم</label>
        <textarea
          id="textB"
          v-model="textB"
          placeholder="متن دوم را اینجا وارد کنید..."
          rows="8"
        />
      </div>
    </div>

    <div class="action-bar">
      <button class="btn-primary" :disabled="loading" @click="compare">
        <span v-if="loading" class="spinner"></span>
        <span v-else>🚀</span>
        {{ loading ? "در حال پردازش..." : "شروع مقایسه" }}
      </button>
      <span v-if="matches.length" class="badge"
        >{{ matches.length }} تطبیق یافت شد</span
      >
    </div>

    <div v-if="error" class="alert-error">⚠️ {{ error }}</div>

    <template v-if="matches.length">
      <div class="results-header">
        <span class="results-title">نتایج مقایسه</span>
        <div class="legend">
          <span class="legend-item"
            ><span
              class="legend-dot"
              style="background: #dcfce7; border: 1.5px solid #10b981"
            ></span>
            بالا (≥۹۰٪)</span
          >
          <span class="legend-item"
            ><span
              class="legend-dot"
              style="background: #fef9c3; border: 1.5px solid #f59e0b"
            ></span>
            متوسط (≥۷۰٪)</span
          >
          <span class="legend-item"
            ><span
              class="legend-dot"
              style="background: #ffe4e6; border: 1.5px solid #ef4444"
            ></span>
            پایین</span
          >
        </div>
      </div>
      <div class="results-table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>جمله از متن اول</th>
              <th>جمله از متن دوم</th>
              <th>معنایی</th>
              <th>دقیق</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(m, i) in matches"
              :key="i"
              :class="scoreClass(m.similarity)"
            >
              <td>
                <span style="color: var(--text-muted); font-size: 0.82rem">{{
                  i + 1
                }}</span>
              </td>
              <td>{{ m.text_a }}</td>
              <td>{{ m.text_b }}</td>
              <td>
                <span
                  :class="['score-pill', 'score-' + scoreClass(m.similarity)]"
                >
                  {{ (m.similarity * 100).toFixed(1) }}%
                </span>
              </td>
              <td>
                <span
                  v-if="m.exact_similarity != null"
                  :class="[
                    'score-pill',
                    'score-' + scoreClass(m.exact_similarity),
                  ]"
                >
                  {{ (m.exact_similarity * 100).toFixed(1) }}%
                </span>
                <span v-else style="color: var(--text-muted)">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <div v-else-if="!loading && !error" class="empty-state">
      <div class="empty-icon">📝</div>
      <div>دو متن را وارد کرده و دکمه مقایسه را بزنید</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { compareTexts } from "../api";

const textA = ref("");
const textB = ref("");
const matches = ref([]);
const loading = ref(false);
const error = ref("");

async function compare() {
  error.value = "";
  matches.value = [];
  loading.value = true;
  try {
    const res = await compareTexts(textA.value, textB.value);
    matches.value = res.data.matches;
  } catch (e) {
    error.value = e.response?.data?.detail || "خطا در ارتباط با سرور";
  } finally {
    loading.value = false;
  }
}

function scoreClass(score) {
  if (score >= 0.9) return "high";
  if (score >= 0.7) return "medium";
  return "low";
}
</script>
