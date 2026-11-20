import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, userEvent, waitFor, within } from "storybook/test";
import { Button } from "./button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./dropdown-menu";
import {
  Popover,
  PopoverContent,
  PopoverDescription,
  PopoverHeader,
  PopoverTitle,
  PopoverTrigger,
} from "./popover";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "./sheet";
import { Tooltip, TooltipContent, TooltipTrigger } from "./tooltip";

function Overlays() {
  return (
    <main className="space-y-6 p-8">
      <h1 className="text-2xl font-semibold">Overlays and navigation</h1>
      <div className="flex flex-wrap gap-3">
        <Dialog>
          <DialogTrigger render={<Button />}>Open dialog</DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Keep changes?</DialogTitle>
              <DialogDescription>
                Your work remains private until you share it.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <DialogClose render={<Button variant="outline" />}>
                Cancel
              </DialogClose>
              <DialogClose render={<Button />}>Save changes</DialogClose>
            </DialogFooter>
          </DialogContent>
        </Dialog>
        <Sheet>
          <SheetTrigger render={<Button variant="outline" />}>
            Open panel
          </SheetTrigger>
          <SheetContent>
            <SheetHeader>
              <SheetTitle>Project details</SheetTitle>
              <SheetDescription>
                Review context without leaving your work.
              </SheetDescription>
            </SheetHeader>
            <p className="px-4 text-sm text-muted-foreground">
              Panels work with keyboard navigation and restore focus when
              closed.
            </p>
          </SheetContent>
        </Sheet>
        <DropdownMenu>
          <DropdownMenuTrigger render={<Button variant="outline" />}>
            Project menu
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuGroup>
              <DropdownMenuLabel>Project actions</DropdownMenuLabel>
              <DropdownMenuItem>Edit project</DropdownMenuItem>
              <DropdownMenuItem>Duplicate</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem variant="destructive">Archive</DropdownMenuItem>
            </DropdownMenuGroup>
          </DropdownMenuContent>
        </DropdownMenu>
        <Popover>
          <PopoverTrigger render={<Button variant="outline" />}>
            Show details
          </PopoverTrigger>
          <PopoverContent>
            <PopoverHeader>
              <PopoverTitle>Working together</PopoverTitle>
              <PopoverDescription>
                Contextual information stays close to its trigger.
              </PopoverDescription>
            </PopoverHeader>
          </PopoverContent>
        </Popover>
        <Tooltip>
          <TooltipTrigger render={<Button variant="ghost" />}>
            Help
          </TooltipTrigger>
          <TooltipContent>Keyboard shortcuts and quick help</TooltipContent>
        </Tooltip>
      </div>
    </main>
  );
}

const meta = {
  title: "Components/Overlays",
  component: Overlays,
} satisfies Meta<typeof Overlays>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  async play({ canvasElement }) {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);
    const trigger = canvas.getByRole("button", { name: "Open dialog" });
    await userEvent.click(trigger);
    await expect(
      await body.findByRole("dialog", { name: "Keep changes?" }),
    ).toBeVisible();
    await userEvent.keyboard("{Escape}");
    await waitFor(() =>
      expect(
        body.queryByRole("dialog", { name: "Keep changes?" }),
      ).not.toBeInTheDocument(),
    );
    await expect(trigger).toHaveFocus();
    await userEvent.click(canvas.getByRole("button", { name: "Project menu" }));
    await expect(
      await body.findByRole("menuitem", { name: "Edit project" }),
    ).toBeVisible();
    await userEvent.keyboard("{Escape}");
  },
};

export const DialogOpen: Story = {
  render: () => (
    <main className="p-8">
      <Dialog open>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Keep changes?</DialogTitle>
            <DialogDescription>
              Your work remains private until you share it.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline">Cancel</Button>
            <Button>Save changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </main>
  ),
};
