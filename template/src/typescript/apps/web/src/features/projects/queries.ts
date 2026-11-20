import "server-only";
import { desc, eq } from "drizzle-orm";
import { getDb } from "@/db/client";
import { project } from "@/db/schema";
import type { ProjectView } from "./schema";

export async function listProjects(ownerId: string): Promise<ProjectView[]> {
  const rows = await getDb()
    .select({
      id: project.id,
      name: project.name,
      description: project.description,
      status: project.status,
      updatedAt: project.updatedAt,
    })
    .from(project)
    .where(eq(project.ownerId, ownerId))
    .orderBy(desc(project.updatedAt))
    .limit(100);
  return rows.map((row) => ({
    ...row,
    updatedAt: row.updatedAt.toISOString(),
  }));
}
