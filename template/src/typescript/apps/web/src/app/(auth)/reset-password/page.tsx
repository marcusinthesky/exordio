import { AuthFrame } from "@/features/auth/auth-frame";
import { ResetPasswordForm } from "@/features/auth/reset-form";

export const metadata = { title: "Choose a password" };

export default async function ResetPasswordPage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string }>;
}) {
  const { token } = await searchParams;
  return (
    <AuthFrame
      title="A fresh start"
      description="Choose a new password to secure your account."
    >
      <ResetPasswordForm token={token ?? ""} />
    </AuthFrame>
  );
}
