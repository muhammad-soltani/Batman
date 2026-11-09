<script setup>
import { ref, computed } from "vue";
import CompareView from "./components/CompareView.vue";
import ReportView from "./components/ReportView.vue";
import DiffView from "./components/DiffView.vue";

const tab = ref("compare");
const tabs = [
  { id: "compare", label: "مقایسه جملات" },
  { id: "report", label: "گزارش سرقت ادبی" },
  { id: "diff", label: "تفاوت و هایلایت" },
];

const views = { compare: CompareView, report: ReportView, diff: DiffView };
const currentView = computed(() => views[tab.value]);
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <div class="header-inner">
        <div class="logo">
          <div class="logo-title">Batman</div>
          <div class="logo-sub">بستر تشخیص مشابهت نصوص</div>
        </div>
        <nav class="tab-nav" role="tablist">
          <button
            v-for="t in tabs"
            :key="t.id"
            type="button"
            role="tab"
            :aria-selected="tab === t.id"
            :class="['tab-btn', { active: tab === t.id }]"
            @click="tab = t.id"
          >
            {{ t.label }}
          </button>
        </nav>
      </div>
    </header>

    <main class="app-main" role="tabpanel">
      <Transition name="fade" mode="out-in">
        <keep-alive>
          <component :is="currentView" />
        </keep-alive>
      </Transition>
    </main>

    <footer class="app-footer">Batman &mdash; بستر تشخیص مشابهت نصوص</footer>
  </div>
</template>
