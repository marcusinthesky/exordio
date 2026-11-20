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
| `typescript` | Bun library imported by a runnable CLI workspace |
| `go` (upcoming) | Reusable package and CLI in one Go module, with lint, tests and race detection |
| `rust` (development preview) | Rust library and CLI in one locked Cargo package |
| `lean` | Mathlib proofs with LeanArchitect annotations and a LeanBlueprint graph/PDF |
| `latex` | A Tectonic article with cached local builds |

Each language has a local README and namespaced commands. Python and TypeScript
retain their library/application package boundaries. Lean includes its blueprint
tooling even when manuscript LaTeX is absent.

### Go development preview

Go is available in the development template, not in the pinned `v0.1.0` release.
From a development checkout containing Go support, use the normal maintainer
preview command after setup:

```bash
just render /tmp/exordio-go -d 'languages=["go"]'
```

Choose a new destination. Initialize Git there, enter its Devenv shell and run
`just setup`, `just go::run Ada` and `just check`. Go alone needs neither a Python
application workspace nor Bun. Planning, references and agents remain separate
choices.

The `go_module` answer defaults to `example.com/<project_slug>`. For a module
published directly from GitHub, use `github.com/OWNER/REPOSITORY/src/go` because
the module lives below the repository root. The generated Go README explains
dependency updates, package boundaries and module release tags.

### Rust development preview

Rust support belongs to the development template, not the published `v0.1.0`
release. From a checkout containing the Rust support, render a fresh project:

```bash
env -u PYTHONPATH -u PYTHONHOME uvx --from copier==9.16.0 copier copy --defaults --vcs-ref HEAD -d 'languages=["rust"]' . ../rust-example
cd ../rust-example
git init -b main
bash infra/nix/install-devenv.sh
devenv shell
just setup
just rust::run Ada
just check
```

The starter is one Rust 2024 package under `src/rust`: a reusable library, a thin
CLI, ordinary tests and documentation examples. It has no third-party runtime
dependencies. Nix pins the compiler, Cargo, Clippy, rustfmt and the additional
quality tools; Cargo owns application dependencies through `Cargo.toml` and the
committed `Cargo.lock`.

`just rust::check` checks formatting, types and borrowing, Clippy diagnostics,
dependency consistency and unused dependencies, Nextest tests, doctests,
documentation and a release build. Checks use frozen, offline dependencies after
setup and leave source files unchanged. `just rust::fmt` writes formatting changes.

`just rust::security` uses cargo-deny with fresh advisory data and the project's
dependency policies. It is separate from offline checks. `just rust::coverage`
uses cargo-llvm-cov and the matching LLVM tools; no minimum percentage is imposed.
The starter's README explains how to extend the policies as dependencies and
features are introduced. Nightly tools and application-specific fuzz targets are
not required by the starter.

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
