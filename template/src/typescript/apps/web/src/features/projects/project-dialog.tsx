"use client";

import { Button } from "@exordio/ui/components/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@exordio/ui/components/dialog";
import { Input } from "@exordio/ui/components/input";
import { Label } from "@exordio/ui/components/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@exordio/ui/components/select";
import { Textarea } from "@exordio/ui/components/textarea";
import { zodResolver } from "@hookform/resolvers/zod";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useId, useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { toast } from "sonner";
import { createProject, deleteProject, updateProject } from "./actions";
import {
  type ProjectInput,
  type ProjectView,
  projectInputSchema,
} from "./schema";

export function ProjectDialog({ project }: { project?: ProjectView }) {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const id = useId();
  const router = useRouter();
  const defaults: ProjectInput = project
    ? {
        name: project.name,
        description: project.description,
        status: project.status,
      }
    : { name: "", description: "", status: "planned" };
  const form = useForm<ProjectInput>({
    resolver: zodResolver(projectInputSchema),
    defaultValues: defaults,
  });
  const { errors, isSubmitting } = form.formState;
  function changeOpen(value: boolean) {
    if (isSubmitting) return;
    if (value) {
      form.reset(defaults);
      setMessage("");
    }
    setOpen(value);
  }
  async function submit(values: ProjectInput) {
    setMessage("");
    try {
      const result = project
        ? await updateProject(project.id, values)
        : await createProject(values);
      if (!result.ok) {
        setMessage(result.message);
        return;
      }
      toast.success(project ? "Project updated" : "Project created");
      setOpen(false);
      router.refresh();
    } catch {
      setMessage("We couldn't save your changes. Please try again.");
    }
  }
  return (
    <Dialog open={open} onOpenChange={changeOpen}>
      <DialogTrigger
        render={
          project ? (
            <Button
              variant="ghost"
              size="icon"
              aria-label={`Edit ${project.name}`}
            />
          ) : (
            <Button />
          )
        }
      >
        {project ? (
          <Pencil className="size-4" aria-hidden="true" />
        ) : (
          <>
            <Plus className="size-4" aria-hidden="true" />
            New project
          </>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>
            {project ? "Edit project" : "Create a project"}
          </DialogTitle>
          <DialogDescription>
            {project
              ? "Keep your project details up to date."
              : "Start with a name and a little context. You can refine it as you go."}
          </DialogDescription>
        </DialogHeader>
        <form
          onSubmit={form.handleSubmit(submit)}
          className="space-y-5"
          noValidate
        >
          <div className="space-y-2">
            <Label htmlFor={`${id}-name`}>Project name</Label>
            <Input
              id={`${id}-name`}
              autoComplete="off"
              maxLength={80}
              aria-invalid={Boolean(errors.name)}
              aria-describedby={errors.name ? `${id}-name-error` : undefined}
              {...form.register("name")}
            />
            {errors.name && (
              <p id={`${id}-name-error`} className="text-sm text-destructive">
                {errors.name.message}
              </p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor={`${id}-description`}>Description</Label>
            <Textarea
              id={`${id}-description`}
              maxLength={1200}
              rows={4}
              aria-invalid={Boolean(errors.description)}
              aria-describedby={
                errors.description ? `${id}-description-error` : undefined
              }
              {...form.register("description")}
            />
            {errors.description && (
              <p
                id={`${id}-description-error`}
                className="text-sm text-destructive"
              >
                {errors.description.message}
              </p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor={`${id}-status`}>Status</Label>
            <Controller
              name="status"
              control={form.control}
              render={({ field }) => (
                <Select value={field.value} onValueChange={field.onChange}>
                  <SelectTrigger
                    id={`${id}-status`}
                    className="w-full"
                    onBlur={field.onBlur}
                  >
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="planned">Planned</SelectItem>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="done">Done</SelectItem>
                  </SelectContent>
                </Select>
              )}
            />
          </div>
          {message && (
            <p role="alert" className="text-sm text-destructive">
              {message}
            </p>
          )}
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              disabled={isSubmitting}
              onClick={() => setOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting
                ? "Saving…"
                : project
                  ? "Save changes"
                  : "Create project"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function DeleteProjectDialog({ project }: { project: ProjectView }) {
  const [open, setOpen] = useState(false);
  const [pending, setPending] = useState(false);
  const [message, setMessage] = useState("");
  const router = useRouter();
  async function remove() {
    setPending(true);
    setMessage("");
    try {
      const result = await deleteProject(project.id);
      if (!result.ok) {
        setMessage(result.message);
        return;
      }
      toast.success("Project deleted");
      setOpen(false);
      router.refresh();
    } catch {
      setMessage("We couldn't delete the project. Please try again.");
    } finally {
      setPending(false);
    }
  }
  return (
    <Dialog
      open={open}
      onOpenChange={(value) => {
        if (!pending) {
          setOpen(value);
          setMessage("");
        }
      }}
    >
      <DialogTrigger
        render={
          <Button
            variant="ghost"
            size="icon"
            aria-label={`Delete ${project.name}`}
          />
        }
      >
        <Trash2 className="size-4" aria-hidden="true" />
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete this project?</DialogTitle>
          <DialogDescription>
            “{project.name}” will be permanently removed. This can't be undone.
          </DialogDescription>
        </DialogHeader>
        {message && (
          <p role="alert" className="text-sm text-destructive">
            {message}
          </p>
        )}
        <DialogFooter>
          <Button
            variant="outline"
            disabled={pending}
            onClick={() => setOpen(false)}
          >
            Keep project
          </Button>
          <Button variant="destructive" disabled={pending} onClick={remove}>
            {pending ? "Deleting…" : "Delete project"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
