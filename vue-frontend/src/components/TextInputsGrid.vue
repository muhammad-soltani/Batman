<script setup>
import { MAX_TEXT_LENGTH } from "../config";

const props = defineProps({
  modelA: { type: String, default: "" },
  modelB: { type: String, default: "" },
  idA: { type: String, default: "textA" },
  idB: { type: String, default: "textB" },
  placeholderA: { type: String, default: "متن اول را اینجا وارد کنید..." },
  placeholderB: { type: String, default: "متن دوم را اینجا وارد کنید..." },
  maxLength: { type: Number, default: MAX_TEXT_LENGTH },
});

const emit = defineEmits(["update:modelA", "update:modelB"]);

const fields = [
  { key: "A", label: "متن اول" },
  { key: "B", label: "متن دوم" },
];

const value = (key) => props[`model${key}`];
const isOver = (key) => value(key).length > props.maxLength;
</script>

<template>
  <div class="inputs-grid">
    <div v-for="f in fields" :key="f.key" class="input-wrap">
      <div class="input-header">
        <label class="input-label" :for="props[`id${f.key}`]">{{ f.label }}</label>
        <span
          class="input-counter"
          :class="{ 'input-counter-over': isOver(f.key) }"
          :id="`${props[`id${f.key}`]}-counter`"
        >
          {{ value(f.key).length.toLocaleString("fa") }} /
          {{ maxLength.toLocaleString("fa") }} کاراکتر
        </span>
      </div>
      <textarea
        :id="props[`id${f.key}`]"
        :value="value(f.key)"
        :placeholder="props[`placeholder${f.key}`]"
        :aria-invalid="isOver(f.key) || undefined"
        :aria-describedby="`${props[`id${f.key}`]}-counter`"
        :class="{ 'textarea-over': isOver(f.key) }"
        rows="8"
        @input="emit(`update:model${f.key}`, $event.target.value)"
      />
    </div>
  </div>
</template>
