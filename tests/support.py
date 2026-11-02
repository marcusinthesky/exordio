"""Run the real Copier and Git interfaces against disposable repositories."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ("planning", "reference")
LANGUAGES = ("python", "typescript", "lean", "latex")
COPIER = [sys.executable, "-m", "copier"]
WORKFLOW = "src/python/scripts/workflow/script.py"


def clean_environment() -> dict[str, str]:
    """Keep user Python and Git configuration outside the test fixture."""
    env = os.environ.copy()
    for name in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV"):
        env.pop(name, None)
    env.update(
        {
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "Template Test",
            "GIT_AUTHOR_EMAIL": "template-test@example.invalid",
            "GIT_COMMITTER_NAME": "Template Test",
            "GIT_COMMITTER_EMAIL": "template-test@example.invalid",
        }
    )
    return env


def run(
    args: list[str],
    cwd: Path,
    *,
    check: bool = True,
    timeout: int = 120,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = clean_environment()
    env.update(extra_env or {})
    result = subprocess.run(
        args,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if check:
        assert result.returncode == 0, (
            f"Command failed ({result.returncode}): {args!r}\n"
            f"{result.stdout[-8000:]}\n{result.stderr[-8000:]}"
        )
    return result


def git(repo: Path, *args: str) -> str:
    return run(["git", "-c", "core.hooksPath=/dev/null", *args], repo).stdout.strip()


def commit_all(repo: Path, message: str) -> None:
    git(repo, "add", "--all")
    git(repo, "commit", "--quiet", "--message", message)


def snapshot_template(destination: Path) -> Path:
    destination.mkdir(parents=True)
    files = git(
        ROOT,
        "ls-files",
        "--cached",
        "--others",
        "--exclude-standard",
        "-z",
        "copier.yml",
        "template",
    )
    for relative in filter(None, files.split("\0")):
        source = ROOT / relative
        if source.exists() or source.is_symlink():
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target, follow_symlinks=False)
    git(destination, "init", "--quiet", "--initial-branch=main")
    commit_all(destination, "feat(template): initial fixture")
    git(destination, "tag", "v0.1.0")
    return destination


def render(
    source: Path,
    destination: Path,
    data: dict[str, object] | None = None,
    *,
    ref: str = "HEAD",
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    data_file = destination.parent / f"{destination.name}-input.yml"
    data_file.write_text(yaml.safe_dump(data or {}), encoding="utf-8")
    return run(
        [
            *COPIER,
            "copy",
            "--defaults",
            "--vcs-ref",
            ref,
            "--data-file",
            str(data_file),
            str(source),
            str(destination),
        ],
        source,
        check=check,
    )


def answers(repo: Path) -> dict[str, object]:
    return yaml.safe_load((repo / ".copier-answers.yml").read_text(encoding="utf-8"))


def update(repo: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    return run([*COPIER, "update", "--defaults", *extra_args], repo)


def workflow(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Only explicit preparation may populate the script environment online."""
    offline = [] if args == ("prepare",) else ["--offline"]
    return run(["uv", "run", *offline, "--frozen", "--script", WORKFLOW, *args], repo, check=check)
