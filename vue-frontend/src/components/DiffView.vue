<template>
  <div class="card">
    <div class="card-title">
      <span class="card-title-icon">🎨</span>
      تفاوت معنایی و هایلایت
    </div>

    <div class="inputs-grid">
      <div class="input-wrap">
        <label class="input-label" for="diffA">📄 متن اول</label>
        <textarea
          id="diffA"
          v-model="textA"
          placeholder="متن اول را اینجا وارد کنید..."
          rows="8"
        />
      </div>
      <div class="input-wrap">
        <label class="input-label" for="diffB">📄 متن دوم</label>
        <textarea
          id="diffB"
          v-model="textB"
          placeholder="متن دوم را اینجا وارد کنید..."
          rows="8"
        />
      </div>
    </div>

    <div class="action-bar">
      <button class="btn-primary" :disabled="loading" @click="fetchDiff">
        <span v-if="loading" class="spinner"></span>
        <span v-else>🎨</span>
        {{ loading ? "در حال پردازش..." : "نمایش تفاوت" }}
      </button>
    </div>

    <div v-if="error" class="alert-error">⚠️ {{ error }}</div>

    <template v-if="result">
      <!-- Semantic similarity score banner -->
      <div class="diff-meta">
        <span style="font-size: 1.5rem">🧠</span>
        <span>شباهت معنایی کلی:</span>
        <span style="font-size: 1.3rem; font-weight: 800">
          {{ (result.semantic_diff.semantic_similarity * 100).toFixed(1) }}%
        </span>
      </div>

      <!-- Semantic diff lists -->
      <div class="section-label">📌 تفاوت‌های معنایی</div>
      <div class="two-col" style="margin-bottom: 0">
        <div>
          <div
            class="section-label"
            style="font-size: 0.82rem; color: var(--text-muted)"
          >
            🔵 فقط در متن اول ({{ result.semantic_diff.only_in_a.length }})
          </div>
          <ul class="diff-list">
            <li
              v-if="!result.semantic_diff.only_in_a.length"
              style="color: var(--text-muted)"
            >
              موردی یافت نشد
            </li>
            <li v-for="(s, i) in result.semantic_diff.only_in_a" :key="i">
              {{ s }}
            </li>
          </ul>
        </div>
        <div>
          <div
            class="section-label"
            style="font-size: 0.82rem; color: var(--text-muted)"
          >
            🟠 فقط در متن دوم ({{ result.semantic_diff.only_in_b.length }})
          </div>
          <ul class="diff-list">
            <li
              v-if="!result.semantic_diff.only_in_b.length"
              style="color: var(--text-muted)"
            >
              موردی یافت نشد
            </li>
            <li v-for="(s, i) in result.semantic_diff.only_in_b" :key="i">
              {{ s }}
            </li>
          </ul>
        </div>
      </div>

      <hr class="section-divider" />

      <!-- Highlight -->
      <div class="section-label">🎨 هایلایت تغییرات</div>
      <div class="legend" style="margin-bottom: 14px">
        <span class="legend-item"
          ><span
            class="legend-dot"
            style="background: #dbeafe; border: 1.5px solid #3b82f6"
          ></span>
          مشابه</span
        >
        <span class="legend-item"
          ><span
            class="legend-dot"
            style="background: #fef3c7; border: 1.5px dashed #f59e0b"
          ></span>
          کلمه قبلی (جایگزین‌شده)</span
        >
        <span class="legend-item"
          ><span
            class="legend-dot"
            style="background: #ffedd5; border: 1.5px solid #f97316"
          ></span>
          کلمه جدید (جایگزین)</span
        >
        <span class="legend-item"
          ><span
            class="legend-dot"
            style="background: #fee2e2; border: 1.5px solid #ef4444"
          ></span>
          حذف</span
        >
        <span class="legend-item"
          ><span
            class="legend-dot"
            style="background: #dcfce7; border: 1.5px solid #10b981"
          ></span>
          اضافه</span
        >
      </div>
      <div class="two-col">
        <div>
          <div
            class="section-label"
            style="font-size: 0.82rem; color: var(--text-muted)"
          >
            متن اول
          </div>
          <div class="highlight-box" v-html="result.highlight.a_html" />
        </div>
        <div>
          <div
            class="section-label"
            style="font-size: 0.82rem; color: var(--text-muted)"
          >
            متن دوم
          </div>
          <div class="highlight-box" v-html="result.highlight.b_html" />
        </div>
      </div>
    </template>

    <div v-else-if="!loading && !error" class="empty-state">
      <div class="empty-icon">🎨</div>
      <div>دو متن را وارد کرده و تفاوت‌ها را مشاهده کنید</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { getDiffHighlight } from "../api";

const textA = ref("");
const textB = ref("");
const result = ref(null);
const loading = ref(false);
const error = ref("");

async function fetchDiff() {
  error.value = "";
  result.value = null;
  loading.value = true;
  try {
    const res = await getDiffHighlight(textA.value, textB.value);
    result.value = res.data;
  } catch (e) {
    error.value = e.response?.data?.detail || "خطا در ارتباط با سرور";
  } finally {
    loading.value = false;
  }
}
</script>
