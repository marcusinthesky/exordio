---
description: Recover from setup and validation failures.
---

# Troubleshooting

## The shell does not start

Check that Nix is installed and its daemon is available. Run
`bash infra/nix/install-devenv.sh` to install the CLI version matching the lock,
then enter `devenv shell`. Linux x86-64 and ARM64 are supported.

## A dependency or native executable is missing

Run `just setup` inside the pinned shell. Setup prepares frozen environments
and native runtime paths without rewriting locks. It needs network access.
Checks use installed dependencies and do not fetch missing inputs.

For Lean, use `just lean::setup` after a fresh checkout. Blueprint rendering needs
the Graphviz/compiler dependencies supplied by Lean's own environment.
Read the Lean README before changing Lean, Mathlib or Architect versions.

## A view or bibliography is stale

Edit the source record, then run `just sync` and `just check`. Do not repair a
generated table manually. With references and LaTeX, source citation metadata
belongs in reference records rather than the exported bibliography.

## A task cannot finish

`done` needs at least one nonempty active acceptance criterion, all checked.
Use `closed` with a reason for discontinued work. Finish or close children before
making their parent terminal. Neither state propagates automatically.

## A declared link fails

Use the exact repository-relative filename suggested by the error. Directories,
URLs and section fragments belong in normal body links rather than `links`.

## AgentSync refuses to apply

Preserve the authored destination, merge its intended content into canonical
`.agents/` sources, and follow their README before removing old native files.
Preflight checks all destinations before apply. It does not hide collisions
in ignored backups.

## A preview destination already exists

Choose a new directory for `just render`. This deliberate guard prevents
overwriting a previous preview. The command renders local uncommitted changes.

## An update conflicts

Resolve conflicts before setup/synchronization and check the diff.
Removing a feature and migrating the old profile-based preview require manual
review; see [updates](updates.md).
