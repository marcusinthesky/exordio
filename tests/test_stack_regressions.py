"""Exercise growing workspaces, filesystem paths and the pinned link checker."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from tests.support import ROOT, run


def test_python_discovers_added_members_with_repeated_test_names(tmp_path: Path) -> None:
    workspace = tmp_path / "python"
    workspace.mkdir()
    shutil.copy2(ROOT / "template/src/python/pyproject.toml", workspace / "pyproject.toml")
    for category, member, failing in (
        ("packages", "example_core", False),
        ("apps", "example_app", False),
        ("packages", "new_library", True),
        ("apps", "new_application", False),
    ):
        package = workspace / category / member
        tests = package / "tests"
        tests.mkdir(parents=True)
        (package / "pyproject.toml").write_text(
            f'[project]\nname = "{member.replace("_", "-")}"\nversion = "0.1.0"\n'
            "[tool.uv]\npackage = false\n"
        )
        (tests / "test_same_name.py").write_text(f"def test_member():\n    assert {not failing}\n")

    result = run([sys.executable, "-m", "pytest", "-q"], workspace, check=False)

    assert result.returncode == 1
    assert "1 failed, 3 passed" in result.stdout
    assert "new_library" in result.stdout


def test_typescript_application_runs_from_spaces_and_unicode(tmp_path: Path) -> None:
    workspace = tmp_path / "project's café workspace" / "typescript"
    shutil.copytree(ROOT / "template/src/typescript", workspace)
    package_links = workspace / "node_modules/@example"
    package_links.mkdir(parents=True)
    (package_links / "core").symlink_to(workspace / "packages/core", target_is_directory=True)

    result = run(["bun", "test"], workspace)

    assert "3 pass" in result.stderr


def test_lychee_configuration_checks_local_heading_links(tmp_path: Path) -> None:
    (tmp_path / "target.md").write_text("# Existing heading\n")
    source = tmp_path / "source.md"
    source.write_text("# Source\n\n[Target](target.md#existing-heading)\n")
    command = [
        "lychee",
        "--config",
        str(ROOT / "template/lychee.toml"),
        "--offline",
        "--cache=false",
        "--no-progress",
        str(source),
    ]
    run(command, tmp_path)
    source.write_text("# Source\n\n[Target](target.md#missing-heading)\n")

    result = run(command, tmp_path, check=False)

    assert result.returncode != 0
    assert "Cannot find fragment" in result.stdout + result.stderr
