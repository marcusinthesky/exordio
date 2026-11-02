---
description: A small selectable template with clear ownership.
---

# Architecture

Exordio distributes one Copier template. Root files maintain the distribution;
`template/` contains the files emitted into projects. One release sequence owns
the catalog. Separate independently versioned add-ons are unnecessary here.

## Select capabilities, not profiles

Two independent workflow choices supply planning and references. Four independent
languages supply runnable examples. All default to empty. AgentSync and
SecretSpec remain optional integrations; Nix is the shared environment foundation.
There are no workflow bundles, cloud scaffolds or implicit research applications.

Copier uses bracket delimiters and the `.copier` suffix so Insitu Jinja and GitHub
expressions retain their own syntax. Generation runs no tasks. Dependencies are
prepared only through explicit setup.

## Own source once

Copier owns configuration and starter code. Actual plans, tasks and references
are created exclusively by commands: their paths never occur in template output.
Insitu owns marked regions; metadata and surrounding prose belong to the project.
The Copier answers file is the sole saved capability configuration.

Planning paths supply identity. Slug-based nesting reveals immediate children
without numeric allocation or a dependency graph. `done` requires verified
acceptance; `closed` requires a reason. Terminal parents cannot contain open
children. Parents have their own authored status, independent of child status.

References use flat CSL metadata and directory-derived citation keys. Local
description and links are removed before Pandoc exports bibliography entries.
Export exists only when references and LaTeX are both selected.

Declared links are canonical repository-relative files, matching SQL identity.
Ordinary body links retain URL and section semantics. Schematter checks three
small contracts: work item, reference and the 1,500-token entry budget.

## Keep execution explicit

Devenv pins tools on Linux x86-64 and ARM64. Language workspaces and PEP 723 repository scripts have separate frozen locks. Setup can download inputs and create ignored
environments; checks use prepared inputs and never repair tracked files.

Nix builds AgentSync directly from its pinned Rust source and Cargo lock.
Only the downloaded Insitu executable needs explicit native runtime preparation,
which copies ignored installed files before patching to preserve immutable caches.
Nix definitions and static schemas live under infra/nix and infra/schemas.
Root Devenv files remain native entrypoints. Python repository commands live
under src/python/scripts/, independently of the optional application workspace. Maintainer tooling references shared
helpers in the emitted template directly.

A zero-dependency PEP 723 Python preflight inspects every destination before
native AgentSync apply. Bun belongs only to the TypeScript workspace. Authored
files, unexpected links and symlinked parents stop setup without replacement.
Without AgentSync, projects can author their own instructions outside template ownership.
SecretSpec resolves credentials only for an explicit subprocess.

Python and TypeScript retain separate library/application packages. Lean and
Mathlib move together; LeanArchitect extracts blueprint content from compiled
annotations. LeanBlueprint renders that content through plasTeX. Its nested Lake
workspace uses direct rendering commands rather than a custom upstream adapter.
Lean provides its own blueprint dependencies independently of manuscript LaTeX.

## Prefer existing tools

Copier's native local-HEAD rendering previews dirty changes without a custom
snapshot runner. Zensical builds the creator guides directly from `docs/`.
Root maintainer documents remain readable on GitHub. CI uploads site artifacts;
publication is separate. There is no documentation staging service.

Tagged releases in `marcusinthesky/exordio` version the entire distribution.
Updates preserve selections or add capabilities.
Feature removal and existing-project adoption remain manual migrations because
Copier may remove previously owned paths.
