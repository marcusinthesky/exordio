---
description: Choose independent workflows, languages and integrations.
---

# Choose only what you need

There are no starter profiles. Workflow and language selections default to empty.
You can select TypeScript alone, references without planning, or Lean without
a manuscript.

## Markdown workflows

| Selection | Adds |
| --- | --- |
| `planning` | Plans, nested tasks, a roadmap and local child views |
| `reference` | Citation records, an index and declared backlinks |

Either selection installs Insitu and the document validators. With neither
selected, the project has no workflow environment or context tree.

Reference records live in `.context/reference/KEY/README.md`. Flat CSL fields
describe the source; the directory supplies its citation key. References plus
LaTeX derive the manuscript bibliography automatically during `just sync`.
Without reference records, LaTeX owns its ordinary `refs.bib` directly.

## Languages

| Selection | First useful result |
| --- | --- |
| `python` | Typed library imported by an application in a locked uv workspace |
| `typescript` | Bun library/CLI, or one fixed full-stack components setup |
| `lean` | Mathlib proofs with LeanArchitect annotations and a LeanBlueprint graph/PDF |
| `latex` | A Tectonic article with cached local builds |

Each language has a local README and namespaced commands. Python and TypeScript
retain their library/application package boundaries. Lean includes its blueprint
tooling even when manuscript LaTeX is absent.

## TypeScript: initialise with components

When TypeScript is selected, **Initialise with components** is one additional
checkbox, disabled by default. It selects the entire application stack together.
There are no separate choices of ORM, authentication library, UI system or test
runner, so Exordio maintains two TypeScript variants.

| Variant | Included |
| --- | --- |
| TypeScript | Bun library and CLI, strict TypeScript, Biome, Knip and Bun tests |
| TypeScript + components | Next.js App Router, React, shared shadcn UI, Tailwind, PostgreSQL/Drizzle, Better Auth, Storybook, Vitest and Playwright |

The components stack also supplies forms with React Hook Form and Zod, tables
with TanStack Table, charts with Recharts, Lucide icons and Sonner notifications.
A working application demonstrates authentication, per-user records, validation,
loading/error states and the shared layout. Storybook catalogs the reusable UI.
Node runs the web framework; Bun owns dependency installation and the lock.

Generated code stays under `src/typescript/`: `apps/web` owns application behavior
and `packages/ui` owns visual components, layouts and central theme tokens.
Storybook lives with the UI package. Framework, database and authentication
imports are prohibited inside reusable UI. No hosted service or paid account
is required for local development; PostgreSQL and Mailpit run through Devenv.

This option is a **development preview**, not included in release `v0.1.0`.
From a checkout containing the feature, preview it in a new directory with:

```bash
just render /tmp/exordio-components -d 'languages=["typescript"]' -d typescript_components=true
```

In the generated project's pinned shell:

```bash
just setup
just dev
```

`just dev` explicitly starts local services, applies committed migrations and
runs the application. The generated TypeScript README documents Storybook,
local email, tests and deployment settings. The full check requires the prepared
local services; setup never creates or migrates production databases.

An existing TypeScript project's variant is intentionally fixed across Copier
updates. See [manual migration](updates.md#switch-typescript-variants) to switch
between the basic and components versions without losing authored code.

## Integrations

AgentSync optionally projects shared instructions into Codex and/or Claude
configuration. Nix builds its pinned Rust CLI; no npm installation is needed.
Its Python preflight stops on authored destinations; migrate those files
deliberately. Without it, the README and agent prompt remain useful; projects may author their own instructions.

SecretSpec optionally resolves declared credentials for `just secret-run COMMAND`.
Shell entry and ordinary checks never load secrets. Configure a provider when a
real project needs one; never put secret values in Copier answers.

Nix supplies the reproducible environment for every project. There is no empty
Terraform/Kubernetes scaffold or automatic deployment.
