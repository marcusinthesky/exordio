import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const cases = [
  {
    id: "foundations-overview--light",
    name: "foundations-light",
    width: 1280,
    height: 900,
  },
  {
    id: "foundations-overview--dark",
    name: "foundations-dark",
    width: 1280,
    height: 900,
  },
  {
    id: "layouts-workspace--default",
    name: "workspace-desktop",
    width: 1280,
    height: 900,
  },
  {
    id: "layouts-workspace--default",
    name: "workspace-mobile",
    width: 390,
    height: 844,
  },
];

for (const scenario of cases) {
  test(`${scenario.name} accessibility and layout`, async ({ page }) => {
    await page.setViewportSize({
      width: scenario.width,
      height: scenario.height,
    });
    await page.goto(`/iframe.html?id=${scenario.id}&viewMode=story`);
    await expect(page.locator("#storybook-root")).not.toBeEmpty();
    await page.evaluate(() => document.fonts.ready);
    await expect(page.locator(".sb-errordisplay")).toBeHidden();
    expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth),
    ).toBeLessThanOrEqual(scenario.width);
  });

  test(`${scenario.name} screenshot`, async ({ page }) => {
    test.skip(
      process.platform !== "linux" || process.arch !== "x64",
      "Reviewed screenshot baselines are Linux x86-64; accessibility/layout and browser interactions run on both architectures.",
    );
    await page.setViewportSize({
      width: scenario.width,
      height: scenario.height,
    });
    await page.goto(`/iframe.html?id=${scenario.id}&viewMode=story`);
    await expect(page.locator("#storybook-root")).not.toBeEmpty();
    await page.evaluate(() => document.fonts.ready);
    await expect(page).toHaveScreenshot(`${scenario.name}.png`, {
      fullPage: true,
    });
  });
}
