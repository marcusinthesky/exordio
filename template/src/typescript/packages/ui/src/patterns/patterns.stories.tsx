import type { Meta, StoryObj } from "@storybook/react-vite";
import { FolderIcon } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { expect, userEvent, waitFor, within } from "storybook/test";
import { Button } from "../components/button";
import { DataTable } from "../components/data-table";
import { Toaster } from "../components/sonner";
import { ConfirmationDialog } from "./confirmation-dialog";
import { EmptyState } from "./empty-state";
import { ErrorState } from "./error-state";

const meta = {
  title: "Patterns/Feedback",
  decorators: [
    (Story) => (
      <main className="mx-auto max-w-3xl space-y-6 p-8">
        <Story />
      </main>
    ),
  ],
} satisfies Meta;
export default meta;
type Story = StoryObj<typeof meta>;

export const Empty: Story = {
  render: () => (
    <EmptyState
      icon={<FolderIcon />}
      title="No projects yet"
      description="Your next idea belongs here. Give it a name and take the first step."
      action={<Button>Create a project</Button>}
    />
  ),
};
export const Failure: Story = {
  render: () => (
    <ErrorState
      description="We couldn't load your projects. Your changes are safe."
      action={<Button variant="outline">Try again</Button>}
    />
  ),
};

function Confirmation() {
  const [open, setOpen] = useState(false);
  const [deleted, setDeleted] = useState(false);
  return (
    <div className="space-y-4">
      <ConfirmationDialog
        trigger="Delete project"
        title="Delete this project?"
        description="This action cannot be undone. All project records will be removed."
        confirmLabel="Delete permanently"
        open={open}
        onOpenChange={setOpen}
        onConfirm={() => {
          setDeleted(true);
          setOpen(false);
        }}
      />
      {deleted && <output>Project deleted.</output>}
    </div>
  );
}

export const Confirm: Story = {
  render: () => <Confirmation />,
  async play({ canvasElement }) {
    await userEvent.click(
      within(canvasElement).getByRole("button", { name: "Delete project" }),
    );
    await userEvent.click(
      await within(canvasElement.ownerDocument.body).findByRole("button", {
        name: "Delete permanently",
      }),
    );
    await expect(
      await within(canvasElement).findByRole("status"),
    ).toHaveTextContent("Project deleted.");
  },
};

export const Notification: Story = {
  beforeEach() {
    toast.dismiss();
    return () => {
      toast.dismiss();
    };
  },
  render: (_args, { globals }) => (
    <>
      <Toaster
        theme={globals.theme === "dark" ? "dark" : "light"}
        richColors
        expand
        visibleToasts={5}
        duration={Number.POSITIVE_INFINITY}
      />
      <Button
        onClick={() => {
          toast("Your workspace is ready.");
          toast.success("Your changes have been saved.");
          toast.info("A project update is available.");
          toast.warning("Your session expires soon.");
          toast.error("We couldn't save your changes.");
        }}
      >
        Show notifications
      </Button>
    </>
  ),
  async play({ canvasElement }) {
    await userEvent.click(
      within(canvasElement).getByRole("button", { name: "Show notifications" }),
    );
    const body = within(canvasElement.ownerDocument.body);
    for (const message of [
      "Your workspace is ready.",
      "Your changes have been saved.",
      "A project update is available.",
      "Your session expires soon.",
      "We couldn't save your changes.",
    ]) {
      const notification = await body.findByText(message);
      await waitFor(() => expect(notification).toBeVisible());
    }
  },
};

export const NotificationDark: Story = {
  ...Notification,
  globals: { theme: "dark" },
};

export const SearchAndSort: Story = {
  render: () => (
    <DataTable
      searchColumn="name"
      columns={[
        { accessorKey: "name", header: "Project" },
        { accessorKey: "status", header: "Status" },
      ]}
      data={[
        { name: "Website refresh", status: "Active" },
        { name: "Research", status: "Planned" },
      ]}
    />
  ),
  async play({ canvasElement }) {
    const canvas = within(canvasElement);
    await userEvent.type(
      canvas.getByRole("textbox", { name: "Search records" }),
      "Website",
    );
    await expect(canvas.getByText("Website refresh")).toBeVisible();
    await expect(canvas.queryByText("Research")).not.toBeInTheDocument();
    await userEvent.clear(
      canvas.getByRole("textbox", { name: "Search records" }),
    );
    await userEvent.click(canvas.getByRole("button", { name: "Project" }));
    await expect(canvas.getAllByRole("row")[1]).toHaveTextContent("Research");
  },
};
