---
description: Checked Lean proofs and a blueprint generated from the same declarations.
---

# Lean

Start with `Example/Basic.lean`: two real-number identities, proved with Mathlib,
carry `@[blueprint]` annotations containing their mathematical explanations.
LeanArchitect extracts the statements, dependencies and proof status directly
from compiled Lean. LeanBlueprint turns that output into a browsable graph and
a printable companion.

```bash
just lean::setup
just lean::check
```

Setup explicitly downloads the locked dependencies, Mathlib cache and TeX
resources. Later checks use prepared local inputs. HTML appears in
`blueprint/web/` and PDF in `blueprint/print/print.pdf`; these are ignored outputs.
Run `just lean::blueprint-web` or `just lean::blueprint-pdf` to rebuild either.

`Example.lean` imports the library's modules. Add new imports there so the build
includes them; annotate the declarations you want in the blueprint. The shared
`blueprint/src/content.tex` chooses which extracted modules to show. Edit source
annotations and prose, then rebuild; generated status is never authored by hand.

Lean, Mathlib and LeanArchitect use v4.35.0. First-party warnings are errors, so
an admitted proof fails. Fetch extra Mathlib modules with
`just lean::cache Mathlib.Module.Name`. See [ARCHITECTURE.md](ARCHITECTURE.md) for
toolchain ownership and the nested blueprint layout.
