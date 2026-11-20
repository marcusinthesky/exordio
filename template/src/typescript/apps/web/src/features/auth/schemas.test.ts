import { describe, expect, it } from "vitest";
import { passwordSchema, registerSchema } from "./schemas";

describe("account input", () => {
  it("requires a usable name, email, and long password", () => {
    expect(
      registerSchema.safeParse({
        name: " ",
        email: "not-an-email",
        password: "short",
      }).success,
    ).toBe(false);
    expect(
      registerSchema.parse({
        name: "  Ada  ",
        email: "ada@example.com",
        password: "correct-horse-battery",
      }).name,
    ).toBe("Ada");
  });
  it("sets bounded password lengths", () => {
    expect(passwordSchema.safeParse("x".repeat(11)).success).toBe(false);
    expect(passwordSchema.safeParse("x".repeat(12)).success).toBe(true);
    expect(passwordSchema.safeParse("x".repeat(129)).success).toBe(false);
  });
});
