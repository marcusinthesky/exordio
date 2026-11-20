import { defineConfig } from "@playwright/test";

const executablePath = process.env["PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH"];

export default defineConfig({
  testDir: "./tests/visual",
  fullyParallel: false,
  forbidOnly: Boolean(process.env["CI"]),
  workers: 1,
  // Initial baselines must be reviewed explicitly, never created by a check.
  updateSnapshots: "none",
  snapshotPathTemplate: "{testDir}/baselines/{arg}{ext}",
  expect: {
    toHaveScreenshot: {
      animations: "disabled",
      caret: "hide",
      maxDiffPixelRatio: 0.005,
    },
  },
  reporter: [
    ["list"],
    ["html", { outputFolder: "playwright-report/visual", open: "never" }],
  ],
  outputDir: "test-results/visual",
  use: {
    baseURL: "http://127.0.0.1:6006",
    viewport: { width: 1280, height: 900 },
    deviceScaleFactor: 1,
    locale: "en-US",
    timezoneId: "UTC",
    reducedMotion: "reduce",
    launchOptions: executablePath ? { executablePath } : {},
  },
  webServer: {
    command: "node scripts/serve-storybook.mjs",
    url: "http://127.0.0.1:6006",
    reuseExistingServer: false,
    timeout: 30_000,
  },
});
