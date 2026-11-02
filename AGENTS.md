# Agent contract

Read README.md, CONTRIBUTING.md, ARCHITECTURE.md and adjacent READMEs.
Maintainer tooling lives at the root; emitted files live under template/.
Use `devenv shell` and `uv run --frozen`; scrub host Python paths.
Copier uses bracket delimiters and the .copier suffix.
Keep actual tasks and references outside template ownership; never overwrite them.
Preserve AgentSync collision checks, explicit SecretSpec access and Nix pinning.
Setup prepares dependencies; sync/fmt write explicitly; check reports drift.
Run `just check` before handoff. Build the site with `just site`.
