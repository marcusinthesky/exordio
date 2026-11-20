"use client";

import { Button } from "@exordio/ui/components/button";
import { LogOut } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";
import { authClient } from "@/auth/client";

export function UserMenu({ name }: { name: string }) {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  async function signOut() {
    setPending(true);
    try {
      const result = await authClient.signOut();
      if (result.error) {
        toast.error("Unable to sign out. Please try again.");
        return;
      }
      router.push("/login");
      router.refresh();
    } catch {
      toast.error("Unable to sign out. Please try again.");
    } finally {
      setPending(false);
    }
  }
  return (
    <div className="flex items-center gap-3">
      <span className="hidden max-w-40 truncate text-sm text-muted-foreground sm:block">
        {name}
      </span>
      <Button
        size="icon"
        variant="ghost"
        aria-label="Sign out"
        disabled={pending}
        onClick={signOut}
      >
        <LogOut className="size-4" aria-hidden="true" />
      </Button>
    </div>
  );
}
