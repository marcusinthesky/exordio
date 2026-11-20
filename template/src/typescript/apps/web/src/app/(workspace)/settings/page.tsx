import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@exordio/ui/components/card";
import { PageHeader } from "@exordio/ui/layouts/page-header";
import { requireUser } from "@/auth/session";
import { AccountForm } from "@/features/auth/account-form";

export const metadata = { title: "Settings" };

export default async function SettingsPage() {
  const user = await requireUser();
  return (
    <div className="max-w-2xl space-y-8">
      <PageHeader
        title="Settings"
        description="Make this workspace feel like yours."
      />
      <Card>
        <CardHeader>
          <CardTitle>Profile</CardTitle>
          <CardDescription>
            Your name is how you'll appear in the workspace.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <AccountForm name={user.name} email={user.email} />
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Account security</CardTitle>
          <CardDescription>
            Password reset links are sent to your account email.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <a
            href="/forgot-password"
            className="text-sm font-medium underline underline-offset-4"
          >
            Reset your password
          </a>
        </CardContent>
      </Card>
    </div>
  );
}
