import type { Meta, StoryObj } from "@storybook/react-vite";
import { InfoIcon } from "lucide-react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "./accordion";
import { Alert, AlertDescription, AlertTitle } from "./alert";
import { Avatar, AvatarFallback } from "./avatar";
import { Badge } from "./badge";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "./breadcrumb";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "./card";
import { Progress } from "./progress";
import { ScrollArea } from "./scroll-area";
import { Skeleton } from "./skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./tabs";

function Display() {
  return (
    <main className="mx-auto max-w-3xl space-y-8 p-8">
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href="/">Workspace</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>Components</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      <h1 className="text-2xl font-semibold">Content and feedback</h1>
      <div className="flex items-center gap-3">
        <Avatar>
          <AvatarFallback>AC</AvatarFallback>
        </Avatar>
        <div className="flex flex-wrap gap-2">
          <Badge>Active</Badge>
          <Badge variant="secondary">Planned</Badge>
          <Badge variant="outline">Review</Badge>
          <Badge variant="destructive">Needs attention</Badge>
        </div>
      </div>
      <Alert>
        <InfoIcon aria-hidden="true" />
        <AlertTitle>You're all set</AlertTitle>
        <AlertDescription>
          Small details make a consistent experience.
        </AlertDescription>
      </Alert>
      <Card>
        <CardHeader>
          <CardTitle>Project health</CardTitle>
          <CardDescription>
            One visual language across every screen.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Progress value={65} aria-label="Project completion" />
        </CardContent>
        <CardFooter className="text-muted-foreground">65% complete</CardFooter>
      </Card>
      <Tabs defaultValue="overview">
        <TabsList aria-label="Project sections">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="activity">Activity</TabsTrigger>
        </TabsList>
        <TabsContent value="overview">
          <p className="py-4 text-sm text-muted-foreground">
            An overview of the team's work.
          </p>
        </TabsContent>
        <TabsContent value="activity">
          <p className="py-4 text-sm text-muted-foreground">
            Recent changes and progress.
          </p>
        </TabsContent>
      </Tabs>
      <Accordion>
        <AccordionItem value="theming">
          <AccordionTrigger>Where do I change the theme?</AccordionTrigger>
          <AccordionContent>
            Edit the shared CSS tokens to restyle every component and layout
            together.
          </AccordionContent>
        </AccordionItem>
        <AccordionItem value="components">
          <AccordionTrigger>Can I customize these components?</AccordionTrigger>
          <AccordionContent>
            The source lives in this repository, alongside its stories and
            tests.
          </AccordionContent>
        </AccordionItem>
      </Accordion>
      <section aria-labelledby="loading-heading">
        <h2 id="loading-heading" className="mb-4 text-sm font-medium">
          Loading state
        </h2>
        <div className="flex gap-4">
          <Skeleton className="size-12 rounded-full" />
          <div className="flex-1 space-y-3">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        </div>
      </section>
      <ScrollArea
        className="h-32 rounded-lg border p-4"
        role="region"
        aria-label="Recent updates"
        tabIndex={0}
      >
        <ol className="space-y-2 text-sm text-muted-foreground">
          {[
            "Project created",
            "Brief updated",
            "Design approved",
            "Build started",
            "Preview shared",
            "Review requested",
            "Feedback added",
            "Changes accepted",
            "Checks passed",
            "Release prepared",
          ].map((update) => (
            <li key={update}>{update}</li>
          ))}
        </ol>
      </ScrollArea>
    </main>
  );
}

const meta = {
  title: "Components/Content and feedback",
  component: Display,
} satisfies Meta<typeof Display>;
export default meta;
export const Default: StoryObj<typeof meta> = {};
export const Dark: StoryObj<typeof meta> = { globals: { theme: "dark" } };
