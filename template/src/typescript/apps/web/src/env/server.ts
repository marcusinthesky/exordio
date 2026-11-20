import "server-only";
import { serverEnvironmentSchema } from "./schema";

// Validate on first request, not during compilation. Builds need no credentials.
export function getServerEnvironment() {
  const result = serverEnvironmentSchema.safeParse(process.env);
  if (!result.success) {
    const keys = [
      ...new Set(result.error.issues.map((issue) => issue.path.join("."))),
    ];
    throw new Error(
      `Invalid server environment: ${keys.join(", ")}. See apps/web/env.example.`,
    );
  }
  return result.data;
}
