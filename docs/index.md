---
description: Create a plan, edit a task and see its parent update.
---

# Your first useful plan

<!-- rumdl-disable MD033 -->
<div class="exordio-intro">
  <img src="assets/exordio-wordmark.svg" alt="Exordio: an open spellbook beneath a rising spark" width="480" height="144">
  <p class="exordio-motto">A spell for good beginnings.</p>
  <p>Choose your tools. Prepare your workspace. Make something worth keeping.</p>
</div>
<!-- rumdl-enable MD033 -->

A plan should show what to do next without copying every detail onto a board.
Here you will edit one Markdown task and refresh its parent's view.

## Prepare your machine

Use Linux x86-64 or ARM64 with [Git](https://git-scm.com/downloads),
[Nix](https://nixos.org/download/) and
[uv](https://docs.astral.sh/uv/getting-started/installation/).
Initial setup downloads pinned tools. Later checks use prepared inputs.

## Cast the first command

Choose a destination that does not exist:

```bash
env -u PYTHONPATH -u PYTHONHOME uvx --from copier==9.16.0 copier copy --vcs-ref v0.1.0 --defaults -d 'workflows=["planning"]' gh:marcusinthesky/exordio my-project
cd my-project
git init -b main
bash infra/nix/install-devenv.sh
devenv shell
just setup
```

This selects only planning. Omit `--defaults` for the questionnaire; every
capability is optional. Generation writes files without running setup tasks.
The command pins the `v0.1.0` release so your starting point is reproducible.

## Make the first task

```bash
just plan-new project "Project plan"
just task-new .context/plan/project first-step "Make the first useful change"
just sync
```

Open `ROADMAP.md` and follow the plan link. Its immediate-child table shows:

| Status | Item | Description |
| --- | --- | --- |
| backlog | Make the first useful change | Make the first useful change |

The task lives at `.context/plan/project/tasks/first-step/README.md`.
Task directories use your slug; paths supply identity, without numeric IDs.
Run the same task command with a task directory as parent to nest work further.

## Edit source once

Change the task's frontmatter from `status: backlog` to `status: in-progress`:

```bash
just sync
just check
```

The parent's row follows the task. The roadmap still describes the plan's own
state. Edit metadata rather than the generated table. A check reports stale
views without refreshing them.

## Complete work honestly

Replace the placeholder in `## Acceptance` with your intended outcome. Verify
each active criterion, check it, then set `status: done`. Fenced examples and
struck-through criteria do not establish completion.

Use `closed` with `resolution.reason` when intentionally stopping work.
A terminal parent cannot contain open children. Finished children contribute
to the terminal count instead of cluttering the open-child view.

Commit authored records and synchronized views together when ready.
Explore [daily commands](daily-use.md), [optional features](features.md),
[updates](updates.md) and [troubleshooting](troubleshooting.md).
