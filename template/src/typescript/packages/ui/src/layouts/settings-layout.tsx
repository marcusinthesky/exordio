import type { ReactNode } from "react";

export function SettingsLayout({
  navigation,
  children,
}: {
  navigation: ReactNode;
  children: ReactNode;
}) {
  return (
    <div className="grid gap-8 lg:grid-cols-[12rem_minmax(0,1fr)]">
      <nav
        aria-label="Settings"
        className="flex gap-2 overflow-x-auto lg:flex-col"
      >
        {navigation}
      </nav>
      <div className="min-w-0 space-y-6">{children}</div>
    </div>
  );
}
