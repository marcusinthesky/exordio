---
description: One shared visual language for components, layouts and application states.
---

# UI system

This private React package contains the application's presentation primitives,
layouts and interaction patterns. The Next.js application supplies data, routes,
authentication and authorization. Storybook supplies deterministic examples.
Both consumers render the same component source and Tailwind stylesheet.

## Discover before building

From the project root:

```bash
just typescript::storybook
just typescript::test-stories
just typescript::test-visual
```

Storybook includes foundations, light/dark previews, form states, overlays,
dashboard and account layouts, data-table interactions, notifications and
confirmation flows. Interaction and accessibility checks execute in a real
Chromium browser. Browser installation belongs to explicit setup; checks do not
download dependencies or update screenshot baselines.

## Package boundary

| Directory | Owns |
| --- | --- |
| `src/components/` | shadcn/Base UI primitives, the data table and chart infrastructure |
| `src/layouts/` | Application shell, page header, settings and authentication compositions |
| `src/patterns/` | Empty/error states, confirmation, metrics and activity charts |
| `src/styles/` | Semantic colors, typography, radii, page width and shared Tailwind CSS |
| Colocated stories | States, usage examples and interaction checks |

Use direct imports such as `@exordio/ui/components/button`. The package exports
source, so Next.js transpiles it and Vite renders it without a separate UI build.
React is a peer dependency. Import `@exordio/ui/styles.css` once per consumer and
declare that consumer's Tailwind source directory in its entry stylesheet.

Presentation components can receive callbacks and rendered links. They must not
import `next`, database clients, authentication or application modules. Connect
those concerns in the application. A server-side page can pass plain data into a
client-side feature component, which then composes the table, dialog and forms.

## Theme centrally

Edit [tokens.css](src/styles/tokens.css) for branding and light/dark colors.
[globals.css](src/styles/globals.css) maps those values to Tailwind utilities.
Use semantic classes such as `bg-card`, `text-muted-foreground` and `border-input`.
New layouts should use the existing spacing, typography and page-width conventions.
The local Inter font is installed from a pinned package; builds never fetch fonts.

Color, radius and font changes should be reviewed against the light/dark foundation
stories and mobile/desktop layout snapshots. Automated accessibility checks are
useful regressions; keyboard and screen-reader review remain part of significant
interaction changes.

## Add or update components

The committed components come from the official `base-nova` shadcn registry and
use Base UI consistently. [UPSTREAM.json](UPSTREAM.json) records source hashes;
[LICENSE.shadcn](LICENSE.shadcn) preserves the upstream MIT notice. These are local
sources with small workspace, icon, theme and strict-typing adaptations.

Use the pinned local shadcn CLI from this package to add a component explicitly:

```bash
bun run --cwd src/typescript/packages/ui shadcn add calendar
```

Run additions from the generated repository, review the new source and dependency
changes, and refresh the lock intentionally. Keep `components.json` aligned with
the package exports. If a component introduces shared hooks, add an explicit
`./hooks/*` source export when that directory first exists. Do not mix another
component base or a separate theming
system into this package. Renovate updates dependencies; it does not synchronize
vendored component source. Upstream component changes require review, stories,
interaction tests and visual baseline review.

Add a story for reusable behavior or a visible state. Prefer a focused test of
keyboard interaction, validation or focus management over a test that merely
renders a component. Keep application-specific forms and database operations in
the app even when their presentation uses this package.
