"use client";

import { Button } from "@exordio/ui/components/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@exordio/ui/components/sheet";
import { MenuIcon } from "lucide-react";
import { type ReactNode, useState } from "react";

type AppShellProps = {
  brand: ReactNode;
  navigation: ReactNode;
  actions?: ReactNode;
  children: ReactNode;
};

/** Applications supply links and session actions; the shell owns only layout. */
export function AppShell({
  brand,
  navigation,
  actions,
  children,
}: AppShellProps) {
  const [open, setOpen] = useState(false);
  return (
    <div className="min-h-dvh bg-background">
      <a
        href="#main-content"
        className="sr-only fixed top-3 left-3 z-[100] rounded-lg bg-primary px-4 py-2 text-primary-foreground focus:not-sr-only"
      >
        Skip to content
      </a>
      <aside className="fixed inset-y-0 left-0 hidden w-(--sidebar-width) flex-col border-r bg-sidebar text-sidebar-foreground md:flex">
        <div className="flex h-16 items-center border-b px-6 font-semibold tracking-tight">
          {brand}
        </div>
        <nav
          aria-label="Main navigation"
          className="flex flex-1 flex-col gap-1 p-4"
        >
          {navigation}
        </nav>
        <p className="border-t px-6 py-4 text-xs text-muted-foreground">
          A place for good beginnings.
        </p>
      </aside>
      <div className="md:pl-(--sidebar-width)">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between gap-3 border-b bg-background/95 px-4 backdrop-blur-sm md:px-8">
          <div className="flex items-center gap-3">
            <Sheet open={open} onOpenChange={setOpen}>
              <SheetTrigger
                render={
                  <Button variant="ghost" size="icon" className="md:hidden" />
                }
              >
                <MenuIcon aria-hidden="true" />
                <span className="sr-only">Open navigation</span>
              </SheetTrigger>
              <SheetContent
                side="left"
                className="w-(--sidebar-width) bg-sidebar"
                onClick={(event) => {
                  if (
                    event.target instanceof Element &&
                    event.target.closest("a")
                  )
                    setOpen(false);
                }}
              >
                <SheetHeader>
                  <SheetTitle>{brand}</SheetTitle>
                  <SheetDescription className="sr-only">
                    Application navigation
                  </SheetDescription>
                </SheetHeader>
                <nav
                  aria-label="Mobile navigation"
                  className="flex flex-col gap-1 p-4"
                >
                  {navigation}
                </nav>
              </SheetContent>
            </Sheet>
            <span className="text-sm font-medium text-muted-foreground">
              Workspace
            </span>
          </div>
          <div className="flex items-center gap-2">{actions}</div>
        </header>
        <main
          id="main-content"
          tabIndex={-1}
          className="mx-auto w-full max-w-(--page-width) space-y-8 p-4 outline-none md:p-8"
        >
          {children}
        </main>
      </div>
    </div>
  );
}
