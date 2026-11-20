import { z } from "zod";

const booleanString = z
  .enum(["true", "false"])
  .transform((value) => value === "true");

export const serverEnvironmentSchema = z
  .object({
    APP_ENV: z.enum(["development", "test", "production"]),
    DATABASE_URL: z
      .url()
      .refine((url) => /^postgres(ql)?:/.test(url), "Use PostgreSQL."),
    BETTER_AUTH_URL: z.url(),
    BETTER_AUTH_SECRET: z.string().min(32),
    SMTP_HOST: z.string().min(1),
    SMTP_PORT: z.coerce.number().int().min(1).max(65535),
    SMTP_SECURE: booleanString,
    SMTP_REQUIRE_TLS: booleanString,
    SMTP_USER: z.string().optional(),
    SMTP_PASSWORD: z.string().optional(),
    EMAIL_FROM: z.string().min(3),
  })
  .superRefine((env, context) => {
    if (!URL.canParse(env.BETTER_AUTH_URL)) return;
    const origin = new URL(env.BETTER_AUTH_URL);
    if (
      !["http:", "https:"].includes(origin.protocol) ||
      origin.username ||
      origin.password
    ) {
      context.addIssue({
        code: "custom",
        path: ["BETTER_AUTH_URL"],
        message: "Use an HTTP(S) origin.",
      });
    }
    if (origin.pathname !== "/" || origin.search || origin.hash) {
      context.addIssue({
        code: "custom",
        path: ["BETTER_AUTH_URL"],
        message: "Use an origin without a path.",
      });
    }
    if (env.APP_ENV === "production") {
      if (origin.protocol !== "https:") {
        context.addIssue({
          code: "custom",
          path: ["BETTER_AUTH_URL"],
          message: "Production requires HTTPS.",
        });
      }
      if (!env.SMTP_SECURE && !env.SMTP_REQUIRE_TLS) {
        context.addIssue({
          code: "custom",
          path: ["SMTP_REQUIRE_TLS"],
          message: "Production email requires TLS.",
        });
      }
    }
    if (Boolean(env.SMTP_USER) !== Boolean(env.SMTP_PASSWORD)) {
      context.addIssue({
        code: "custom",
        path: ["SMTP_USER"],
        message: "Set both SMTP credentials or neither.",
      });
    }
  });
