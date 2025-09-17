/// <reference types="vitest" />
import path from "path";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: process.env.VITE_HOST || "0.0.0.0",
    port: parseInt(process.env.VITE_PORT || "3000"),
    proxy: {
      "/api": {
        target: process.env.VITE_API_URL || "http://backend:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
    teardownTimeout: 10000,
  },
});
