# UI contract

Read README.md and find an existing component or story before adding UI.
Use semantic Tailwind tokens from src/styles; change branding in tokens.css.
Keep Base UI as the single behavior foundation. Preserve keyboard and focus logic.
Use direct package exports. Do not import apps, Next.js, auth or database modules.
Accept data, callbacks and rendered links; applications own business behavior.
Keep stories beside source. Cover important states, mobile layout and keyboard behavior.
Use deterministic data and local fonts. Never load production services in stories.
Run typecheck, Storybook interactions/accessibility and applicable visual checks.
Do not update screenshots during checks. Review intended changes before updating baselines.
Preserve LICENSE.shadcn and the source provenance when adapting upstream components.
