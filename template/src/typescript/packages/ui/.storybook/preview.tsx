import type { Preview } from "@storybook/react-vite";
import { TooltipProvider } from "../src/components/tooltip";
import "../src/styles/globals.css";

const preview: Preview = {
  globalTypes: {
    theme: {
      description: "Shared application color scheme",
      toolbar: {
        icon: "circlehollow",
        items: ["light", "dark"],
        dynamicTitle: true,
      },
    },
  },
  initialGlobals: { theme: "light" },
  decorators: [
    (Story, context) => {
      const theme = context.globals.theme === "dark" ? "dark" : "light";
      // Portal-based menus/dialogs share the same theme as the canvas.
      document.documentElement.classList.toggle("dark", theme === "dark");
      document.documentElement.style.colorScheme = theme;
      return (
        <TooltipProvider>
          <div className="min-h-screen bg-background text-foreground">
            <Story />
          </div>
        </TooltipProvider>
      );
    },
  ],
  parameters: {
    layout: "fullscreen",
    a11y: { test: "error" },
    backgrounds: { disable: true },
    controls: { matchers: { color: /(background|color)$/i, date: /Date$/i } },
    options: {
      storySort: {
        order: ["Foundations", "Components", "Layouts", "Patterns"],
      },
    },
  },
  tags: ["autodocs"],
};

export default preview;
