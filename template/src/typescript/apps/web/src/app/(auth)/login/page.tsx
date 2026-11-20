import { AuthForm } from "@/features/auth/auth-form";
import { AuthFrame } from "@/features/auth/auth-frame";

export const metadata = { title: "Sign in" };

export default function LoginPage() {
  return (
    <AuthFrame
      title="Welcome back"
      description="Sign in to pick up where you left off."
    >
      <AuthForm mode="login" />
    </AuthFrame>
  );
}
