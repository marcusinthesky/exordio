import { z } from "zod";

const projectStatusSchema = z.enum(["planned", "active", "done"]);
export const projectInputSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, "Give your project a name.")
    .max(80, "Use at most 80 characters."),
  description: z.string().trim().max(1200, "Use at most 1,200 characters."),
  status: projectStatusSchema,
});
export const projectIdSchema = z.uuid();

export type ProjectInput = z.infer<typeof projectInputSchema>;
export type ProjectView = ProjectInput & { id: string; updatedAt: string };
export type ProjectMutationResult =
  | { ok: true }
  | { ok: false; message: string };
