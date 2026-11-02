---
description: A locked Bun workspace with a shared TypeScript library and runnable app.
---

# TypeScript

`packages/core` exports a typed function; `apps/example-app` consumes it through a
workspace dependency. Bun runs and tests the application directly. TypeScript
checks the whole workspace, and Biome handles formatting and lint.

```bash
just typescript::setup
just typescript::run Ada
just typescript::check
```

Setup installs the committed lock without rewriting it. Checks invoke installed
tools and do not fetch packages. Builds write an executable Bun bundle to ignored
`dist/`. Add packages under `packages/` and apps under `apps/`; update `bun.lock`
explicitly when changing their dependencies. The example identifiers are stable
so their complete lock can be shared by every generated project.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the package boundary.
