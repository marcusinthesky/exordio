"use client";

import { Button } from "@exordio/ui/components/button";
import { EmptyState } from "@exordio/ui/patterns/empty-state";

export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <main className="flex min-h-svh items-center justify-center px-6">
      <EmptyState
        title="We couldn't load this page"
        description="Please try again in a moment."
        action={<Button onClick={reset}>Try again</Button>}
      />
    </main>
  );
}
