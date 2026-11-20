"use server";

import { and, eq } from "drizzle-orm";
import { revalidatePath } from "next/cache";
import { requireUser } from "@/auth/session";
import { getDb } from "@/db/client";
import { project } from "@/db/schema";
import {
  type ProjectMutationResult,
  projectIdSchema,
  projectInputSchema,
} from "./schema";

export async function createProject(
  input: unknown,
): Promise<ProjectMutationResult> {
  const user = await requireUser();
  const values = projectInputSchema.safeParse(input);
  if (!values.success)
    return {
      ok: false,
      message: "Check the project name, description, and status.",
    };
  try {
    await getDb()
      .insert(project)
      .values({ ...values.data, ownerId: user.id });
  } catch {
    return {
      ok: false,
      message: "Your project couldn't be saved. Please try again.",
    };
  }
  revalidatePath("/dashboard");
  return { ok: true };
}

export async function updateProject(
  id: unknown,
  input: unknown,
): Promise<ProjectMutationResult> {
  const user = await requireUser();
  const parsedId = projectIdSchema.safeParse(id);
  const values = projectInputSchema.safeParse(input);
  if (!parsedId.success || !values.success)
    return { ok: false, message: "Check the project details." };
  try {
    const changed = await getDb()
      .update(project)
      .set({ ...values.data, updatedAt: new Date() })
      .where(and(eq(project.id, parsedId.data), eq(project.ownerId, user.id)))
      .returning({ id: project.id });
    if (changed.length === 0)
      return { ok: false, message: "This project is no longer available." };
  } catch {
    return {
      ok: false,
      message: "Your changes couldn't be saved. Please try again.",
    };
  }
  revalidatePath("/dashboard");
  return { ok: true };
}

export async function deleteProject(
  id: unknown,
): Promise<ProjectMutationResult> {
  const user = await requireUser();
  const parsedId = projectIdSchema.safeParse(id);
  if (!parsedId.success)
    return { ok: false, message: "This project is no longer available." };
  try {
    const removed = await getDb()
      .delete(project)
      .where(and(eq(project.id, parsedId.data), eq(project.ownerId, user.id)))
      .returning({ id: project.id });
    if (removed.length === 0)
      return { ok: false, message: "This project is no longer available." };
  } catch {
    return {
      ok: false,
      message: "Your project couldn't be deleted. Please try again.",
    };
  }
  revalidatePath("/dashboard");
  return { ok: true };
}
