import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@exordio/ui/components/card";
import type { ReactNode } from "react";

export function AuthFrame({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: ReactNode;
}) {
  return (
    <Card>
      <CardHeader className="space-y-2">
        <CardTitle>
          <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        </CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}
