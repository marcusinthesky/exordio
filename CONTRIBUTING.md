---
description: Change the template, inspect a real project and verify the result.
---

# Contributing

Read [README](README.md) and [architecture](ARCHITECTURE.md) first.
With Git, Nix and uv on a supported Linux machine:

```bash
git clone https://github.com/marcusinthesky/exordio.git
cd exordio
bash template/infra/nix/install-devenv.sh
devenv shell
just setup
```

Setup prepares frozen maintainer dependencies and installs Git hooks.

## Know the boundary

| Place | Purpose |
| --- | --- |
| `copier.yml` | Questions and conditional output |
| `template/` | Generated project files; infrastructure under infra/ and Python utilities under src/python/scripts/ |
| `tests/` | Rendering, behavior, upgrades and runtime verification |
| `docs/` | Creator guides and site assets |
| Root environment | Maintainer tools |

Read adjacent READMEs before editing. Bracket expressions belong to Copier;
downstream Jinja and GitHub syntax must remain intact.

## Make a change visible

```bash
just render /tmp/exordio-preview -d 'workflows=["planning"]'
just test tests/test_workflows.py
just check
```

Choose a new destination each time. Native Copier rendering includes uncommitted
changes and does not alter the source index. To execute the preview's commands,
initialize Git there, enter its own Devenv shell and run setup.

Keep generation data-only and actual records outside template ownership.
Checks report drift; formatting and synchronization are explicit writes.
Add a behavioral regression when changing a retained contract. Preserve native
coverage and update tests; do not replace them with assertions about source text.
See [tests](tests/README.md) for focused commands.

## Documentation

```bash
just site
just site-serve
```

Zensical uses the creator guides under `docs/` directly, including their assets.
Link root maintainer documents through GitHub from the site. Root entry points
have a 1,500-token budget. Site output is ignored and uploaded for review in CI;
this repository does not publish it automatically.

## Cut a release

The first release is `v0.1.0` in `marcusinthesky/exordio`. After the reviewed
changes are merged and the new repository exists, work from its clean `main`
checkout. Run `just check` (which includes `just site`) and confirm the runtime
CI matrix passes for the same commit.

Create and push an annotated `v0.1.0` tag on that commit, then wait for its CI
checks before publishing a GitHub release for the existing tag. Describe the
available capabilities and any migration limits in the release notes.
Copier consumes the tagged repository directly; no package upload is needed.

For later releases, update the project version and frozen lock metadata, advance
the pinned creation examples and walkthrough fixture, and repeat these checks.
Keep install examples pinned to a published tag; `copier update` selects the
latest stable tag by default. Site hosting remains a separate step.

## Agent instructions

```text
Make this bounded improvement to Exordio: [describe it].
Read README, CONTRIBUTING, ARCHITECTURE and adjacent READMEs.
Distinguish maintainer files from emitted template files.
Use pinned Devenv tools and frozen dependencies. Preserve authored content,
exclusive creation, explicit setup and read-only checks.
Render a fresh example, verify the behavior and run just check.
Keep the code readable and small. Report validation and remaining limitations.
Do not commit or push unless asked.
```
