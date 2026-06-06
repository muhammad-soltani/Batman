<script setup>
const props = defineProps({
  modelA: { type: String, default: "" },
  modelB: { type: String, default: "" },
  idA: { type: String, default: "textA" },
  idB: { type: String, default: "textB" },
  placeholderA: { type: String, default: "متن اول را اینجا وارد کنید..." },
  placeholderB: { type: String, default: "متن دوم را اینجا وارد کنید..." },
});

const emit = defineEmits(["update:modelA", "update:modelB"]);
</script>

<template>
  <div class="inputs-grid">
    <div class="input-wrap">
      <div class="input-header">
        <label class="input-label" :for="idA">متن اول</label>
        <span class="input-counter"
          >{{ props.modelA.length.toLocaleString("fa") }} کاراکتر</span
        >
      </div>
      <textarea
        :id="idA"
        :value="modelA"
        :placeholder="placeholderA"
        rows="8"
        @input="emit('update:modelA', $event.target.value)"
      />
    </div>
    <div class="input-wrap">
      <div class="input-header">
        <label class="input-label" :for="idB">متن دوم</label>
        <span class="input-counter"
          >{{ props.modelB.length.toLocaleString("fa") }} کاراکتر</span
        >
      </div>
      <textarea
        :id="idB"
        :value="modelB"
        :placeholder="placeholderB"
        rows="8"
        @input="emit('update:modelB', $event.target.value)"
      />
    </div>
  </div>
</template>
