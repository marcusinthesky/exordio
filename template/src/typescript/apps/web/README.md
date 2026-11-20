---
description: A Next.js application with owned projects, local services and a shared design system.
---

# Web application

This is the working application for the TypeScript **Initialise with components**
option. It uses Next.js App Router on Node, Better Auth, PostgreSQL with Drizzle,
React Hook Form with Zod, and the sibling `@exordio/ui` package. Bun installs the
frozen workspace; Next.js runs on Node. No vendor account is needed locally.

## First useful change

From the generated repository root:

```bash
just setup
just dev
```

Open `http://localhost:3000`, create an account, and create a project. The dashboard
supports searching, sorting, editing, and deleting your projects. Profile settings
update your account name; the theme toggle follows the shared design tokens.
`just dev` starts the local services and applies committed migrations explicitly
before running the web application.

Development email goes to Mailpit at `http://localhost:8025`. Registration sends
an email verification link; **local development** permits signing in before
verification. Password recovery sends a single-use reset link and revokes existing
sessions after the password changes. Production requires verified email; signing
in with an unverified account sends a replacement verification link.

## Application boundaries

| Directory | Responsibility |
| --- | --- |
| `src/app/` | Routes, layouts, server-side page composition |
| `src/features/projects/` | Project forms, validation, queries and server actions |
| `src/features/auth/` | Login, registration, recovery and profile presentation |
| `src/auth/` | Better Auth server/client integration and email delivery |
| `src/db/` | Drizzle schema and the server-only PostgreSQL pool |
| `src/env/` | Validated server environment; no public secret aliases |
| `src/components/` | Application navigation, branding, theme and session adapters |
| `drizzle/` | Committed SQL migrations and schema history |

Reusable presentation belongs in `../../packages/ui`. App-specific forms compose
those primitives. `packages/ui` has no database, authentication or Next.js imports.
The `@/` import alias always refers to this application's `src/` directory.

Every project read is scoped to the authenticated user. Update and delete combine
both the project ID and owner ID in the SQL predicate. Client-supplied owner IDs
are discarded by the validation schema. The dashboard shows the latest 100
projects; add server pagination when a product needs a larger collection.

## Database changes

Edit `src/db/schema.ts`, then from the repository root run:

```bash
just typescript::db-generate
just typescript::db-migrate
```

Review and commit both SQL and Drizzle metadata. Migration generation and
application are explicit writes and do not run inside `check`. There is no
implicit seed or destructive reset. The initial migration includes Better Auth's
user, account, session, verification and database-backed rate-limit tables.

## Configuration and deployment

Explicit setup creates an ignored `.env.local` from the local defaults and a
random authentication secret. Existing files are preserved. See `env.example`
for the variable names. Inherited environment variables take precedence, so
SecretSpec and deployment-managed secrets can supply values without a file.

`APP_ENV` describes the deployment, independently of Node's build mode. Set
`APP_ENV=production` for a real deployment, provide PostgreSQL and SMTP credentials,
set `BETTER_AUTH_URL` to your HTTPS application origin, and use a strong random
`BETTER_AUTH_SECRET`. Production configuration requires encrypted SMTP through
`SMTP_SECURE=true` or `SMTP_REQUIRE_TLS=true`. Local Mailpit uses neither.

The app does not fetch fonts or credentials during compilation. Deploy the Next.js
build with Node 24, apply the committed database migrations as a separate release
step, and then start the application. `/api/health` returns only `ok` or
`unavailable`; it does not reveal database errors or configuration.

By default no forwarded IP header is trusted, so requests share conservative
rate-limit counters. Before public deployment, configure Better Auth's trusted
proxy/IP policy for your hosting environment and enforce HTTPS at the edge.
Authentication rate limits use the database so counters are shared across
instances. Back up the database and retain migration history. OAuth and paid auth
services are not required by this starter.

## Verification

The TypeScript workspace provides unit tests, strict type checking, linting,
unused-code and import-boundary checks, production builds, Storybook interaction
and accessibility checks, and browser journeys. Unit tests cover input bounds,
configuration, ownership predicates, rejected unauthenticated writes, and safe
error responses. The browser suite exercises the actual application and database.

`next-env.d.ts` and `.next/` are generated and ignored. `next typegen` prepares route
types during type checking; application builds do not rewrite authored TypeScript
configuration. See [the workspace guide](../../README.md) for all commands.
