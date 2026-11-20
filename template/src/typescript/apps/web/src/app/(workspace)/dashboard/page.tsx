import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@exordio/ui/components/card";
import { PageHeader } from "@exordio/ui/layouts/page-header";
import { ActivityChart } from "@exordio/ui/patterns/activity-chart";
import { EmptyState } from "@exordio/ui/patterns/empty-state";
import { FolderKanban } from "lucide-react";
import { requireUser } from "@/auth/session";
import { ProjectDialog } from "@/features/projects/project-dialog";
import { ProjectTable } from "@/features/projects/project-table";
import { listProjects } from "@/features/projects/queries";

export const metadata = { title: "Projects" };

export default async function DashboardPage() {
  const user = await requireUser();
  const projects = await listProjects(user.id);
  const metrics = [
    {
      label: "In your workspace",
      value: projects.length,
      detail: "Your 100 most recently updated projects",
    },
    {
      label: "In progress",
      value: projects.filter((project) => project.status === "active").length,
      detail: "Good ideas taking shape",
    },
    {
      label: "Completed",
      value: projects.filter((project) => project.status === "done").length,
      detail: "A moment to appreciate your progress",
    },
  ];
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Your workspace"
        title="Projects"
        description="A clear view of what you're building, and what comes next."
        actions={<ProjectDialog />}
      />
      <section
        aria-label="Project overview"
        className="grid gap-4 sm:grid-cols-3"
      >
        {metrics.map((metric) => (
          <Card key={metric.label}>
            <CardHeader>
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {metric.label}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-3xl font-semibold tracking-tight tabular-nums">
                {metric.value}
              </p>
              <p className="text-xs text-muted-foreground">{metric.detail}</p>
            </CardContent>
          </Card>
        ))}
      </section>
      <Card>
        <CardHeader>
          <CardTitle>Project progress</CardTitle>
        </CardHeader>
        <CardContent>
          <ActivityChart
            label="Projects by status"
            data={[
              {
                label: "Planned",
                value: projects.filter(
                  (project) => project.status === "planned",
                ).length,
              },
              {
                label: "Active",
                value: projects.filter((project) => project.status === "active")
                  .length,
              },
              {
                label: "Done",
                value: projects.filter((project) => project.status === "done")
                  .length,
              },
            ]}
          />
        </CardContent>
      </Card>
      <section aria-label="Your projects">
        {projects.length ? (
          <ProjectTable projects={projects} />
        ) : (
          <EmptyState
            title="Good things start here"
            description="Create your first project. A name, a little context, and you're on your way."
            icon={<FolderKanban className="size-6" aria-hidden="true" />}
            action={<ProjectDialog />}
          />
        )}
      </section>
    </div>
  );
}
