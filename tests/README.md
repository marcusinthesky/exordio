---
description: Behavioral coverage for template generation, workflow rules and tagged upgrades.
---

# Tests

Run `just test` from the repository root after `just setup`.

Tests copy the current source into temporary Git repositories. They exercise
the real Copier CLI, so uncommitted template changes are tested without
changing the working branch or relying on its current committed template.

Twelve render fixtures cover the independent workflow choices, each language on
its own, useful integrations and the maximal selection. Workflow tests create
real records, exercise completion rules and detect stale views. Upgrade tests
make two local tags and preserve authored content, saved answers and reviewable
configuration conflicts.

Native Insitu integration uses the locked tool environment prepared by setup.
Toolchain builds are exercised separately by the runtime CI matrix; ordinary
render tests do not download every language dependency.

Run a generated project in its own pinned devenv environment with:

```bash
PROJECT_WORKFLOWS='["planning"]' PROJECT_LANGUAGES='["python"]' \
  uv run --frozen python -m tests.check_project
```

The runner checks that setup preserves tracked files, creates
records explicitly, and checks the project with offline package settings and
blocked HTTP proxies. The maximal fixture also enables both agents and
SecretSpec. An agent-only fixture checks native AgentSync without a language
workspace or Bun installation. Native dependencies are required for every test run; complete
`just setup` before testing.

The render fixtures lint generated documentation and check entry-point budgets.
Documentation tests execute the printed planning walkthrough and verify native
Copier previews. Adoption regressions preserve authored agent configuration
during tagged upgrades; language regressions cover test discovery and filesystem
paths. The site uses Zensical directly rather than a custom export layer.

`just check` finishes with a strict documentation build. Run `just site` on its
own while editing guides, or `just site-serve` for a local browser preview.
Read [the contributor guide](../CONTRIBUTING.md) for the shortest change loop.

CI prepares x64 TeX resources once using sequential manuscript, reference and
blueprint fixtures, then passes the resulting Tectonic cache to project jobs.
Explicit TeX setup retries diagnosed transient bundle-server failures; offline
checks continue to fail if a required resource is absent.
