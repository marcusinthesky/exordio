import type { Meta, StoryObj } from "@storybook/react-vite";
import { FolderIcon, PlusIcon } from "lucide-react";
import { Badge } from "./components/badge";
import { Button } from "./components/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./components/card";
import { Input } from "./components/input";
import { Label } from "./components/label";
import { PageHeader } from "./layouts/page-header";
import { ActivityChart } from "./patterns/activity-chart";
import { EmptyState } from "./patterns/empty-state";
import { MetricCard } from "./patterns/metric-card";

function ThemeOverview() {
  return (
    <main className="mx-auto max-w-6xl space-y-8 p-6 md:p-10">
      <PageHeader
        eyebrow="Exordio design system"
        title="A good beginning"
        description="One source of truth for components, layouts, typography and feedback. Change the shared tokens and the whole system follows."
        actions={
          <Button>
            <PlusIcon aria-hidden="true" />
            New project
          </Button>
        }
      />
      <div className="grid gap-4 sm:grid-cols-3">
        <MetricCard
          label="Active projects"
          value={12}
          description="Across your workspace"
        />
        <MetricCard
          label="Completed"
          value={28}
          description="Meaningful progress, one step at a time"
        />
        <MetricCard
          label="Team members"
          value={4}
          description="Building something together"
        />
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Project activity</CardTitle>
            <CardDescription>
              A shared chart palette that adapts to your theme.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ActivityChart
              label="Completed tasks"
              data={[
                { label: "Mon", value: 4 },
                { label: "Tue", value: 6 },
                { label: "Wed", value: 5 },
                { label: "Thu", value: 9 },
                { label: "Fri", value: 12 },
              ]}
            />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Details matter</CardTitle>
            <CardDescription>
              Semantic colors and consistent field states.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="theme-project-name">Project name</Label>
              <Input id="theme-project-name" defaultValue="My next project" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="theme-invalid">Contact email</Label>
              <Input
                id="theme-invalid"
                aria-invalid="true"
                aria-describedby="theme-error"
                defaultValue="not-an-email"
              />
              <p id="theme-error" className="text-sm text-destructive">
                Enter a valid email address.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge>Active</Badge>
              <Badge variant="secondary">Planned</Badge>
              <Badge variant="outline">Review</Badge>
            </div>
            <div className="flex gap-2">
              <Button>Save changes</Button>
              <Button variant="outline">Cancel</Button>
              <Button disabled>Pending</Button>
            </div>
          </CardContent>
        </Card>
      </div>
      <EmptyState
        icon={<FolderIcon className="size-6" />}
        title="Space for your next idea"
        description="Empty states explain what comes next and provide a clear way to get started."
        action={<Button variant="outline">Create a project</Button>}
      />
      <section aria-labelledby="tokens-heading" className="space-y-4">
        <h2 id="tokens-heading" className="text-lg font-semibold">
          Semantic palette
        </h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
          {[
            {
              label: "Primary",
              className: "bg-primary text-primary-foreground",
            },
            {
              label: "Secondary",
              className: "bg-secondary text-secondary-foreground",
            },
            { label: "Muted", className: "bg-muted text-muted-foreground" },
            { label: "Accent", className: "bg-accent text-accent-foreground" },
            { label: "Card", className: "bg-card text-card-foreground" },
          ].map((item) => (
            <div
              key={item.label}
              className={`rounded-lg border px-4 py-8 text-center text-sm font-medium ${item.className}`}
            >
              {item.label}
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

const meta = {
  title: "Foundations/Overview",
  component: ThemeOverview,
} satisfies Meta<typeof ThemeOverview>;
export default meta;
export const Light: StoryObj<typeof meta> = { globals: { theme: "light" } };
export const Dark: StoryObj<typeof meta> = { globals: { theme: "dark" } };
