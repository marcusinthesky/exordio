import { AuthForm } from "@/features/auth/auth-form";
import { AuthFrame } from "@/features/auth/auth-frame";

export const metadata = { title: "Create account" };

export default function RegisterPage() {
  return (
    <AuthFrame
      title="A good beginning"
      description="Create your account and make room for your next idea."
    >
      <AuthForm mode="register" />
    </AuthFrame>
  );
}
