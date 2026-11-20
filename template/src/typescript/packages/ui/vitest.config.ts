import { fileURLToPath } from "node:url";
import { storybookTest } from "@storybook/addon-vitest/vitest-plugin";
import react from "@vitejs/plugin-react";
import { playwright } from "@vitest/browser-playwright";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [
    react(),
    storybookTest({
      configDir: fileURLToPath(new URL("./.storybook", import.meta.url)),
    }),
  ],
  test: {
    name: "stories",
    // Storybook requires explicit write access for failure attachments, on loopback only.
    api: { host: "127.0.0.1", allowWrite: true, allowExec: false },
    attachmentsDir: fileURLToPath(
      new URL("../../test-results/stories/", import.meta.url),
    ),
    setupFiles: ["./.storybook/vitest.setup.ts"],
    browser: {
      enabled: true,
      headless: true,
      screenshotFailures: true,
      screenshotDirectory: fileURLToPath(
        new URL("../../test-results/stories/", import.meta.url),
      ),
      provider: playwright({
        launchOptions: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH
          ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH }
          : {},
      }),
      instances: [{ browser: "chromium" }],
    },
  },
});
