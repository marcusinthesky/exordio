import type { Meta, StoryObj } from "@storybook/react-vite";
import {
  FolderIcon,
  LayoutDashboardIcon,
  PlusIcon,
  SettingsIcon,
  SparklesIcon,
} from "lucide-react";
import { Avatar, AvatarFallback } from "../components/avatar";
import { Badge } from "../components/badge";
import { Button } from "../components/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/card";
import { DataTable } from "../components/data-table";
import { MetricCard } from "../patterns/metric-card";
import { AppShell } from "./app-shell";
import { PageHeader } from "./page-header";

const projects = [
  { name: "Website refresh", owner: "Alex Chen", status: "Active" },
  { name: "Customer research", owner: "Morgan Reed", status: "Planned" },
  { name: "Design foundations", owner: "Alex Chen", status: "Done" },
];

function Workspace() {
  return (
    <AppShell
      brand={
        <span className="flex items-center gap-2">
          <SparklesIcon className="size-5 text-primary" aria-hidden="true" />
          Exordio
        </span>
      }
      navigation={
        <>
          <a
            href="#main-content"
            aria-current="page"
            className="flex items-center gap-3 rounded-lg bg-sidebar-accent px-3 py-2 text-sm font-medium text-sidebar-accent-foreground"
          >
            <LayoutDashboardIcon className="size-4" aria-hidden="true" />
            Overview
          </a>
          <a
            href="#projects"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
          >
            <FolderIcon className="size-4" aria-hidden="true" />
            Projects
          </a>
          <a
            href="#settings"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
          >
            <SettingsIcon className="size-4" aria-hidden="true" />
            Settings
          </a>
        </>
      }
      actions={
        <Avatar>
          <AvatarFallback>AC</AvatarFallback>
        </Avatar>
      }
    >
      <PageHeader
        eyebrow="Your workspace"
        title="Make room for progress"
        description="A clear view of what's moving, what needs attention, and what comes next."
        actions={
          <Button>
            <PlusIcon aria-hidden="true" />
            New project
          </Button>
        }
      />
      <div className="grid gap-4 sm:grid-cols-3">
        <MetricCard label="Active" value={1} description="Moving forward" />
        <MetricCard
          label="Planned"
          value={1}
          description="Ready for the next step"
        />
        <MetricCard
          label="Completed"
          value={1}
          description="Progress worth celebrating"
        />
      </div>
      <section id="projects" aria-label="Projects">
        <Card>
          <CardHeader>
            <CardTitle>Projects</CardTitle>
            <CardDescription>
              A small, focused collection of meaningful work.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <DataTable
              data={projects}
              searchColumn="name"
              columns={[
                {
                  accessorKey: "name",
                  header: "Project",
                  cell: ({ row }) => (
                    <span className="font-medium">{row.original.name}</span>
                  ),
                },
                { accessorKey: "owner", header: "Owner" },
                {
                  accessorKey: "status",
                  header: "Status",
                  cell: ({ row }) => (
                    <Badge
                      variant={
                        row.original.status === "Active"
                          ? "default"
                          : "secondary"
                      }
                    >
                      {row.original.status}
                    </Badge>
                  ),
                },
              ]}
            />
          </CardContent>
        </Card>
      </section>
    </AppShell>
  );
}

const meta = {
  title: "Layouts/Workspace",
  component: Workspace,
} satisfies Meta<typeof Workspace>;
export default meta;
export const Default: StoryObj<typeof meta> = {};
export const Dark: StoryObj<typeof meta> = { globals: { theme: "dark" } };
