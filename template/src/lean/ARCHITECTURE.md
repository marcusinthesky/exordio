---
description: Why the proof compiler, blueprint extraction and rendering stay together.
---

# Lean and its blueprint

The pinned Nix compiler supplies Lean and Lake for Linux x86-64 and ARM64. The
`lean-toolchain` file declares the same version for editors; a setup gate rejects
a mismatch before compiling. This avoids an imperative Elan installation that
can reference garbage-collected Nix libraries.

Mathlib and LeanArchitect follow the compiler version. The complete Lake
manifest fixes their Git revisions; checks never call `lake update`. Setup is
the network boundary, and checks verify prepared revisions before compiling.

LeanArchitect owns extraction from compiled annotations; LeanBlueprint owns
HTML rendering. Calling plasTeX directly supports this nested Lake project:
LeanBlueprint's convenience CLI assumes that the Lake and Git roots coincide.
The blueprint's Python environment is separate from application Python. Its
pygraphviz extension builds against pinned Nix Graphviz, avoiding a wheel's
bundled native libraries. Tectonic renders the same content as PDF.

Blueprint tools accompany Lean even when the separate LaTeX manuscript language
is absent. There is no deployment or extra proof-status database. Keep research
assumptions explicit in theorem hypotheses; mathematical explanation still
requires human review.
