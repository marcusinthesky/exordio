import { AuthFrame } from "@/features/auth/auth-frame";
import { ResetRequestForm } from "@/features/auth/reset-form";

export const metadata = { title: "Reset password" };

export default function ForgotPasswordPage() {
  return (
    <AuthFrame
      title="Forgot your password?"
      description="We'll send you a link to choose a new one."
    >
      <ResetRequestForm />
    </AuthFrame>
  );
}
