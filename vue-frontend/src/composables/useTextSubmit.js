/**
 * useTextSubmit — shared state + fetch logic for every compare/report/diff view.
 *
 * Usage:
 *   const { textA, textB, loading, error, result, submit } = useTextSubmit(apiFn)
 *
 * @param {(text_a: string, text_b: string) => Promise} apiFn
 *   An API function that receives (text_a, text_b) and returns an axios promise.
 * @param {(data: any) => any} [transform]
 *   Optional function to extract the relevant slice from the response data.
 *   Defaults to returning the full `data` object.
 */
import { ref } from "vue";

export function useTextSubmit(apiFn, transform = (data) => data) {
  const textA = ref("");
  const textB = ref("");
  const result = ref(null);
  const loading = ref(false);
  const error = ref("");

  async function submit() {
    if (!textA.value.trim() || !textB.value.trim()) {
      error.value = "لطفاً هر دو متن را وارد کنید.";
      return;
    }
    error.value = "";
    result.value = null;
    loading.value = true;
    try {
      const res = await apiFn(textA.value, textB.value);
      result.value = transform(res.data);
    } catch (e) {
      error.value = e.response?.data?.detail || "خطا در ارتباط با سرور";
    } finally {
      loading.value = false;
    }
  }

  return { textA, textB, result, loading, error, submit };
}
