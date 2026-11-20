"use client";

import { Button } from "@exordio/ui/components/button";
import { Input } from "@exordio/ui/components/input";
import { Label } from "@exordio/ui/components/label";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useId, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { authClient } from "@/auth/client";

const profileSchema = z.object({
  name: z.string().trim().min(1, "Enter your name.").max(80),
});

export function AccountForm({ name, email }: { name: string; email: string }) {
  const id = useId();
  const router = useRouter();
  const [failed, setFailed] = useState(false);
  const form = useForm<z.infer<typeof profileSchema>>({
    resolver: zodResolver(profileSchema),
    defaultValues: { name },
  });
  async function submit(values: z.infer<typeof profileSchema>) {
    setFailed(false);
    try {
      const result = await authClient.updateUser(values);
      if (result.error) {
        setFailed(true);
        return;
      }
      toast.success("Profile updated");
      router.refresh();
    } catch {
      setFailed(true);
    }
  }
  return (
    <form className="space-y-5" onSubmit={form.handleSubmit(submit)} noValidate>
      <div className="space-y-2">
        <Label htmlFor={`${id}-name`}>Name</Label>
        <Input
          id={`${id}-name`}
          autoComplete="name"
          aria-invalid={Boolean(form.formState.errors.name)}
          {...form.register("name")}
        />
        {form.formState.errors.name && (
          <p role="alert" className="text-sm text-destructive">
            {form.formState.errors.name.message}
          </p>
        )}
      </div>
      <div className="space-y-2">
        <Label htmlFor={`${id}-email`}>Email</Label>
        <Input id={`${id}-email`} value={email} type="email" readOnly />
        <p className="text-sm text-muted-foreground">
          This is the email used to sign in.
        </p>
      </div>
      {failed && (
        <p role="alert" className="text-sm text-destructive">
          Unable to save your profile. Please try again.
        </p>
      )}
      <Button type="submit" disabled={form.formState.isSubmitting}>
        {form.formState.isSubmitting ? "Saving…" : "Save profile"}
      </Button>
    </form>
  );
}
