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
