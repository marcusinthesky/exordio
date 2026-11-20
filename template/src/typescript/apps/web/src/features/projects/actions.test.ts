import { PgDialect } from "drizzle-orm/pg-core";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  requireUser: vi.fn(),
  getDb: vi.fn(),
  revalidatePath: vi.fn(),
  values: vi.fn(),
  set: vi.fn(),
  where: vi.fn(),
  returning: vi.fn(),
}));

vi.mock("@/auth/session", () => ({ requireUser: mocks.requireUser }));
vi.mock("@/db/client", () => ({ getDb: mocks.getDb }));
vi.mock("next/cache", () => ({ revalidatePath: mocks.revalidatePath }));

import { createProject, deleteProject, updateProject } from "./actions";

const id = "cb7d958a-9267-4910-9739-664e0987f5cc";
const input = {
  name: "First milestone",
  description: "Ready to start",
  status: "planned",
};

beforeEach(() => {
  vi.resetAllMocks();
  mocks.requireUser.mockResolvedValue({ id: "current-user" });
  mocks.returning.mockResolvedValue([{ id }]);
  mocks.where.mockReturnValue({ returning: mocks.returning });
  mocks.set.mockReturnValue({ where: mocks.where });
  mocks.values.mockResolvedValue(undefined);
  mocks.getDb.mockReturnValue({
    insert: () => ({ values: mocks.values }),
    update: () => ({ set: mocks.set }),
    delete: () => ({ where: mocks.where }),
  });
});

describe("project authorization and mutations", () => {
  it("assigns ownership from the validated session, never the submitted owner", async () => {
    expect(await createProject({ ...input, ownerId: "attacker" })).toEqual({
      ok: true,
    });
    expect(mocks.values).toHaveBeenCalledWith({
      ...input,
      ownerId: "current-user",
    });
  });

  it.each([
    "update",
    "delete",
  ])("scopes %s to both project and authenticated owner", async (operation) => {
    const result =
      operation === "update"
        ? await updateProject(id, input)
        : await deleteProject(id);
    expect(result).toEqual({ ok: true });
    const condition = mocks.where.mock.calls[0]?.[0];
    const query = new PgDialect().sqlToQuery(condition);
    expect(query.params).toEqual([id, "current-user"]);
    expect(query.sql).toContain('"owner_id"');
    expect(query.sql).toContain(" and ");
  });

  it("does not claim success for another user's or missing project", async () => {
    mocks.returning.mockResolvedValue([]);
    expect(await updateProject(id, input)).toEqual({
      ok: false,
      message: "This project is no longer available.",
    });
    expect(await deleteProject(id)).toEqual({
      ok: false,
      message: "This project is no longer available.",
    });
    expect(mocks.revalidatePath).not.toHaveBeenCalled();
  });

  it("does not touch persistence when authentication fails", async () => {
    mocks.requireUser.mockRejectedValue(new Error("redirect to login"));
    await expect(createProject(input)).rejects.toThrow("redirect to login");
    await expect(updateProject(id, input)).rejects.toThrow("redirect to login");
    await expect(deleteProject(id)).rejects.toThrow("redirect to login");
    expect(mocks.getDb).not.toHaveBeenCalled();
  });

  it("validates on the server even if the client bypasses the form", async () => {
    expect((await createProject({ ...input, name: "" })).ok).toBe(false);
    expect((await updateProject("forged-id", input)).ok).toBe(false);
    expect((await deleteProject("forged-id")).ok).toBe(false);
    expect(mocks.getDb).not.toHaveBeenCalled();
  });

  it("does not expose database errors to the client", async () => {
    mocks.values.mockRejectedValue(
      new Error("database password and private SQL"),
    );
    const result = await createProject(input);
    expect(result).toEqual({
      ok: false,
      message: "Your project couldn't be saved. Please try again.",
    });
  });
});
