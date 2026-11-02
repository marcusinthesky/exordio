---
description: A short edit, synchronize and check loop.
---

# Everyday work

Enter `devenv shell` and run `just --list` for installed commands.
Run `just setup` after the first checkout or a dependency update.

## Plan work

```bash
just plan-new delivery "Delivery plan"
just task-new .context/plan/delivery implement "Implement the first slice"
just sync
just check
```

Edit the task's frontmatter and acceptance, then synchronize again.
Paths stay stable when status changes. Parent views expose immediate children;
they do not infer the parent's own status.

## Keep a reference

With references selected:

```bash
just reference-new shannon1948 "A Mathematical Theory of Communication"
just sync
just check
```

Edit flat CSL fields such as `author`, `issued`, `DOI` and `URL` in the reference.
Its directory is the citation key. When LaTeX is also selected, synchronization
exports `src/latex/refs.bib`; edit the record rather than that derived file.

## Connect records

Add canonical file paths to `links`:

```yaml
links:
  - README.md
```

The target's backlink appears when it is part of the indexed context.
Declared links include filenames and use no `./`, traversal, URL encoding,
queries or fragments. Body links retain ordinary Markdown URL/section syntax.

## Run and maintain code

Language commands use namespaces such as `just python::run Ada` and
`just typescript::run Ada`. Consult each workspace README for builds and tests.

`just check` validates without repair; `just fmt` writes formatting changes.
`just sync` explicitly refreshes installed views. `just links` checks external
links online, separately from local correctness.

AgentSync users can apply/check their native configuration with
`just agents::apply` and `just agents::check`. SecretSpec users pass a subprocess
to `just secret-run` rather than loading credentials into the shell.
