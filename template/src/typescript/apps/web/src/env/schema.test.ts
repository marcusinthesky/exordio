import { describe, expect, it } from "vitest";
import { serverEnvironmentSchema } from "./schema";

const local = {
  APP_ENV: "development",
  DATABASE_URL: "postgresql://localhost/exordio",
  BETTER_AUTH_URL: "http://localhost:3000",
  BETTER_AUTH_SECRET: "unit-test-only-secret-with-32-characters",
  SMTP_HOST: "localhost",
  SMTP_PORT: "1025",
  SMTP_SECURE: "false",
  SMTP_REQUIRE_TLS: "false",
  EMAIL_FROM: "Test <test@example.invalid>",
};

describe("server configuration", () => {
  it("accepts explicit local services", () => {
    const env = serverEnvironmentSchema.parse(local);
    expect(env.SMTP_PORT).toBe(1025);
    expect(env.SMTP_SECURE).toBe(false);
  });

  it("never invents a missing authentication secret", () => {
    expect(
      serverEnvironmentSchema.safeParse({
        ...local,
        BETTER_AUTH_SECRET: undefined,
      }).success,
    ).toBe(false);
  });

  it("requires secure transport for production", () => {
    expect(
      serverEnvironmentSchema.safeParse({ ...local, APP_ENV: "production" })
        .success,
    ).toBe(false);
    expect(
      serverEnvironmentSchema.safeParse({
        ...local,
        APP_ENV: "production",
        BETTER_AUTH_URL: "https://example.com",
        SMTP_REQUIRE_TLS: "true",
      }).success,
    ).toBe(true);
  });

  it.each([
    "not-a-url",
    "https://user:password@example.com",
    "https://example.com/path",
    "https://example.com?redirect=other",
    "ftp://example.com",
  ])("rejects unsuitable auth origins", (url) => {
    expect(
      serverEnvironmentSchema.safeParse({ ...local, BETTER_AUTH_URL: url })
        .success,
    ).toBe(false);
  });

  it("requires a complete SMTP credential pair", () => {
    expect(
      serverEnvironmentSchema.safeParse({ ...local, SMTP_USER: "user" })
        .success,
    ).toBe(false);
  });
});
