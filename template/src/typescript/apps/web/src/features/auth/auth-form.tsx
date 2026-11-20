"use client";

import { Button } from "@exordio/ui/components/button";
import { Input } from "@exordio/ui/components/input";
import { Label } from "@exordio/ui/components/label";
import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useId, useState } from "react";
import { useForm } from "react-hook-form";
import type { z } from "zod";
import { authClient } from "@/auth/client";
import { registerSchema } from "./schemas";

export function AuthForm({ mode }: { mode: "login" | "register" }) {
  const router = useRouter();
  const id = useId();
  const [message, setMessage] = useState("");
  const [verificationSent, setVerificationSent] = useState(false);
  const isRegister = mode === "register";
  const form = useForm<z.infer<typeof registerSchema>>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: isRegister ? "" : "Returning user",
      email: "",
      password: "",
    },
  });
  const { errors, isSubmitting } = form.formState;

  async function submit(values: z.infer<typeof registerSchema>) {
    setMessage("");
    try {
      const result = isRegister
        ? await authClient.signUp.email({
            ...values,
            callbackURL: "/dashboard",
          })
        : await authClient.signIn.email({
            email: values.email,
            password: values.password,
            callbackURL: "/dashboard",
          });
      if (result.error) {
        if (!isRegister && result.error.code === "EMAIL_NOT_VERIFIED") {
          setMessage(
            "Check your inbox: we've sent a new verification link. Verify your email, then sign in again.",
          );
          return;
        }
        setMessage(
          isRegister
            ? "Unable to create the account. Check your details or try signing in."
            : "Unable to sign in. Check your details and email verification, then try again.",
        );
        return;
      }
      if (isRegister && !result.data?.token) {
        setVerificationSent(true);
        return;
      }
      router.push("/dashboard");
      router.refresh();
    } catch {
      setMessage("We couldn't connect. Please try again.");
    }
  }

  if (verificationSent) {
    return (
      <div className="space-y-4">
        <output className="block text-sm">
          Check your inbox to verify your email before signing in. If the link
          expires, sign in to request a new one.
        </output>
        <Button className="w-full" render={<Link href="/login" />}>
          Go to sign in
        </Button>
      </div>
    );
  }

  return (
    <form onSubmit={form.handleSubmit(submit)} className="space-y-5" noValidate>
      {isRegister && (
        <div className="space-y-2">
          <Label htmlFor={`${id}-name`}>Name</Label>
          <Input
            id={`${id}-name`}
            autoComplete="name"
            aria-invalid={Boolean(errors.name)}
            aria-describedby={errors.name ? `${id}-name-error` : undefined}
            {...form.register("name")}
          />
          {errors.name && (
            <p id={`${id}-name-error`} className="text-sm text-destructive">
              {errors.name.message}
            </p>
          )}
        </div>
      )}
      <div className="space-y-2">
        <Label htmlFor={`${id}-email`}>Email</Label>
        <Input
          id={`${id}-email`}
          type="email"
          autoComplete="email"
          aria-invalid={Boolean(errors.email)}
          aria-describedby={errors.email ? `${id}-email-error` : undefined}
          {...form.register("email")}
        />
        {errors.email && (
          <p id={`${id}-email-error`} className="text-sm text-destructive">
            {errors.email.message}
          </p>
        )}
      </div>
      <div className="space-y-2">
        <Label htmlFor={`${id}-password`}>Password</Label>
        <Input
          id={`${id}-password`}
          type="password"
          autoComplete={isRegister ? "new-password" : "current-password"}
          aria-invalid={Boolean(errors.password)}
          aria-describedby={`${id}-password-help`}
          {...form.register("password")}
        />
        <p
          id={`${id}-password-help`}
          className={
            errors.password
              ? "text-sm text-destructive"
              : "text-sm text-muted-foreground"
          }
        >
          {errors.password?.message ??
            (isRegister
              ? "Use at least 12 characters."
              : "Enter the password for your account.")}
        </p>
      </div>
      {message && (
        <p role="alert" className="text-sm text-destructive">
          {message}
        </p>
      )}
      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting
          ? "Please wait…"
          : isRegister
            ? "Create account"
            : "Sign in"}
      </Button>
      <div className="space-y-3 text-center text-sm text-muted-foreground">
        {!isRegister && (
          <p>
            <Link
              href="/forgot-password"
              className="text-foreground underline underline-offset-4"
            >
              Forgot your password?
            </Link>
          </p>
        )}
        <p>
          {isRegister ? "Already have an account? " : "New here? "}
          <Link
            href={isRegister ? "/login" : "/register"}
            className="font-medium text-foreground underline underline-offset-4"
          >
            {isRegister ? "Sign in" : "Create an account"}
          </Link>
        </p>
      </div>
    </form>
  );
}
