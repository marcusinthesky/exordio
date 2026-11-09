"""Exercise a generated project in its own environment, as runtime CI does."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from tests.support import (
    LANGUAGES,
    WORKFLOWS,
    clean_environment,
    commit_all,
    git,
    render,
    snapshot_template,
)


def runtime(repo: Path, *command: str, offline: bool = False) -> None:
    env = clean_environment()
    if offline:
        env.update(UV_OFFLINE="1", CARGO_NET_OFFLINE="true", NO_PROXY="", no_proxy="")
        env.update(
            {
                name: "http://127.0.0.1:9"
                for name in (
                    "HTTP_PROXY",
                    "HTTPS_PROXY",
                    "ALL_PROXY",
                    "http_proxy",
                    "https_proxy",
                    "all_proxy",
                )
            }
        )
    subprocess.run(["devenv", "shell", "--", "just", *command], cwd=repo, env=env, check=True)


def exercise(
    directory: Path, workflows: list[str], languages: list[str], agents: list[str] | None = None
) -> None:
    source = snapshot_template(directory / "catalog")
    repo = directory / "project"
    maximal = set(workflows) == set(WORKFLOWS) and set(languages) == set(LANGUAGES)
    render(
        source,
        repo,
        {
            "workflows": workflows,
            "languages": languages,
            "agents": agents if agents is not None else ["codex", "claude"] if maximal else [],
            "secrets": maximal,
        },
    )
    git(repo, "init", "--quiet", "--initial-branch=main")
    commit_all(repo, "feat(project): initialize runtime fixture")
    runtime(repo, "setup")
    assert not git(repo, "status", "--porcelain=v1", "--untracked-files=no"), (
        "Setup rewrote tracked content"
    )
    if "planning" in workflows:
        runtime(repo, "plan-new", "project", "Project plan")
        runtime(repo, "task-new", ".context/plan/project", "first", "First task")
    if "reference" in workflows:
        runtime(repo, "reference-new", "paper", "Useful paper")
    if workflows:
        runtime(repo, "sync")
        commit_all(repo, "docs(project): create records and refresh views")
    before = git(repo, "diff", "--binary", "HEAD")
    runtime(repo, "check", offline=True)
    assert git(repo, "diff", "--binary", "HEAD") == before, "Checks rewrote tracked content"
    # Exercise the *generated commands* with deliberate defects, not just clean fixtures.
    # Each probe is restored, then the no-mutation invariant is checked again.
    for language, target, fault, command in (
        (
            "python",
            repo / "src/python/packages/example_core/src/example_core/__init__.py",
            "\\nimport exordio_unused_quality_probe\\n",
            "python::lint",
        ),
        (
            "typescript",
            repo / "src/typescript/packages/core/src/index.ts",
            "\\nconst exordioTypeProbe: string = 123;\\n",
            "typescript::typecheck",
        ),
    ):
        if language not in languages:
            continue
        original = target.read_bytes()
        try:
            target.write_bytes(original + fault.replace("\\n", "\n").encode())
            try:
                runtime(repo, command, offline=True)
            except subprocess.CalledProcessError:
                pass
            else:
                raise AssertionError(f"{command} accepted the injected {language} defect")
        finally:
            target.write_bytes(original)
    assert git(repo, "diff", "--binary", "HEAD") == before, "Quality probes changed tracked content"


def main() -> None:
    workflows = json.loads(os.environ.get("PROJECT_WORKFLOWS", "[]"))
    languages = json.loads(os.environ.get("PROJECT_LANGUAGES", "[]"))
    assert isinstance(workflows, list) and set(workflows) <= set(WORKFLOWS)
    assert isinstance(languages, list) and set(languages) <= set(LANGUAGES)
    agents = json.loads(os.environ.get("PROJECT_AGENTS", "null"))
    assert agents is None or isinstance(agents, list) and set(agents) <= {"codex", "claude"}
    with TemporaryDirectory(prefix="catalog-runtime-") as temporary:
        exercise(Path(temporary), workflows, languages, agents)


if __name__ == "__main__":
    main()
