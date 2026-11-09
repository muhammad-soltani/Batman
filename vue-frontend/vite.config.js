import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// Backend used by the dev-server proxy. 0.0.0.0 is a bind address, not a
// valid destination on every OS (connecting to it fails on Windows).
const apiTarget = process.env.API_PROXY_TARGET || "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3002,
    proxy: {
      "/api": { target: apiTarget, changeOrigin: true },
    },
  },
  build: {
    sourcemap: false,
  },
  test: {
    environment: "jsdom",
    include: ["tests/**/*.spec.js"],
    restoreMocks: true,
  },
});
