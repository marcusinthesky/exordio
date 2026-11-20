---
description: Update structure while preserving authored records.
---

# Keep the project current

Commit local work and keep `.copier-answers.yml` under version control:

```bash
env -u PYTHONPATH -u PYTHONHOME uvx --from copier==9.16.0 copier update
```

Review changes and conflicts, then run `just setup`, `just sync` when available,
and `just check`. Copier selects the latest stable tag from the source saved in
`.copier-answers.yml`. Projects created from Exordio releases use
`gh:marcusinthesky/exordio`. To target a particular release, add
`--vcs-ref v0.1.0`, substituting the desired tag.

## Add a feature

Use Copier's questionnaire and retain existing selections. Saved empty lists
remain authoritative. Plans, tasks and references created by commands belong to
your project and never occur in template output.

## Preserve agent instructions

When enabling AgentSync, existing authored destinations or unexpected links
stop apply before any destination is changed. Merge intended instructions into
the canonical `.agents/` sources, preserve them in Git, then deliberately remove
old destinations and stop tracking generated links. Follow the generated
AgentSync README before applying again.

## Migrate deliberately

Removing capabilities or adopting into an existing repository is a manual
migration. Copier can remove previously owned paths, including customized code.
Use a branch, preserve retained content and inspect a trial update.

Projects from the earlier profile/stack prototype need regeneration or a manual
migration; there is no legacy converter. A project created from another source
repository keeps that source in its Copier answers; it does not switch to
Exordio automatically.

## Switch TypeScript variants

`typescript_components` is saved with the TypeScript selection. Normal updates
retain it even if a future template changes its default. Adding TypeScript with
components to a project that previously had no TypeScript is supported.

Changing an existing TypeScript project from basic to components, or back again,
is deliberately rejected before Copier writes files. The two variants have
different application/package paths and lockfiles; an automatic switch could
remove customized code. This guard uses the existing Copier answers file.

To migrate, commit current work and generate the desired variant in a new
sibling directory at the intended template version. Port application code and
configuration deliberately, retaining existing data and migration history.
Review every removed path, run setup and the complete check in the new project,
then adopt it. Do not bypass the guard by editing saved answers in place: that
would cause future updates to treat the old project as a different template.
