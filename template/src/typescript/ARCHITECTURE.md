---
description: Why the TypeScript starter uses Bun workspaces and direct tool commands.
---

# TypeScript workspace

Bun owns runtime execution, workspace dependency installation and tests. A library
and its executable consumer demonstrate the package boundary without a framework.
TypeScript provides strict static checks and Biome provides formatting and lint.

| Concern | Owner |
| --- | --- |
| Dependencies | Committed `bun.lock` |
| Application and library code | Their workspace packages |
| Build output | Ignored `dist/` |
| Cross-language commands | Root justfile |

The starter has no task scheduler: the workspace is small enough for direct
commands. A generated project can add a build graph when its dependencies justify
one. Installation happens in setup; checks execute locally installed tools.

Script commands explicitly use Bun for JavaScript command-line tools rather than
depending on an ambient Node installation. The Linux devenv selects Biome's
static musl executable from the locked optional packages, avoiding an assumption
about a machine-level ELF loader on NixOS.
