---
description: Compare blank Git and Exordio starters using pinned Zero2Repo cases.
---

# Zero2Repo comparison

This maintainer-only adapter compares the same official Codex CLI agent starting
from either `git init` or a generated Exordio project. It reuses
[Zero2Repo](https://github.com/Gradient-Data/Zero2Repo) commit
`c10b60ca3f2d9498a7e2dfea6b4a881037a0cccc`: public specifications, interface
contracts, native execution and hidden acceptance tests. The primary score is
Zero2Repo's binary reward, **not an LM judgment or a new weighted rubric**.

## Comparison

| Arm | Initial `/app` |
| --- | --- |
| `blank` | Empty Git repository |
| `exordio` | Pinned Copier output with the task's language selected, initialized in Git |

Both arms receive the same task text, agent, model, reasoning effort, case image
and budgets. The native prompt's empty-workspace wording is made neutral in both
arms. Other task requirements and grading rules remain unchanged. Exordio selects
only Python or TypeScript; planning, references, AgentSync and secrets are off.
The agent can adapt the generated layout to the original public interface.

The pilot selects Python `case001` and `case002`, and TypeScript `case003` and
`case012`. Four tasks × two arms × three repetitions produces 24 attempts. The
seed shuffles the complete plan; it does not make model responses deterministic.
Attempts run sequentially with fresh agent sessions and workspaces.

This measures **the generated scaffold in Zero2Repo's shared case runtime**.
Preparation renders files but does not install Nix, enter `devenv shell` or run
the starter's `just setup`. Both arms retain the native case toolchains and
dependencies. It therefore does not measure the benefit of a prepared Exordio
Nix environment, or the effort of asking an agent to discover and install Exordio.
Generated Nix files remain available, but their commands may need adaptation.

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

Edit `.cache/agentbench.json` to choose an explicit model identifier and exact
published Codex CLI version. `SET_ME` values are rejected. `zero2repo` is resolved
relative to the configuration file; the example therefore points at
`.cache/zero2repo`. `template_ref` pins the template commit, independently of the
adapter branch. Keep the supplied task set for the first pilot.

```bash
just bench prepare .cache/agentbench.json .cache/campaigns/pilot
just bench run .cache/campaigns/pilot
```

The first command prepares the campaign; the second prints its execution plan.
Review the frozen model, CLI, template, prompts, image identities and budgets
before spending model tokens. Preparation time is separate from agent time.

## Execute and inspect

Configure `OPENAI_API_KEY` in the shell using the provider's normal mechanism;
never put credentials in the JSON configuration. This uses the native Codex API
runner; host CLI login is not mounted. Keep `OPENAI_BASE_URL` and
`CBRUN_CODEX_GATEWAY_WEBSOCKETS` unchanged between preparation and execution.
Other `CBRUN_*`, `CODINGBENCH_*` and `CODING_BENCH_*` overrides are cleared.
Budgets bound agent wall time, inactivity and judge time; there is no token cap.

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
claims against its published leaderboard. A qualitative LM judge, a full Nix
runtime treatment and a larger task suite are separate experiments.

## Checks

```bash
just test tests/test_agentbench.py tests/test_agentbench_runner.py
just check
```

Tests exercise campaign contracts without calling a model. The actual Docker
image builds and agent trials are explicit local steps. Keep preparation and
trial artifacts under ignored `.cache/`; benchmark code is never emitted into
generated projects.
