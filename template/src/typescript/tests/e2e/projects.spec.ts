import { randomUUID } from "node:crypto";
import AxeBuilder from "@axe-core/playwright";
import { expect, type Page, test } from "@playwright/test";

const password = "Exordio-test-password-42!";

async function register(page: Page, email: string) {
  await page.goto("/register");
  await page.getByLabel("Name", { exact: true }).fill("Example developer");
  await page.getByLabel("Email", { exact: true }).fill(email);
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page
    .getByRole("button", { name: "Create account", exact: true })
    .click();
  await expect(page).toHaveURL(/\/dashboard$/);
}

test("authentication, persisted projects, ownership, and logout", async ({
  page,
}) => {
  const id = randomUUID();
  const email = `owner-${id}@example.test`;
  const name = `Project ${id.slice(0, 8)}`;
  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/login/);
  await register(page, email);
  await expect(
    page.getByRole("heading", { name: "Projects", exact: true }),
  ).toBeVisible();

  await page
    .getByRole("button", { name: "New project", exact: true })
    .first()
    .click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel("Project name").fill(name);
  await dialog
    .getByLabel("Description")
    .fill("Created through the public browser workflow.");
  await dialog
    .getByRole("button", { name: "Create project", exact: true })
    .click();
  await expect(dialog).toBeHidden();
  await expect(
    page.getByRole("button", { name: `Edit ${name}`, exact: true }),
  ).toBeVisible();
  await page.reload();
  await expect(
    page.getByRole("button", { name: `Edit ${name}`, exact: true }),
  ).toBeVisible();

  await page.getByRole("button", { name: `Edit ${name}`, exact: true }).click();
  const renamed = `${name} updated`;
  await dialog.getByLabel("Project name").fill(renamed);
  await dialog
    .getByRole("button", { name: "Save changes", exact: true })
    .click();
  await expect(dialog).toBeHidden();
  await expect(
    page.getByRole("button", { name: `Edit ${renamed}`, exact: true }),
  ).toBeVisible();
  await page.getByPlaceholder("Search projects…").fill("no-such-project");
  await expect(
    page.getByRole("button", { name: `Edit ${renamed}`, exact: true }),
  ).toBeHidden();
  await page.getByPlaceholder("Search projects…").clear();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);

  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(page).toHaveURL(/\/login/);
  await register(page, `other-${id}@example.test`);
  await expect(
    page.getByRole("button", { name: `Edit ${renamed}`, exact: true }),
  ).toBeHidden();
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(page).toHaveURL(/\/login/);
  await page.getByLabel("Email", { exact: true }).fill(email);
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  await page
    .getByRole("button", { name: `Delete ${renamed}`, exact: true })
    .click();
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Delete project", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: `Edit ${renamed}`, exact: true }),
  ).toBeHidden();
});

test("public pages are accessible on a narrow viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  for (const route of ["/", "/login", "/register", "/forgot-password"]) {
    await page.goto(route);
    await expect(page.getByRole("main")).toBeVisible();
    expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth),
    ).toBeLessThanOrEqual(390);
  }
});
