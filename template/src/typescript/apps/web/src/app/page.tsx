import { Badge } from "@exordio/ui/components/badge";
import { Button } from "@exordio/ui/components/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@exordio/ui/components/card";
import { ArrowRight, CheckCircle2, Layers, Sparkles } from "lucide-react";
import Link from "next/link";
import { Brand } from "@/components/brand";
import { ThemeToggle } from "@/components/theme-toggle";

const features = [
  {
    title: "A place for every project",
    description:
      "Capture the next idea, define what matters, and keep work moving.",
    icon: Layers,
  },
  {
    title: "Clarity at a glance",
    description:
      "See what's planned, what's active, and what you've accomplished.",
    icon: CheckCircle2,
  },
  {
    title: "Room to make it yours",
    description:
      "A thoughtful starting point with calm layouts and a theme that follows you.",
    icon: Sparkles,
  },
];

export default function HomePage() {
  return (
    <div className="mx-auto max-w-6xl px-6">
      <header className="flex h-20 items-center justify-between border-b">
        <Brand />
        <nav aria-label="Main navigation" className="flex items-center gap-2">
          <ThemeToggle />
          <Button variant="ghost" render={<Link href="/login" />}>
            Sign in
          </Button>
          <Button size="sm" render={<Link href="/register" />}>
            Get started
          </Button>
        </nav>
      </header>
      <main>
        <section className="mx-auto flex max-w-3xl flex-col items-center gap-7 py-24 text-center sm:py-32">
          <Badge variant="secondary">A spell for good beginnings</Badge>
          <h1 className="text-balance text-5xl font-semibold tracking-tight sm:text-7xl">
            Give your next idea a place to grow.
          </h1>
          <p className="max-w-xl text-pretty text-lg leading-relaxed text-muted-foreground">
            Bring your projects into focus. A simple, considered workspace for
            turning a good beginning into something that matters.
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            <Button size="lg" render={<Link href="/register" />}>
              Create your workspace <ArrowRight aria-hidden="true" />
            </Button>
            <Button variant="outline" size="lg" render={<Link href="/login" />}>
              Continue your work
            </Button>
          </div>
        </section>
        <section
          aria-label="What you can do"
          className="grid gap-5 pb-24 md:grid-cols-3"
        >
          {features.map(({ title, description, icon: Icon }) => (
            <Card key={title} className="bg-card">
              <CardHeader>
                <Icon className="mb-3 size-5 text-primary" aria-hidden="true" />
                <CardTitle>{title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm leading-relaxed text-muted-foreground">
                  {description}
                </p>
              </CardContent>
            </Card>
          ))}
        </section>
      </main>
      <footer className="border-t py-8 text-sm text-muted-foreground">
        Made for good beginnings.
      </footer>
    </div>
  );
}
