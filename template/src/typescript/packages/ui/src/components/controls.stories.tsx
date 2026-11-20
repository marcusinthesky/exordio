import type { Meta, StoryObj } from "@storybook/react-vite";
import { useState } from "react";
import { expect, userEvent, within } from "storybook/test";
import { Button } from "./button";
import { Checkbox } from "./checkbox";
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "./field";
import { Input } from "./input";
import { Label } from "./label";
import { RadioGroup, RadioGroupItem } from "./radio-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./select";
import { Separator } from "./separator";
import { Slider } from "./slider";
import { Switch } from "./switch";
import { Textarea } from "./textarea";

function Controls() {
  const [enabled, setEnabled] = useState(true);
  return (
    <main className="mx-auto max-w-xl space-y-8 p-8">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold">Form controls</h1>
        <p className="text-sm text-muted-foreground">
          Shared labels, descriptions and keyboard behavior.
        </p>
      </div>
      <FieldGroup>
        <Field>
          <FieldLabel htmlFor="project-name">Project name</FieldLabel>
          <Input id="project-name" defaultValue="A good beginning" />
          <FieldDescription>
            A clear name helps your team find its work.
          </FieldDescription>
        </Field>
        <Field>
          <FieldLabel htmlFor="project-description">Description</FieldLabel>
          <Textarea
            id="project-description"
            placeholder="What would you like to achieve?"
          />
        </Field>
        <Field data-invalid>
          <FieldLabel htmlFor="invalid-email">Contact email</FieldLabel>
          <Input
            id="invalid-email"
            aria-invalid="true"
            aria-describedby="email-error"
            defaultValue="invalid"
          />
          <FieldError id="email-error">Enter a valid email address.</FieldError>
        </Field>
        <Field>
          <FieldLabel htmlFor="disabled-field">Workspace ID</FieldLabel>
          <Input
            id="disabled-field"
            disabled
            defaultValue="workspace-example"
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="project-status">Status</FieldLabel>
          <Select
            defaultValue="planned"
            items={[
              { label: "Planned", value: "planned" },
              { label: "Active", value: "active" },
              { label: "Done", value: "done" },
            ]}
          >
            <SelectTrigger id="project-status" className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="planned">Planned</SelectItem>
              <SelectItem value="active">Active</SelectItem>
              <SelectItem value="done">Done</SelectItem>
            </SelectContent>
          </Select>
        </Field>
        <Separator />
        <div className="flex items-center gap-3">
          <Checkbox id="updates" />
          <Label htmlFor="updates">Send project updates</Label>
        </div>
        <div className="flex items-center justify-between gap-4">
          <Label htmlFor="notifications">Notifications</Label>
          <Switch
            id="notifications"
            checked={enabled}
            onCheckedChange={setEnabled}
          />
        </div>
        <fieldset className="space-y-3">
          <legend id="visibility-label" className="mb-3 text-sm font-medium">
            Project visibility
          </legend>
          <RadioGroup defaultValue="private" aria-labelledby="visibility-label">
            <div className="flex items-center gap-3">
              <RadioGroupItem value="private" id="private" />
              <Label htmlFor="private">Private</Label>
            </div>
            <div className="flex items-center gap-3">
              <RadioGroupItem value="team" id="team" />
              <Label htmlFor="team">Team</Label>
            </div>
          </RadioGroup>
        </fieldset>
        <Field>
          <FieldLabel id="priority-label">Priority</FieldLabel>
          <Slider
            aria-labelledby="priority-label"
            defaultValue={[50]}
            max={100}
            step={10}
          />
        </Field>
        <div>
          <Button>Save preferences</Button>
        </div>
      </FieldGroup>
    </main>
  );
}

const meta = {
  title: "Components/Form controls",
  component: Controls,
} satisfies Meta<typeof Controls>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  async play({ canvasElement }) {
    const canvas = within(canvasElement);
    const name = canvas.getByRole("textbox", { name: "Project name" });
    await userEvent.clear(name);
    await userEvent.type(name, "Updated project");
    await expect(name).toHaveValue("Updated project");
    const updates = canvas.getByRole("checkbox", {
      name: "Send project updates",
    });
    await userEvent.click(updates);
    await expect(updates).toBeChecked();
    const toggle = canvas.getByRole("switch", { name: "Notifications" });
    await userEvent.click(toggle);
    await expect(toggle).not.toBeChecked();
  },
};

export const Dark: Story = { globals: { theme: "dark" } };
