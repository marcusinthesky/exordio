import AxeBuilder from "@axe-core/playwright";
import { expect, type Page, test } from "@playwright/test";

async function expectThemedChartTicks(page: Page) {
  const chart = page.locator('[data-slot="chart"]');
  await expect(chart).toHaveCount(1);
  const ticks = chart.locator(".recharts-cartesian-axis-tick-value");
  await expect(ticks.first()).toBeVisible();
  const expectedFill = await chart.evaluate((element) => {
    // Resolve the semantic token through CSS so hex, RGB and OKLCH serialize equally.
    const probe = element.ownerDocument.createElement("span");
    probe.style.color = "var(--muted-foreground)";
    element.append(probe);
    const color = getComputedStyle(probe).color;
    probe.remove();
    return color;
  });
  for (const tick of await ticks.all()) {
    await expect(tick).toHaveCSS("fill", expectedFill);
  }
}

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
    if (scenario.id.startsWith("foundations-overview")) {
      await expectThemedChartTicks(page);
    }
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
    if (scenario.id.startsWith("foundations-overview")) {
      await expectThemedChartTicks(page);
    }
    await expect(page).toHaveScreenshot(`${scenario.name}.png`, {
      fullPage: true,
    });
  });
}
