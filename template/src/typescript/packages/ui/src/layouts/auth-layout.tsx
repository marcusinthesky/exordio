import type { ReactNode } from "react";

export function AuthLayout({
  brand,
  title,
  description,
  children,
  footer,
}: {
  brand: ReactNode;
  title: string;
  description: string;
  children: ReactNode;
  footer?: ReactNode;
}) {
  return (
    <main className="grid min-h-dvh lg:grid-cols-2">
      <div className="flex flex-col justify-center bg-card px-6 py-12 sm:px-12">
        <div className="mx-auto w-full max-w-sm space-y-8">
          <div className="text-lg font-semibold tracking-tight">{brand}</div>
          <div className="space-y-2">
            <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
            <p className="text-sm leading-6 text-muted-foreground">
              {description}
            </p>
          </div>
          {children}
          {footer && (
            <div className="text-center text-sm text-muted-foreground">
              {footer}
            </div>
          )}
        </div>
      </div>
      <div className="hidden flex-col justify-end border-l bg-sidebar p-12 lg:flex">
        <div className="max-w-lg space-y-4">
          <p className="text-xs font-semibold tracking-widest text-primary uppercase">
            Start with purpose
          </p>
          <h2 className="text-4xl leading-tight font-medium tracking-tight">
            Room for your next
            <br />
            good idea.
          </h2>
          <p className="text-base leading-7 text-muted-foreground">
            A thoughtful workspace for turning the first step into meaningful
            progress.
          </p>
        </div>
      </div>
    </main>
  );
}
