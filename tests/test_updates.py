"""Tagged updates preserve authored records and expose configuration conflicts."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from tests.support import (
    answers,
    commit_all,
    git,
    render,
    snapshot_template,
    update,
    workflow,
)


def project(source: Path, repo: Path) -> None:
    render(source, repo, {"workflows": ["planning"]}, ref="v0.1.0")
    git(repo, "init", "--quiet", "--initial-branch=main")
    commit_all(repo, "feat(project): initialize")
    workflow(repo, "prepare")


def release(source: Path) -> None:
    readme = source / "template/README.md.copier"
    readme.write_text(readme.read_text() + "\nNew template guidance.\n")
    commit_all(source, "feat(template): next fixture release")
    git(source, "tag", "v0.2.0")


def test_upgrade_preserves_authored_records_deletions_and_populated_views(
    tmp_path: Path,
) -> None:
    source = snapshot_template(tmp_path / "catalog")
    repo = tmp_path / "project"
    project(source, repo)
    workflow(repo, "plan-new", "project", "--title", "Project plan")
    workflow(repo, "task-new", ".context/plan/project", "first", "--title", "First task")
    workflow(repo, "task-new", ".context/plan/project", "deleted", "--title", "Deleted task")
    task = repo / ".context/plan/project/tasks/first/README.md"
    task.write_text(task.read_text() + "\nMy authored evidence.\n")
    instructions = repo / "AGENTS.md"
    instructions.write_text("# Project instructions\n\nProject-specific instructions.\n")
    commit_all(repo, "docs(project): write records")
    deleted = repo / ".context/plan/project/tasks/deleted"
    shutil.rmtree(deleted)
    workflow(repo, "sync")
    commit_all(repo, "docs(project): retire a task and refresh views")
    before = {p: p.read_bytes() for p in (task, instructions)}
    roadmap = source / "template/ROADMAP.md"
    roadmap.write_text(roadmap.read_text() + "\nUpdated navigation guidance.\n")
    release(source)
    update(repo)
    workflow(repo, "sync")
    workflow(repo, "check")
    data = (repo / ".copier-answers.yml").read_bytes()
    assert data.endswith(b"\n") and not data.endswith(b"\n\n")
    assert answers(repo)["_commit"] == "v0.2.0"
    assert {p: p.read_bytes() for p in before} == before
    assert not deleted.exists()
    assert "New template guidance." in (repo / "README.md").read_text()
    assert "Updated navigation guidance." in (repo / "ROADMAP.md").read_text()
    assert "Project plan" in (repo / "ROADMAP.md").read_text()


@pytest.mark.parametrize("add_language", [False, True])
def test_saved_empty_choices_and_additive_language_updates(
    tmp_path: Path, add_language: bool
) -> None:
    source = snapshot_template(tmp_path / "catalog")
    repo = tmp_path / "project"
    project(source, repo)
    config_path = source / "copier.yml"
    config = yaml.safe_load(config_path.read_text())
    config["languages"]["default"] = ["python"]
    config_path.write_text(yaml.safe_dump(config, sort_keys=False))
    release(source)
    arguments: list[str] = []
    if add_language:
        selection = tmp_path / "new-selection.yml"
        selection.write_text(yaml.safe_dump({"languages": ["python"]}))
        arguments = ["--data-file", str(selection)]
    update(repo, *arguments)
    assert answers(repo)["workflows"] == ["planning"]
    assert answers(repo)["languages"] == (["python"] if add_language else [])
    assert (repo / "src/python/apps").exists() == add_language
    assert (repo / "src/python/scripts/workflow/script.py").is_file()


def test_conflicting_configuration_changes_remain_reviewable(tmp_path: Path) -> None:
    source = snapshot_template(tmp_path / "catalog")
    config_source = source / "template/upgrade-settings.yml"
    config_source.write_text("mode: baseline\n")
    commit_all(source, "feat(template): fixture configuration")
    git(source, "tag", "--force", "v0.1.0")
    repo = tmp_path / "project"
    project(source, repo)
    config = repo / "upgrade-settings.yml"
    config.write_text("mode: project-choice\n")
    commit_all(repo, "feat(project): customize configuration")
    config_source.write_text("mode: template-choice\n")
    release(source)
    update(repo)
    assert all(
        text in config.read_text()
        for text in ("project-choice", "template-choice", "<<<<<<<", ">>>>>>>")
    )
