import { describe, expect, it } from "vitest";
import { projectIdSchema, projectInputSchema } from "./schema";

describe("project input", () => {
  it("normalizes authored text and ignores client-supplied ownership", () => {
    expect(
      projectInputSchema.parse({
        name: "  Research  ",
        description: "  First milestone  ",
        status: "active",
        ownerId: "somebody-else",
        id: "forged",
      }),
    ).toEqual({
      name: "Research",
      description: "First milestone",
      status: "active",
    });
  });

  it.each([
    { name: "   ", description: "", status: "planned" },
    { name: "x".repeat(81), description: "", status: "planned" },
    { name: "Project", description: "x".repeat(1201), status: "planned" },
    { name: "Project", description: "", status: "deleted" },
  ])("rejects invalid project data", (input) => {
    expect(projectInputSchema.safeParse(input).success).toBe(false);
  });

  it("rejects forged or malformed identities", () => {
    expect(projectIdSchema.safeParse("1 OR 1=1").success).toBe(false);
    expect(
      projectIdSchema.safeParse("cb7d958a-9267-4910-9739-664e0987f5cc").success,
    ).toBe(true);
  });
});
