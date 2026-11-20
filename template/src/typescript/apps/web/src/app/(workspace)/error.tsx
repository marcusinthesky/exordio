"use client";

import { Button } from "@exordio/ui/components/button";
import { EmptyState } from "@exordio/ui/patterns/empty-state";

export default function WorkspaceError({ reset }: { reset: () => void }) {
  return (
    <EmptyState
      title="Something interrupted your work"
      description="Your changes may not have been saved. Please try again."
      action={<Button onClick={reset}>Try again</Button>}
    />
  );
}
