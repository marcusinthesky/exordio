import { AppShell } from "@exordio/ui/layouts/app-shell";
import { FolderKanban, Settings } from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";
import { requireUser } from "@/auth/session";
import { Brand } from "@/components/brand";
import { ThemeToggle } from "@/components/theme-toggle";
import { UserMenu } from "@/components/user-menu";

export const dynamic = "force-dynamic";

export default async function WorkspaceLayout({
  children,
}: {
  children: ReactNode;
}) {
  const user = await requireUser();
  const linkClass =
    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:ring-2 focus-visible:ring-ring";
  return (
    <AppShell
      brand={<Brand />}
      navigation={
        <>
          <Link href="/dashboard" className={linkClass}>
            <FolderKanban className="size-4" aria-hidden="true" />
            Projects
          </Link>
          <Link href="/settings" className={linkClass}>
            <Settings className="size-4" aria-hidden="true" />
            Settings
          </Link>
        </>
      }
      actions={
        <>
          <ThemeToggle />
          <UserMenu name={user.name} />
        </>
      }
    >
      {children}
    </AppShell>
  );
}
