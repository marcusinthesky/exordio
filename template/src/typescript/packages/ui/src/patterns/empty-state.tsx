import type { ReactNode } from "react";

export function EmptyState({
  title,
  description,
  icon,
  action,
}: {
  title: string;
  description?: string;
  icon?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="flex min-h-64 flex-col items-center justify-center gap-4 rounded-xl border border-dashed bg-card p-8 text-center">
      {icon && (
        <div
          className="flex size-12 items-center justify-center rounded-xl bg-muted text-muted-foreground"
          aria-hidden="true"
        >
          {icon}
        </div>
      )}
      <div className="max-w-sm space-y-2">
        <h2 className="text-base font-semibold">{title}</h2>
        {description && (
          <p className="text-sm leading-6 text-muted-foreground">
            {description}
          </p>
        )}
      </div>
      {action}
    </div>
  );
}
