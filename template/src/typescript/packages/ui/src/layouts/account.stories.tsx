import type { Meta, StoryObj } from "@storybook/react-vite";
import { SparklesIcon } from "lucide-react";
import { Button } from "../components/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../components/card";
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
} from "../components/field";
import { Input } from "../components/input";
import { AuthLayout } from "./auth-layout";
import { PageHeader } from "./page-header";
import { SettingsLayout } from "./settings-layout";

const meta = { title: "Layouts/Account" } satisfies Meta;
export default meta;
type Story = StoryObj<typeof meta>;

export const SignIn: Story = {
  render: () => (
    <AuthLayout
      brand={
        <span className="flex items-center gap-2">
          <SparklesIcon className="size-5 text-primary" aria-hidden="true" />
          Exordio
        </span>
      }
      title="Welcome back"
      description="Sign in to your workspace and pick up where you left off."
      footer={
        <p>
          New here?{" "}
          <a
            className="font-medium text-primary underline underline-offset-4"
            href="#create-account"
          >
            Create an account
          </a>
        </p>
      }
    >
      <form onSubmit={(event) => event.preventDefault()}>
        <FieldGroup>
          <Field>
            <FieldLabel htmlFor="sign-in-email">Email address</FieldLabel>
            <Input
              id="sign-in-email"
              type="email"
              autoComplete="email"
              placeholder="you@example.com"
            />
          </Field>
          <Field>
            <FieldLabel htmlFor="sign-in-password">Password</FieldLabel>
            <Input
              id="sign-in-password"
              type="password"
              autoComplete="current-password"
            />
          </Field>
          <Button type="submit" className="w-full">
            Sign in
          </Button>
        </FieldGroup>
      </form>
    </AuthLayout>
  ),
};

export const Settings: Story = {
  render: () => (
    <main className="mx-auto max-w-5xl space-y-8 p-8">
      <PageHeader
        title="Settings"
        description="Your workspace, your preferences."
      />
      <SettingsLayout
        navigation={
          <>
            <a
              href="#profile"
              aria-current="page"
              className="rounded-lg bg-accent px-3 py-2 text-sm font-medium text-accent-foreground"
            >
              Profile
            </a>
            <a
              href="#preferences"
              className="rounded-lg px-3 py-2 text-sm text-muted-foreground"
            >
              Preferences
            </a>
            <a
              href="#security"
              className="rounded-lg px-3 py-2 text-sm text-muted-foreground"
            >
              Security
            </a>
          </>
        }
      >
        <Card>
          <CardHeader>
            <CardTitle>Profile</CardTitle>
            <CardDescription>
              Manage how you appear in the workspace.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <FieldGroup>
              <Field>
                <FieldLabel htmlFor="profile-name">Full name</FieldLabel>
                <Input id="profile-name" defaultValue="Alex Chen" />
              </Field>
              <Field>
                <FieldLabel htmlFor="profile-email">Email</FieldLabel>
                <Input
                  id="profile-email"
                  type="email"
                  defaultValue="alex@example.com"
                />
                <FieldDescription>
                  Used for account notifications.
                </FieldDescription>
              </Field>
            </FieldGroup>
          </CardContent>
          <CardFooter className="justify-end">
            <Button>Save changes</Button>
          </CardFooter>
        </Card>
      </SettingsLayout>
    </main>
  ),
};
