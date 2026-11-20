---
description: Compare blank Git and Exordio starters using pinned Zero2Repo cases.
---

# Zero2Repo comparison

This pilot compares blank Git and prepared Exordio projects on four pinned
Zero2Repo cases using GPT-6 Luna, medium reasoning effort and the local
ChatGPT subscription. The host runs Pydantic Coder with tools in the case
container. Zero2Repo supplies the task, monitored solve and hidden judge.
Three repetitions per case and arm produce 24 attempts.

The Python image applies Zero2Repo's own audit installer to its prepared interpreter.
Preparation exercises an ordinary import and checks that the native monitor attributes
a controlled access to Python. The TypeScript pilot remains blocked because Bun accepts
an ES module import rejected by the native judge controls. All eight model-free
case/arm checks must succeed before preparation publishes a campaign.

Preparation builds the language project at /app, initializes Git, installs
the pinned Devenv, and runs setup. The benchmark records campaign preparation
and agent solve times separately. The manifest freezes the [secondary review
rubric](rubric.md) before collection. Per-case results retain individual
repetitions, missing attempts, and invalid attempts.

## Prepare locally

Use native Linux x86-64 with Git, Python 3.13, uv and a local Docker daemon;
this pilot rejects emulation. Read the upstream repository and case-source terms
before running; the corpus is not vendored here. Preparation builds images and
may download dependencies, but makes no model calls.

From the Exordio root, after the ordinary contributor setup:

```bash
git clone https://github.com/Gradient-Data/Zero2Repo.git .cache/zero2repo
git -C .cache/zero2repo checkout c10b60ca3f2d9498a7e2dfea6b4a881037a0cccc
cp bench/config.example.json .cache/agentbench.json
```

The pilot fixes the subscription model and medium effort. Check host access with one model call
using `just bench subscription-smoke`.

```bash
just bench prepare .cache/agentbench.json .cache/campaigns/pilot
just bench run .cache/campaigns/pilot
```

The first command prepares the campaign; the second prints its execution plan.
Review the frozen model, CLI, template, prompts, image identities and budgets
before spending model tokens. Preparation time is separate from agent time.

## Execute and inspect

Use your existing host Codex subscription login for the default model.
The agent container receives workspace tools. The controller handles
credentials and model requests. Subscription cost is reported as unknown.
A setup or infrastructure failure saves diagnostics and stops the schedule.

```bash
just bench run .cache/campaigns/pilot --execute
just bench report .cache/campaigns/pilot
```

`--execute` is required for model calls. Runs retain native submission, audit,
usage, logs and workspace artifacts. Re-running skips completed attempts with a
saved `trial.json`; an unfinished attempt directory stops execution rather than
being overwritten or silently retried. Preserve interrupted attempts and prepare
a new campaign for another trial. Changes to prompts, versions or budgets also
require a new campaign.

The native runner normally requires an explicit submission; it also judges work
when the agent times out. Hidden tests are withheld during the agent phase. The
judge receives the resulting `/app` in a fresh container with networking disabled.
This includes generated build outputs and installed dependencies: the judge does
not rebuild or reinstall the project from a source-only checkout. It is the native
acceptance boundary, not an additional clean-build reproducibility test.

## Read the results

The report separates accepted, failed, incomplete and invalid attempts. Retain
every planned repetition; interrupted or missing measurements must not disappear
from the denominator. Compare arms on the same cases, averaging repetitions
within each case before weighting cases equally. Unknown usage or cost remains
unavailable, never zero. Inspect native usage records when comparing efficiency.
Headline pass rates and the paired difference stay unavailable until every planned
attempt is valid and complete; observed rates and coverage counts remain visible.
Native review flags are reported without changing the upstream reward.

Use this small pilot to check the integration and identify task or environment
failures. Four selected tasks do not establish general superiority. Results are
an Exordio adaptation of Zero2Repo; the changed initial workspace prevents direct
claims against its published leaderboard. Secondary qualitative scoring follows collection.

## Checks

```bash
just test tests/test_agentbench.py tests/test_agentbench_runner.py
just check
```

Tests exercise campaign contracts without calling a model. The actual Docker
image builds and agent trials are explicit local steps. Keep preparation and
trial artifacts under ignored `.cache/`; benchmark code is never emitted into
generated projects.
