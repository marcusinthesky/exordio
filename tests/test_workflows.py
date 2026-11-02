"""Keep authored content safe and derived views honest through real commands."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

from tests.support import WORKFLOW, render, run, workflow


@pytest.fixture
def repo(template_source: Path, tmp_path: Path) -> Path:
    destination = tmp_path / "project's workspace"
    render(template_source, destination, {"workflows": ["planning", "reference"]})
    workflow(destination, "prepare")
    return destination


@pytest.fixture
def helper(repo: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("generated_workflow", repo / WORKFLOW)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def change(helper: ModuleType, path: Path, **values: object) -> None:
    data, body = helper.read_document(path)
    path.write_text(helper.serialize(data | values, body))


def plan_and_task(repo: Path) -> tuple[Path, Path]:
    workflow(repo, "plan-new", "project", "--title", "Project plan")
    workflow(repo, "task-new", ".context/plan/project", "first", "--title", "First task")
    return (
        repo / ".context/plan/project/README.md",
        repo / ".context/plan/project/tasks/first/README.md",
    )


def test_explicit_creation_preserves_user_content(repo: Path, helper: ModuleType) -> None:
    assert helper.read_records(repo) == []
    _, task = plan_and_task(repo)
    task.write_text(task.read_text() + "\nMy authored evidence.\n")
    before = task.read_bytes()
    duplicate = workflow(
        repo,
        "task-new",
        str(task.parent.parent.parent.relative_to(repo)),
        "first",
        "--title",
        "Replacement",
        check=False,
    )
    assert duplicate.returncode != 0
    assert task.read_bytes() == before
    assert helper.validate_records(repo) == []
    run(["just", "reference-new", "literal-title", "A title with spaces and $tokens"], repo)
    assert (
        "A title with spaces and $tokens"
        in (repo / ".context/reference/literal-title/README.md").read_text()
    )


@pytest.mark.parametrize("parent", ["../outside", ".context/reference", ".context/plan/missing"])
def test_invalid_parents_and_slugs_cannot_create_records(repo: Path, parent: str) -> None:
    result = workflow(repo, "task-new", parent, "escape", "--title", "Escape", check=False)
    assert result.returncode != 0
    assert not (repo.parent / "outside").exists()
    assert workflow(repo, "plan-new", "../escape", "--title", "Escape", check=False).returncode != 0


@pytest.mark.parametrize(
    ("enabled", "command"), [(["planning"], "reference-new"), (["reference"], "plan-new")]
)
def test_commands_respect_selected_workflows(
    template_source: Path, tmp_path: Path, enabled: list[str], command: str
) -> None:
    destination = tmp_path / "project"
    render(template_source, destination, {"workflows": enabled})
    workflow(destination, "prepare")
    assert (
        workflow(destination, command, "missing", "--title", "Missing", check=False).returncode != 0
    )


def test_nested_views_show_immediate_children_and_detect_stale_content(
    repo: Path, helper: ModuleType
) -> None:
    parent, task = plan_and_task(repo)
    workflow(
        repo, "task-new", str(task.parent.relative_to(repo)), "nested", "--title", "Nested detail"
    )
    workflow(repo, "sync")
    workflow(repo, "check")
    assert "First task" in parent.read_text() and "Nested detail" not in parent.read_text()
    assert "Nested detail" in task.read_text()
    assert "Project plan" in (repo / "ROADMAP.md").read_text()
    assert "First task" not in (repo / "ROADMAP.md").read_text()
    change(helper, task, title="Updated task", description="Updated summary", status="in-progress")
    before = {p: p.read_bytes() for p in (parent, task)}
    assert workflow(repo, "check", check=False).returncode != 0
    assert {p: p.read_bytes() for p in before} == before
    workflow(repo, "sync")
    workflow(repo, "check")
    assert "Updated task" in parent.read_text() and "in-progress" in parent.read_text()


def test_done_requires_active_checked_acceptance(repo: Path, helper: ModuleType) -> None:
    _, task = plan_and_task(repo)
    invalid = [
        "",
        "Prose alone.\n",
        "- [x]    \n",
        "- [x] ~~Retired.~~\n",
        "```md\n- [x] Example.\n```\n",
        "<!--\n- [x] Hidden.\n-->\n",
        "- [x] Verified.\n- [ ] Pending.\n",
    ]
    for acceptance in invalid:
        assert not helper.verified_acceptance("# Task\n\n## Acceptance\n\n" + acceptance)
    assert helper.verified_acceptance(
        "# Task\n\n## Acceptance\n\n- [X] Verified.\n- [ ] ~~Retired.~~\n"
        "\n## Ideas\n\n- [ ] Optional.\n"
    )
    change(helper, task, status="done")
    assert helper.validate_records(repo)
    task.write_text(task.read_text().replace("- [ ]", "- [x]"))
    assert helper.validate_records(repo) == []


def test_closed_requires_reason_and_terminal_parents_cannot_hide_work(
    repo: Path, helper: ModuleType
) -> None:
    parent, task = plan_and_task(repo)
    change(helper, task, status="closed")
    assert helper.validate_records(repo)
    change(helper, task, resolution={"reason": "No longer needed"})
    assert helper.validate_records(repo) == []
    change(helper, task, status="backlog")
    change(helper, parent, status="closed", resolution={"reason": "Stopped"})
    assert helper.validate_records(repo)


def test_canonical_links_and_native_backlinks(repo: Path, helper: ModuleType) -> None:
    parent, task = plan_and_task(repo)
    workflow(repo, "reference-new", "paper", "--title", "Useful paper")
    target = ".context/reference/paper/README.md"
    for link in (
        "./" + target,
        target + "#summary",
        "https://example.com",
        "missing.md",
        "../outside.md",
    ):
        change(helper, task, links=[link])
        assert helper.validate_records(repo), link
    (repo / "alias.md").symlink_to(repo / target)
    change(helper, task, links=["alias.md"])
    assert helper.validate_records(repo)
    change(helper, task, links=[target])
    task.write_text(task.read_text() + "\n[Body URL](https://example.com).\n")
    workflow(repo, "sync")
    workflow(repo, "check")
    assert "First task" in (repo / target).read_text()
    assert "First task" in parent.read_text()


def test_validation_rejects_duplicate_yaml_and_wrong_roles(repo: Path, helper: ModuleType) -> None:
    _, task = plan_and_task(repo)
    original = task.read_text()
    task.write_text(original.replace("status: backlog", "status: backlog\nstatus: done"))
    with pytest.raises(ValueError, match="duplicate"):
        helper.read_records(repo)
    task.write_text(original)
    change(helper, task, type="document")
    before = task.read_bytes()
    result = workflow(repo, "check", check=False)
    assert result.returncode != 0 and "type" in result.stdout + result.stderr
    assert task.read_bytes() == before


def test_roadmap_budget_is_checked_without_rewriting(repo: Path) -> None:
    path = repo / "ROADMAP.md"
    path.write_text(path.read_text() + "\n" + "Many roadmap details. " * 2500)
    before = path.read_bytes()
    result = workflow(repo, "check", check=False)
    assert result.returncode != 0 and "1500" in result.stdout + result.stderr
    assert path.read_bytes() == before


def test_flat_references_generate_current_bibliography(
    template_source: Path, tmp_path: Path
) -> None:
    destination = tmp_path / "project"
    render(template_source, destination, {"workflows": ["reference"], "languages": ["latex"]})
    workflow(destination, "prepare")
    workflow(destination, "reference-new", "paper-key", "--title", "Useful paper")
    reference = destination / ".context/reference/paper-key/README.md"
    assert "csl:" not in reference.read_text() and "\nid:" not in reference.read_text()
    workflow(destination, "sync")
    workflow(destination, "check")
    bibliography = destination / "src/latex/refs.bib"
    assert all(text in bibliography.read_text().lower() for text in ("paper-key", "useful paper"))
    reference.write_text(reference.read_text().replace("Useful paper", "Updated paper"))
    assert workflow(destination, "check", check=False).returncode != 0
    workflow(destination, "sync")
    workflow(destination, "check")
    assert "updated paper" in bibliography.read_text().lower()
