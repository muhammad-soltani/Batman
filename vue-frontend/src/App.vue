<template>
  <div id="app">
    <header class="app-header">
      <div class="header-inner">
        <div class="logo">
          <span class="logo-icon">🔍</span>
          <div>
            <div class="logo-title">سامانه هوشمند شباهت‌سنجی</div>
            <div class="logo-sub">بستر تشخیص مشابهت نصوص</div>
          </div>
        </div>
        <nav class="tab-nav">
          <button
            v-for="t in tabs"
            :key="t.id"
            :class="['tab-btn', { active: tab === t.id }]"
            @click="tab = t.id"
          >
            <span class="tab-icon">{{ t.icon }}</span>
            {{ t.label }}
          </button>
        </nav>
      </div>
    </header>

    <main class="app-main">
      <Transition name="fade" mode="out-in">
        <component :is="currentView" :key="tab" />
      </Transition>
    </main>

    <footer class="app-footer">
      سامانه تشخیص شباهت و سرقت ادبی متون فارسی
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import CompareView from "./components/CompareView.vue";
import ReportView from "./components/ReportView.vue";
import DiffView from "./components/DiffView.vue";

const tab = ref("compare");
const tabs = [
  { id: "compare", label: "مقایسه جملات", icon: "⚖️" },
  { id: "report", label: "گزارش سرقت ادبی", icon: "📊" },
  { id: "diff", label: "تفاوت و هایلایت", icon: "🎨" },
];

const views = { compare: CompareView, report: ReportView, diff: DiffView };
const currentView = computed(() => views[tab.value]);
</script>

<style>
@import url("https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700&display=swap");

:root {
  --primary: #4f46e5;
  --primary-dark: #3730a3;
  --primary-light: #eef2ff;
  --accent: #f59e0b;
  --success: #10b981;
  --danger: #ef4444;
  --warning: #f59e0b;
  --surface: #ffffff;
  --bg: #f1f5f9;
  --border: #e2e8f0;
  --text: #1e293b;
  --text-muted: #64748b;
  --radius: 14px;
  --shadow: 0 4px 24px rgba(79, 70, 229, 0.08);
  --shadow-lg: 0 8px 40px rgba(79, 70, 229, 0.14);
}

*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: "Vazirmatn", Tahoma, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  direction: rtl;
  min-height: 100vh;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ── HEADER ─────────────────────────────── */
.app-header {
  background: linear-gradient(
    135deg,
    var(--primary-dark) 0%,
    var(--primary) 100%
  );
  box-shadow: 0 2px 16px rgba(79, 70, 229, 0.25);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 14px;
  color: #fff;
}

.logo-icon {
  font-size: 2rem;
}

.logo-title {
  font-size: 1.2rem;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.logo-sub {
  font-size: 0.78rem;
  opacity: 0.75;
  margin-top: 2px;
}

.tab-nav {
  display: flex;
  gap: 4px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  color: rgba(255, 255, 255, 0.75);
  border: none;
  border-bottom: 3px solid transparent;
  border-radius: 0;
  padding: 10px 20px 12px;
  font-family: inherit;
  font-size: 0.92rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 0;
}

.tab-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
}
.tab-btn.active {
  color: #fff;
  border-bottom-color: var(--accent);
  font-weight: 700;
}

.tab-icon {
  font-size: 1.1rem;
}

/* ── MAIN ─────────────────────────────── */
.app-main {
  flex: 1;
  max-width: 1200px;
  margin: 32px auto;
  padding: 0 24px;
  width: 100%;
}

/* ── FOOTER ─────────────────────────────── */
.app-footer {
  text-align: center;
  color: var(--text-muted);
  font-size: 0.8rem;
  padding: 20px;
  border-top: 1px solid var(--border);
  background: var(--surface);
}

/* ── TRANSITION ─────────────────────────── */
.fade-enter-active,
.fade-leave-active {
  transition:
    opacity 0.2s,
    transform 0.2s;
}
.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* ── CARD ─────────────────────────────── */
.card {
  background: var(--surface);
  border-radius: var(--radius);
  padding: 32px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--primary-light);
}

.card-title-icon {
  font-size: 1.4rem;
}

/* ── INPUT SECTION ───────────────────── */
.input-section {
  margin-bottom: 20px;
}

.input-label {
  display: block;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 8px;
  padding-right: 4px;
}

.inputs-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.input-wrap {
  display: flex;
  flex-direction: column;
}

textarea {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid var(--border);
  border-radius: 10px;
  font-size: 0.95rem;
  resize: vertical;
  font-family: inherit;
  direction: rtl;
  color: var(--text);
  background: #fafafa;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
  line-height: 1.8;
  min-height: 160px;
}

textarea:focus {
  outline: none;
  border-color: var(--primary);
  background: #fff;
  box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.08);
}

textarea::placeholder {
  color: #b0bec5;
}

/* ── ACTION BAR ─────────────────────── */
.action-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(
    135deg,
    var(--primary) 0%,
    var(--primary-dark) 100%
  );
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 12px 28px;
  font-family: inherit;
  font-size: 0.98rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(79, 70, 229, 0.4);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}
.btn-primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  box-shadow: none;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* ── ERROR / EMPTY ─────────────────── */
.alert-error {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #991b1b;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  padding: 12px 18px;
  margin-bottom: 20px;
  font-size: 0.92rem;
}

.empty-state {
  text-align: center;
  color: var(--text-muted);
  padding: 48px 0;
  font-size: 0.95rem;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 12px;
}

/* ── RESULTS TABLE ──────────────────── */
.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.results-title {
  font-weight: 700;
  font-size: 1rem;
  color: var(--text);
}

.badge {
  background: var(--primary-light);
  color: var(--primary);
  border-radius: 20px;
  padding: 3px 12px;
  font-size: 0.82rem;
  font-weight: 700;
}

.results-table-wrap {
  overflow-x: auto;
  border-radius: 10px;
  border: 1px solid var(--border);
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.92rem;
}

thead th {
  background: var(--primary-light);
  color: var(--primary);
  font-weight: 700;
  padding: 12px 16px;
  text-align: right;
  font-size: 0.85rem;
  white-space: nowrap;
}

tbody tr {
  transition: background 0.15s;
}
tbody tr:hover td {
  filter: brightness(0.97);
}
tbody td {
  padding: 11px 16px;
  border-top: 1px solid var(--border);
  vertical-align: top;
}

tr.high td {
  background: #f0fdf4;
}
tr.medium td {
  background: #fffbeb;
}
tr.low td {
  background: #fff1f2;
}

.score-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.82rem;
  font-weight: 700;
  white-space: nowrap;
}

.score-high {
  background: #dcfce7;
  color: #15803d;
}
.score-medium {
  background: #fef9c3;
  color: #b45309;
}
.score-low {
  background: #ffe4e6;
  color: #be123c;
}

/* ── STAT CARDS ─────────────────────── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
  margin-bottom: 28px;
}

.stat-card {
  background: var(--primary-light);
  border-radius: 12px;
  padding: 20px 16px;
  text-align: center;
  border: 1px solid rgba(79, 70, 229, 0.1);
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--primary);
  line-height: 1;
  margin-bottom: 6px;
}

.stat-label {
  font-size: 0.78rem;
  color: var(--text-muted);
  font-weight: 500;
}

/* ── DIFF SECTION ─────────────────── */
.diff-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--primary-light);
  border-radius: 10px;
  padding: 14px 18px;
  margin-bottom: 24px;
  font-size: 0.92rem;
  color: var(--primary);
  font-weight: 600;
}

.section-label {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 28px;
}

.diff-list {
  background: #fafafa;
  border: 1px solid var(--border);
  border-radius: 10px;
  min-height: 80px;
  padding: 12px 16px;
  list-style: none;
}

.diff-list li {
  padding: 6px 0;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.9rem;
  line-height: 1.7;
}

.diff-list li:last-child {
  border-bottom: none;
}

.highlight-box {
  background: #fafafa;
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
  font-size: 0.92rem;
  line-height: 2.2;
  min-height: 100px;
  word-break: break-word;
}

/* matching/similar words — highlighted prominently */
.highlight-box .diff-equal {
  background: #dbeafe;
  border-radius: 4px;
  padding: 1px 3px;
  color: #1e40af;
  font-weight: 500;
}

.highlight-box .diff-replace {
  border-radius: 4px;
  padding: 1px 5px;
  font-weight: 600;
  position: relative;
}

/* "from" side — the old word being replaced */
.highlight-box .diff-replace-del {
  background: #fef3c7;
  color: #92400e;
  border: 1.5px dashed #f59e0b;
  text-decoration: line-through;
  text-decoration-color: #d97706;
}

/* "to" side — the new word that replaced it */
.highlight-box .diff-replace-ins {
  background: #ffedd5;
  color: #9a3412;
  border: 1.5px solid #f97316;
  border-bottom: 3px solid #f97316;
}

.highlight-box .diff-del {
  background: #fee2e2;
  border-radius: 4px;
  padding: 1px 4px;
  text-decoration: line-through;
  color: #b91c1c;
  border-bottom: 2px solid #ef4444;
}

.highlight-box .diff-ins {
  background: #dcfce7;
  border-radius: 4px;
  padding: 1px 4px;
  color: #15803d;
  border-bottom: 2px solid #10b981;
}

.legend {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  display: inline-block;
}

/* ── DIVIDER ─────────────────────── */
.section-divider {
  border: none;
  border-top: 2px solid var(--primary-light);
  margin: 28px 0;
}

/* ── RESPONSIVE ──────────────────── */
@media (max-width: 700px) {
  .inputs-grid,
  .two-col {
    grid-template-columns: 1fr;
  }
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  .header-inner {
    padding: 12px 14px 0;
  }
  .app-main {
    padding: 0 12px;
    margin: 16px auto;
  }
  .card {
    padding: 18px 14px;
  }
  .tab-btn {
    padding: 8px 12px 10px;
    font-size: 0.82rem;
  }
}
</style>
