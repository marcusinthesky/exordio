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


def test_adding_go_and_later_updates_preserve_module_identity_and_authored_code(
    tmp_path: Path,
) -> None:
    source = snapshot_template(tmp_path / "catalog")
    repo = tmp_path / "project"
    render(source, repo, ref="v0.1.0")
    git(repo, "init", "--quiet", "--initial-branch=main")
    notes = repo / "notes.md"
    notes.write_text("# Notes\n\nKeep these project decisions.\n")
    commit_all(repo, "docs(project): record authored decisions")
    assert "go_module" not in answers(repo)

    release(source)
    module = "github.com/acme/project/src/go"
    selection = tmp_path / "go-selection.yml"
    selection.write_text(yaml.safe_dump({"languages": ["go"], "go_module": module}))
    update(repo, "--data-file", str(selection))
    assert answers(repo)["languages"] == ["go"]
    assert answers(repo)["go_module"] == module
    assert not (repo / "src/python").exists()
    assert notes.read_text() == "# Notes\n\nKeep these project decisions.\n"

    authored = repo / "src/go/greet/authored.go"
    authored.write_text('package greet\n\nconst AuthoredMessage = "keep me"\n')
    commit_all(repo, "feat(project): implement custom Go behavior")
    preserved = {path: path.read_bytes() for path in (notes, authored, repo / "src/go/go.mod")}
    guide = source / "template/src/go/README.md.copier"
    guide.write_text(guide.read_text() + "\nUpdated Go guidance.\n")
    commit_all(source, "docs(template): refine Go guidance")
    git(source, "tag", "v0.3.0")
    update(repo)

    assert answers(repo)["_commit"] == "v0.3.0"
    assert answers(repo)["go_module"] == module
    assert {path: path.read_bytes() for path in preserved} == preserved
    assert "Updated Go guidance." in (repo / "src/go/README.md").read_text()
    assert f'"{module}/greet"' in (repo / "src/go/cmd/example-app/main.go").read_text()


def test_rust_can_be_added_and_updated_without_replacing_authored_code(tmp_path: Path) -> None:
    source = snapshot_template(tmp_path / "catalog")
    repo = tmp_path / "project"
    render(source, repo, ref="v0.1.0")
    git(repo, "init", "--quiet", "--initial-branch=main")
    instructions = repo / "AGENTS.md"
    instructions.write_text("# Project instructions\n\nPreserve project-specific guidance.\n")
    commit_all(repo, "feat(project): initialize without languages")
    assert not (repo / "src/rust").exists()
    release(source)

    selection = tmp_path / "rust-selection.yml"
    selection.write_text(yaml.safe_dump({"languages": ["rust"]}))
    update(repo, "--data-file", str(selection))
    assert answers(repo)["languages"] == ["rust"]
    assert answers(repo)["workflows"] == []
    assert (repo / "src/rust/Cargo.lock").is_file()
    library = repo / "src/rust/src/lib.rs"
    library.write_text(library.read_text() + '\npub const PROJECT_NAME: &str = "authored";\n')
    before = {path: path.read_bytes() for path in (instructions, library)}
    commit_all(repo, "feat(project): customize Rust library")

    guidance = source / "template/src/rust/ARCHITECTURE.md"
    guidance.write_text(guidance.read_text() + "\nUpdated Rust template guidance.\n")
    commit_all(source, "docs(template): refine Rust guidance")
    git(source, "tag", "v0.3.0")
    update(repo)

    assert answers(repo)["_commit"] == "v0.3.0"
    assert answers(repo)["languages"] == ["rust"]
    assert {path: path.read_bytes() for path in before} == before
    assert "Updated Rust template guidance." in (repo / "src/rust/ARCHITECTURE.md").read_text()
