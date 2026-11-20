import { randomBytes } from "node:crypto";
import { writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

// Setup creates a private, ignored local configuration once. Existing settings,
// including a symlink, are never replaced. Shell entry does not load credentials.
const destination = fileURLToPath(
  new URL("../apps/web/.env.local", import.meta.url),
);
const settings = {
  APP_ENV: "development",
  DATABASE_URL:
    process.env.DATABASE_URL ??
    "postgresql://exordio:exordio@127.0.0.1:55432/exordio",
  BETTER_AUTH_SECRET: randomBytes(32).toString("base64url"),
  BETTER_AUTH_URL: "http://localhost:3000",
  SMTP_HOST: "127.0.0.1",
  SMTP_PORT: process.env.SMTP_PORT ?? "1025",
  SMTP_SECURE: "false",
  SMTP_REQUIRE_TLS: "false",
  EMAIL_FROM: "Exordio <noreply@localhost>",
};
const content = [
  "# Local development only. Created once by explicit setup; never commit.",
  ...Object.entries(settings).map(
    ([key, value]) => `${key}=${JSON.stringify(value)}`,
  ),
  "",
].join("\n");
try {
  await writeFile(destination, content, { flag: "wx", mode: 0o600 });
  console.log("Created apps/web/.env.local for local development.");
} catch (error) {
  if (error.code !== "EEXIST") throw error;
  console.log("Preserved existing apps/web/.env.local.");
}
