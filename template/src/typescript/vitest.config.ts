import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

export default defineConfig({
  resolve: {
    alias: { "@": fileURLToPath(new URL("./apps/web/src", import.meta.url)) },
  },
  test: {
    name: "unit",
    environment: "node",
    include: ["apps/web/src/**/*.test.ts", "tests/unit/**/*.test.ts"],
    maxWorkers: 2,
  },
});
