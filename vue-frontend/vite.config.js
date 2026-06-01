import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      "/compare": "http://localhost:8000",
      "/report": "http://localhost:8000",
      "/diff-highlight": "http://localhost:8000",
    },
  },
});
