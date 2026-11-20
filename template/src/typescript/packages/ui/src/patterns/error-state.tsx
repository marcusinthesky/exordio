import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@exordio/ui/components/alert";
import { AlertCircleIcon } from "lucide-react";
import type { ReactNode } from "react";

export function ErrorState({
  title = "Something went wrong",
  description,
  action,
}: {
  title?: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <Alert variant="destructive">
      <AlertCircleIcon aria-hidden="true" />
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription>
        <p>{description}</p>
        {action}
      </AlertDescription>
    </Alert>
  );
}
