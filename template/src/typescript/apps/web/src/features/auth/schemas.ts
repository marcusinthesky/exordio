import { z } from "zod";

export const passwordSchema = z
  .string()
  .min(12, "Use at least 12 characters.")
  .max(128, "Use at most 128 characters.");
const emailSchema = z.email("Enter a valid email address.").max(254);
export const registerSchema = z.object({
  name: z.string().trim().min(1, "Enter your name.").max(80),
  email: emailSchema,
  password: passwordSchema,
});
export const resetRequestSchema = z.object({ email: emailSchema });
export const resetPasswordSchema = z.object({ password: passwordSchema });
