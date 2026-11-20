import type { ReactNode } from "react";
import { Brand } from "@/components/brand";
import { ThemeToggle } from "@/components/theme-toggle";

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-svh bg-muted/30">
      <header className="mx-auto flex h-20 max-w-6xl items-center justify-between px-6">
        <Brand />
        <ThemeToggle />
      </header>
      <main className="mx-auto max-w-md px-6 pb-16 pt-10 sm:pt-20">
        {children}
      </main>
    </div>
  );
}
