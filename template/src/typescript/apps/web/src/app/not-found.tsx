import { Button } from "@exordio/ui/components/button";
import { EmptyState } from "@exordio/ui/patterns/empty-state";
import Link from "next/link";

export default function NotFound() {
  return (
    <main className="flex min-h-svh items-center justify-center px-6">
      <EmptyState
        title="This page has moved on"
        description="Check the address, or start again from your workspace."
        action={
          <Button render={<Link href="/dashboard" />}>
            Go to your workspace
          </Button>
        }
      />
    </main>
  );
}
