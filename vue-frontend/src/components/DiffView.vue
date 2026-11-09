<script setup>
import { getDiffHighlight } from "../api";
import { useTextSubmit } from "../composables/useTextSubmit";
import TextInputsGrid from "./TextInputsGrid.vue";
import { percent } from "../utils/format";

const {
  textA,
  textB,
  result,
  loading,
  error,
  submit: fetchDiff,
} = useTextSubmit(getDiffHighlight);
</script>

<template>
  <div class="card">
    <div class="card-header">
      <div class="card-title">تفاوت معنایی و هایلایت</div>
    </div>

    <TextInputsGrid
      v-model:modelA="textA"
      v-model:modelB="textB"
      id-a="diffA"
      id-b="diffB"
    />

    <div class="action-bar">
      <button class="btn-primary" :disabled="loading" @click="fetchDiff">
        <span v-if="loading" class="spinner"></span>
        {{ loading ? "در حال پردازش..." : "نمایش تفاوت" }}
      </button>
    </div>

    <div v-if="error" class="alert-error">{{ error }}</div>

    <template v-if="result">
      <!-- Semantic similarity score banner -->
      <div class="diff-meta">
        <span>شباهت معنایی کلی:</span>
        <span class="diff-meta-score">
          {{ percent(result.semantic_diff.semantic_similarity) }}%
        </span>
      </div>

      <!-- Semantic diff lists -->
      <div class="section-label">تفاوت‌های معنایی</div>
      <div class="two-col" style="margin-bottom: 0">
        <div>
          <div class="section-label" style="font-size: 0.78rem">
            فقط در متن اول ({{ result.semantic_diff.only_in_a.length }})
          </div>
          <ul class="diff-list">
            <li
              v-if="!result.semantic_diff.only_in_a.length"
              style="color: var(--text-dim)"
            >
              موردی یافت نشد
            </li>
            <li v-for="(s, i) in result.semantic_diff.only_in_a" :key="i">
              {{ s }}
            </li>
          </ul>
        </div>
        <div>
          <div class="section-label" style="font-size: 0.78rem">
            فقط در متن دوم ({{ result.semantic_diff.only_in_b.length }})
          </div>
          <ul class="diff-list">
            <li
              v-if="!result.semantic_diff.only_in_b.length"
              style="color: var(--text-dim)"
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
      <div class="section-label">هایلایت تغییرات</div>

      <!-- completely different notice -->
      <div
        v-if="result.highlight.completely_different"
        class="alert-completely-different"
      >
        این دو متن از نظر معنایی کاملاً متفاوت هستند — هیچ بخش مشترکی قابل تطبیق
        نیست.
      </div>

      <div class="legend" style="margin-bottom: 14px">
        <span class="legend-item">
          <span
            class="legend-dot"
            style="
              background: rgba(120, 120, 160, 0.2);
              border: 1.5px solid rgba(120, 120, 160, 0.5);
            "
          ></span>
          مشابه
        </span>
        <span class="legend-item">
          <span
            class="legend-dot"
            style="
              background: rgba(234, 179, 8, 0.2);
              border: 1.5px dashed rgba(234, 179, 8, 0.5);
            "
          ></span>
          کلمه قبلی (جایگزین‌شده)
        </span>
        <span class="legend-item">
          <span
            class="legend-dot"
            style="
              background: rgba(34, 197, 94, 0.2);
              border: 1.5px solid rgba(34, 197, 94, 0.5);
            "
          ></span>
          کلمه جدید (جایگزین)
        </span>
        <span class="legend-item">
          <span
            class="legend-dot"
            style="
              background: rgba(239, 68, 68, 0.15);
              border: 1.5px solid rgba(239, 68, 68, 0.5);
            "
          ></span>
          حذف
        </span>
        <span class="legend-item">
          <span
            class="legend-dot"
            style="
              background: rgba(34, 197, 94, 0.15);
              border: 1.5px solid rgba(34, 197, 94, 0.5);
            "
          ></span>
          اضافه
        </span>
      </div>

      <div class="two-col">
        <div>
          <div class="section-label" style="font-size: 0.78rem">متن اول</div>
          <div class="highlight-box" v-html="result.highlight.a_html" />
        </div>
        <div>
          <div class="section-label" style="font-size: 0.78rem">متن دوم</div>
          <div class="highlight-box" v-html="result.highlight.b_html" />
        </div>
      </div>
    </template>

    <div v-else-if="!loading && !error" class="empty-state">
      دو متن را وارد کرده و تفاوت‌ها را مشاهده کنید
    </div>
  </div>
</template>
