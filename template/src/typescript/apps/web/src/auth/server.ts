import "server-only";
import { drizzleAdapter } from "@better-auth/drizzle-adapter";
import { betterAuth } from "better-auth";
import { getDb } from "@/db/client";
import * as schema from "@/db/schema";
import { getServerEnvironment } from "@/env/server";
import { sendAuthEmail } from "./email";

function createAuth() {
  const env = getServerEnvironment();
  return betterAuth({
    appName: "Exordio",
    baseURL: env.BETTER_AUTH_URL,
    secret: env.BETTER_AUTH_SECRET,
    database: drizzleAdapter(getDb(), { provider: "pg", schema }),
    trustedOrigins: [env.BETTER_AUTH_URL],
    emailAndPassword: {
      enabled: true,
      minPasswordLength: 12,
      maxPasswordLength: 128,
      requireEmailVerification: env.APP_ENV === "production",
      revokeSessionsOnPasswordReset: true,
      async sendResetPassword({ user: account, url }) {
        await sendAuthEmail(
          account.email,
          "Reset your password",
          `Reset your password using this link:

${url}

If you did not request this, ignore this email.`,
        );
      },
    },
    emailVerification: {
      sendOnSignUp: true,
      sendOnSignIn: true,
      autoSignInAfterVerification: true,
      async sendVerificationEmail({ user: account, url }) {
        await sendAuthEmail(
          account.email,
          "Verify your email",
          `Verify your email address using this link:

${url}`,
        );
      },
    },
    session: { expiresIn: 60 * 60 * 24 * 7, updateAge: 60 * 60 * 24 },
    advanced: {
      useSecureCookies: env.APP_ENV === "production",
      ipAddress: { ipAddressHeaders: [] },
    },
    rateLimit: {
      enabled: true,
      storage: "database",
      window: 60,
      max: 100,
      customRules: {
        "/sign-in/email": { window: 60, max: 10 },
        "/sign-up/email": { window: 60, max: 5 },
        "/request-password-reset": { window: 60, max: 5 },
      },
    },
  });
}

let instance: ReturnType<typeof createAuth> | undefined;

export function getAuth() {
  instance ??= createAuth();
  return instance;
}
