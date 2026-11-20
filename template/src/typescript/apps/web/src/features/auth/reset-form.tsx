"use client";

import { Button } from "@exordio/ui/components/button";
import { Input } from "@exordio/ui/components/input";
import { Label } from "@exordio/ui/components/label";
import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useId, useState } from "react";
import { useForm } from "react-hook-form";
import type { z } from "zod";
import { authClient } from "@/auth/client";
import { resetPasswordSchema, resetRequestSchema } from "./schemas";

export function ResetRequestForm() {
  const id = useId();
  const [sent, setSent] = useState(false);
  const [failed, setFailed] = useState(false);
  const form = useForm<z.infer<typeof resetRequestSchema>>({
    resolver: zodResolver(resetRequestSchema),
    defaultValues: { email: "" },
  });
  async function submit(values: z.infer<typeof resetRequestSchema>) {
    setFailed(false);
    try {
      const result = await authClient.requestPasswordReset({
        email: values.email,
        redirectTo: "/reset-password",
      });
      if (result.error) {
        setFailed(true);
        return;
      }
      setSent(true);
    } catch {
      setFailed(true);
    }
  }
  if (sent)
    return (
      <div className="space-y-4">
        <output className="block text-sm">
          If an account exists for that address, you'll receive a password reset
          link.
        </output>
        <Button
          variant="outline"
          className="w-full"
          render={<Link href="/login" />}
        >
          Back to sign in
        </Button>
      </div>
    );
  return (
    <form onSubmit={form.handleSubmit(submit)} className="space-y-5" noValidate>
      <div className="space-y-2">
        <Label htmlFor={id}>Email</Label>
        <Input
          id={id}
          type="email"
          autoComplete="email"
          aria-invalid={Boolean(form.formState.errors.email)}
          {...form.register("email")}
        />
        {form.formState.errors.email && (
          <p role="alert" className="text-sm text-destructive">
            {form.formState.errors.email.message}
          </p>
        )}
      </div>
      {failed && (
        <p role="alert" className="text-sm text-destructive">
          Unable to send a reset link. Please try again.
        </p>
      )}
      <Button
        type="submit"
        className="w-full"
        disabled={form.formState.isSubmitting}
      >
        {form.formState.isSubmitting ? "Sending…" : "Send reset link"}
      </Button>
      <p className="text-center text-sm">
        <Link href="/login" className="underline underline-offset-4">
          Back to sign in
        </Link>
      </p>
    </form>
  );
}

export function ResetPasswordForm({ token }: { token: string }) {
  const id = useId();
  const [done, setDone] = useState(false);
  const [failed, setFailed] = useState(false);
  const form = useForm<z.infer<typeof resetPasswordSchema>>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: { password: "" },
  });
  async function submit(values: z.infer<typeof resetPasswordSchema>) {
    setFailed(false);
    try {
      const result = await authClient.resetPassword({
        newPassword: values.password,
        token,
      });
      if (result.error) {
        setFailed(true);
        return;
      }
      setDone(true);
    } catch {
      setFailed(true);
    }
  }
  if (done)
    return (
      <div className="space-y-4">
        <output className="block text-sm">
          Your password has been changed. Sign in with your new password.
        </output>
        <Button className="w-full" render={<Link href="/login" />}>
          Sign in
        </Button>
      </div>
    );
  if (!token)
    return (
      <p className="text-sm">
        This reset link is missing or expired.{" "}
        <Link href="/forgot-password" className="underline underline-offset-4">
          Request another link
        </Link>
        .
      </p>
    );
  return (
    <form onSubmit={form.handleSubmit(submit)} className="space-y-5" noValidate>
      <div className="space-y-2">
        <Label htmlFor={id}>New password</Label>
        <Input
          id={id}
          type="password"
          autoComplete="new-password"
          aria-invalid={Boolean(form.formState.errors.password)}
          {...form.register("password")}
        />
        <p className="text-sm text-muted-foreground">
          At least 12 characters. Existing sessions will be signed out.
        </p>
        {form.formState.errors.password && (
          <p role="alert" className="text-sm text-destructive">
            {form.formState.errors.password.message}
          </p>
        )}
      </div>
      {failed && (
        <p role="alert" className="text-sm text-destructive">
          This link may have expired. Request a new one and try again.
        </p>
      )}
      <Button
        type="submit"
        className="w-full"
        disabled={form.formState.isSubmitting}
      >
        {form.formState.isSubmitting ? "Updating…" : "Set new password"}
      </Button>
    </form>
  );
}
