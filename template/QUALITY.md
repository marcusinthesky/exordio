---
description: Quality gates and upgrade workflow for Exordio-generated projects.
---

# Quality and verification

The generated `just check` command is the read-only source-of-truth validation entry point.
After initial `just setup`, it checks the selected languages and workflows inside the
pinned devenv. `just fmt` is an explicit write operation; do not run it as a CI gate.

## Language-specific checks

- **Python:** Ruff lint/format, strict Pyrefly type checking, pytest, and package builds.
- **TypeScript:** Biome, strict `tsc --noEmit`, Bun tests and build.
- **Lean:** warning-as-error compiler builds, Batteries `lake lint`, blueprint web/PDF.
- **LaTeX:** tex-fmt, ChkTeX and offline Tectonic build.
- **Repository:** prek, actionlint, shellcheck for shell scripts, and Markdown/Nix lint.

The project uses pinned environments and committed dependency locks. Keep newly added
checks read-only; do not automatically update lockfiles or rewrite source during validation.
Run `just setup` after updating language dependencies, then review lockfile diffs.
Inspect CI job results rather than assuming skipped checks passed.

## Existing projects

On an Exordio-generated project, commit or back up authored changes before
running a template update. Review the generated diff and Copier conflict markers,
then run the normal local setup and checks:

```bash
copier update
devenv shell -- just setup
devenv shell -- just check
```

Copier retains the saved selections in `.copier-answers.yml`; no workflow silently
updates existing downstream repositories. Renovate can propose template revisions
from the saved Copier source, but updates still require review.

## Security and heavier analysis

The local quality baseline does not imply a vulnerability-free dependency graph.
Enable repository-hosted CodeQL, OSV-Scanner, release provenance and branch rulesets
separately as supported by the target repository. `Renovate` configuration only
takes effect when the corresponding GitHub app or service is enabled.

Bigger suites (Hypothesis, pytest-xdist, testmon, Knip, architecture policies,
mutation tests and independent Lean kernel checks) should be added when a project
has sufficient code to justify their maintenance. They are not installed by this
minimal template. Never report an advisory scan as an enforced gate.
