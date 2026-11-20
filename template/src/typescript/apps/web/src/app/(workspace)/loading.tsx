import { Skeleton } from "@exordio/ui/components/skeleton";

export default function WorkspaceLoading() {
  return (
    <div aria-busy="true" className="space-y-8">
      <output className="sr-only">Loading your workspace…</output>
      <Skeleton className="h-9 w-48" />
      <div className="grid gap-4 sm:grid-cols-3">
        {[0, 1, 2].map((key) => (
          <Skeleton key={key} className="h-28 rounded-xl" />
        ))}
      </div>
      <Skeleton className="h-80 rounded-xl" />
    </div>
  );
}
