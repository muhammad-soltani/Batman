<script setup>
import { computed } from "vue";
import { compareTexts } from "../api";
import { useTextSubmit } from "../composables/useTextSubmit";
import TextInputsGrid from "./TextInputsGrid.vue";
import { barWidth, percent } from "../utils/format";

const {
  textA,
  textB,
  result,
  loading,
  error,
  submit: compare,
} = useTextSubmit(compareTexts, (data) => data.matches);

const matches = computed(() => result.value ?? []);

function scoreClass(score) {
  if (score >= 0.9) return "high";
  if (score >= 0.7) return "medium";
  return "low";
}

function fillClass(score) {
  if (score >= 0.9) return "fill-high";
  if (score >= 0.7) return "fill-medium";
  return "fill-low";
}
</script>

<template>
  <div class="card">
    <div class="card-header">
      <div class="card-title">مقایسه جملات دو متن</div>
      <span v-if="matches.length" class="badge"
        >{{ matches.length }} تطبیق یافت شد</span
      >
    </div>

    <TextInputsGrid
      v-model:modelA="textA"
      v-model:modelB="textB"
      id-a="textA"
      id-b="textB"
    />

    <div class="action-bar">
      <button class="btn-primary" :disabled="loading" @click="compare">
        <span v-if="loading" class="spinner"></span>
        {{ loading ? "در حال پردازش..." : "شروع مقایسه" }}
      </button>
    </div>

    <div v-if="error" class="alert-error">{{ error }}</div>

    <template v-if="matches.length">
      <div class="results-header">
        <span class="results-title">نتایج مقایسه</span>
        <div class="legend">
          <span class="legend-item">
            <span
              class="legend-dot"
              style="
                background: rgba(34, 197, 94, 0.2);
                border: 1.5px solid rgba(34, 197, 94, 0.5);
              "
            ></span>
            بالا (≥۹۰٪)
          </span>
          <span class="legend-item">
            <span
              class="legend-dot"
              style="
                background: rgba(234, 179, 8, 0.2);
                border: 1.5px solid rgba(234, 179, 8, 0.5);
              "
            ></span>
            متوسط (≥۷۰٪)
          </span>
          <span class="legend-item">
            <span
              class="legend-dot"
              style="
                background: rgba(239, 68, 68, 0.2);
                border: 1.5px solid rgba(239, 68, 68, 0.5);
              "
            ></span>
            پایین
          </span>
        </div>
      </div>
      <div class="results-table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>جمله از متن اول</th>
              <th>جمله از متن دوم</th>
              <th title="شباهت معنا (حتی با کلمات متفاوت)">معنایی</th>
              <th title="شباهت کلمه‌به‌کلمه؛ فاصله، نیم‌فاصله و علائم نگارشی نادیده گرفته می‌شوند">لفظی</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(m, i) in matches"
              :key="m.a_index"
              :class="scoreClass(m.similarity)"
            >
              <td>
                <span
                  style="
                    color: var(--text-dim);
                    font-size: 0.78rem;
                    font-weight: 700;
                  "
                  >{{ i + 1 }}</span
                >
              </td>
              <td>{{ m.text_a }}</td>
              <td>{{ m.text_b }}</td>
              <td>
                <div class="score-bar-wrap">
                  <span
                    :class="['score-pill', 'score-' + scoreClass(m.similarity)]"
                  >
                    {{ percent(m.similarity) }}%
                  </span>
                  <div class="score-bar">
                    <div
                      class="score-bar-fill"
                      :class="fillClass(m.similarity)"
                      :style="{ width: barWidth(m.similarity) }"
                    ></div>
                  </div>
                </div>
              </td>
              <td>
                <div v-if="m.exact_similarity != null" class="score-bar-wrap">
                  <span
                    :class="[
                      'score-pill',
                      'score-' + scoreClass(m.exact_similarity),
                    ]"
                  >
                    {{ percent(m.exact_similarity) }}%
                  </span>
                  <div class="score-bar">
                    <div
                      class="score-bar-fill"
                      :class="fillClass(m.exact_similarity)"
                      :style="{ width: barWidth(m.exact_similarity) }"
                    ></div>
                  </div>
                </div>
                <span v-else style="color: var(--text-dim)">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <div v-else-if="result && !loading" class="empty-state">
      هیچ جمله‌ی مشابهی میان دو متن یافت نشد
    </div>

    <div v-else-if="!loading && !error" class="empty-state">
      دو متن را وارد کرده و دکمه مقایسه را بزنید
    </div>
  </div>
</template>
