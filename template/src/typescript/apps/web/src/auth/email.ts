import "server-only";
import nodemailer from "nodemailer";
import { getServerEnvironment } from "@/env/server";

export async function sendAuthEmail(to: string, subject: string, text: string) {
  const env = getServerEnvironment();
  const transport = nodemailer.createTransport({
    host: env.SMTP_HOST,
    port: env.SMTP_PORT,
    secure: env.SMTP_SECURE,
    requireTLS: env.SMTP_REQUIRE_TLS,
    connectionTimeout: 10_000,
    socketTimeout: 10_000,
    ...(env.SMTP_USER && env.SMTP_PASSWORD
      ? { auth: { user: env.SMTP_USER, pass: env.SMTP_PASSWORD } }
      : {}),
  });
  // Plain text avoids unsafe interpolation and works in the local Mailpit inbox.
  await transport.sendMail({ from: env.EMAIL_FROM, to, subject, text });
}
