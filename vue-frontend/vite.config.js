import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3002,
    proxy: {
      "/api/compare": "http://0.0.0.0:8000",
      "/api/report": "http://0.0.0.0:8000",
      "/api/diff-highlight": "http://0.0.0.0:8000",
    },
  },
});
