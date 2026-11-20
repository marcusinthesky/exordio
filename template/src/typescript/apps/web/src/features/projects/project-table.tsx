"use client";

import { Badge } from "@exordio/ui/components/badge";
import { DataTable } from "@exordio/ui/components/data-table";
import type { ColumnDef } from "@tanstack/react-table";
import { DeleteProjectDialog, ProjectDialog } from "./project-dialog";
import type { ProjectView } from "./schema";

const labels = { planned: "Planned", active: "Active", done: "Done" } as const;
const columns: ColumnDef<ProjectView>[] = [
  {
    accessorKey: "name",
    header: "Project",
    cell: ({ row }) => (
      <div className="min-w-40 space-y-1">
        <p className="font-medium">{row.original.name}</p>
        <p className="max-w-sm truncate text-sm text-muted-foreground">
          {row.original.description || "No description yet"}
        </p>
      </div>
    ),
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => (
      <Badge
        variant={row.original.status === "active" ? "default" : "secondary"}
      >
        {labels[row.original.status]}
      </Badge>
    ),
  },
  {
    accessorKey: "updatedAt",
    header: "Updated",
    cell: ({ row }) => (
      <time
        dateTime={row.original.updatedAt}
        className="whitespace-nowrap text-sm text-muted-foreground"
      >
        {new Intl.DateTimeFormat("en", {
          dateStyle: "medium",
          timeZone: "UTC",
        }).format(new Date(row.original.updatedAt))}
      </time>
    ),
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Actions</span>,
    cell: ({ row }) => (
      <div className="flex justify-end gap-1">
        <ProjectDialog project={row.original} />
        <DeleteProjectDialog project={row.original} />
      </div>
    ),
  },
];

export function ProjectTable({ projects }: { projects: ProjectView[] }) {
  return (
    <DataTable
      columns={columns}
      data={projects}
      searchColumn="name"
      searchPlaceholder="Search projects…"
      emptyMessage="No projects match your search."
    />
  );
}
