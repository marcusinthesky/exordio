---
description: Start a project with only the tools you need.
---

# Exordio

![Exordio: an open spellbook beneath a rising spark](docs/assets/exordio-wordmark.svg)

**A spell for good beginnings.**

Choose your languages and, if useful, Markdown planning or reference records.
Exordio supplies a reproducible Nix environment, checks and documentation.
Each choice is independent: a TypeScript project needs no planning system.

## Start with one useful thing

Use Linux x86-64 or ARM64 with Git, Nix and
[uv](https://docs.astral.sh/uv/getting-started/installation/) installed.
Initial setup downloads pinned dependencies.

This example creates only a TypeScript workspace:

```bash
env -u PYTHONPATH -u PYTHONHOME uvx --from copier==9.16.0 copier copy --vcs-ref v0.1.0 --defaults -d 'languages=["typescript"]' gh:marcusinthesky/exordio my-project
cd my-project
git init -b main
bash infra/nix/install-devenv.sh
devenv shell
just setup
just typescript::run Ada
just check
```

Omit `--defaults` to choose interactively. Both workflow and language selections
default to empty. The example pins the `v0.1.0` release.

## Choose what belongs in your project

| Choice | What you get |
| --- | --- |
| Planning | Nested Markdown tasks, immediate-child views and a roadmap |
| References | Citation records, backlinks and an index |
| Python | A typed library and application in one uv workspace |
| TypeScript | A Bun library and CLI workspace |
| Lean4 | Mathlib proofs, LeanArchitect and a LeanBlueprint graph/PDF |
| LaTeX | A Tectonic article; references can generate its bibliography |
| AgentSync | Shared instructions projected into Codex and/or Claude configuration |
| SecretSpec | Secret access only for an explicitly invoked command |

Read the [feature guide](docs/features.md), or follow the
[planning walkthrough](docs/index.md) to see source metadata become a useful view.
Nix supports every selection; no cloud infrastructure is created.

## Let your agent help

Paste this into an agent with access to your local repositories:

```text
Create a project using Exordio:
https://github.com/marcusinthesky/exordio

Read its README and feature guide first. Choose only the workflows, languages
and integrations needed for my goal. Use Copier 9.16.0 and release v0.1.0.
Generate into a new directory, initialize Git and enter its pinned environment.
Run explicit setup and deliver one useful working result.
Read adjacent READMEs, preserve authored content, and run applicable sync/checks.
Report what works and my next useful step. Do not commit or push unless asked.
```

## Find your next step

- [Everyday work](docs/daily-use.md)
- [Updates](docs/updates.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Contributing](CONTRIBUTING.md)
- [Architecture](ARCHITECTURE.md)

Copier owns project structure; optional Insitu views derive from authored files.
Your records stay ordinary Markdown in Git.
