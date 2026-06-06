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
  <div id="app">
    <header class="app-header">
      <div class="header-inner">
        <div class="logo">
          <div class="logo-title">Batman</div>
          <div class="logo-sub">بستر تشخیص شباهت نصوص</div>
        </div>
        <nav class="tab-nav">
          <button
            v-for="t in tabs"
            :key="t.id"
            :class="['tab-btn', { active: tab === t.id }]"
            @click="tab = t.id"
          >
            {{ t.label }}
          </button>
        </nav>
      </div>
    </header>

    <main class="app-main">
      <Transition name="fade" mode="out-in">
        <keep-alive>
          <component :is="currentView" />
        </keep-alive>
      </Transition>
    </main>

    <footer class="app-footer">Batman &mdash; بستر تشخیص شباهت نصوص</footer>
  </div>
</template>
