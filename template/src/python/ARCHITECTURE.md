---
description: Why Python libraries and applications share one uv workspace and lock.
---

# Python workspace

Libraries and executable consumers have separate package boundaries. A single
uv workspace resolves cross-package imports locally and locks test, build
and runtime dependencies together. This keeps the example runnable and lets the
project grow without publishing internal packages.

| Tool | Responsibility |
| --- | --- |
| uv | Dependency resolution, installation and packaging |
| Ruff | Lint and formatting |
| Pyrefly | Static type checking |
| pytest | Behavior and entry-point tests |

The pinned Nix environment supplies native Ruff and Pyrefly executables. This
avoids Python wheels whose ELF interpreter assumes a conventional Linux layout,
so the checker commands also work on NixOS without a machine-level loader service.

Python commands scrub inherited `PYTHONPATH` and `PYTHONHOME` so an unrelated Nix
or user environment cannot inject incompatible Python packages. Setup is the
network boundary; checks use frozen, offline dependencies and never update locks.
