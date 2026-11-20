# Web application contract

Read README.md and the TypeScript workspace README before changing this app.
Reuse `@exordio/ui` primitives, layouts, patterns, and semantic Tailwind tokens.
Keep routes thin; feature validation, actions, and presentation live together
under `src/features/`. Shared UI must not import from this application.

Use React Server Components for reads. Every protected page and every server
mutation validates the session. Scope database reads, updates, and deletes to
that user's ID; never accept ownership from client input. Validate mutations
with Zod even when a form already validated them. Treat database errors as
private; return an actionable, nonsensitive message.

Keep database and authentication modules server-only. Read secrets through
`getServerEnvironment()` when needed, never at build time or in shared UI.
Preserve Better Auth origin checks, password validation, secure production
cookies, database rate limiting, and recovery email handling.

Generate and review Drizzle migrations explicitly. Never run schema push,
migrations, seed data, dependency installs, or snapshot updates during checks.
Tests and builds must not need an external account or fetch fonts.

Run the workspace's `just typescript::check` before handoff. Use the existing
registration, project CRUD, ownership, and recovery tests as the reference for
new features. Keep stories and visual tests with shared UI.
