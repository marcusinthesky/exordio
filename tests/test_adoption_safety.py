"""Protect authored native agent configuration before installing managed links."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest
import yaml

from tests.support import (
    commit_all,
    git,
    render,
    run,
    snapshot_template,
    update,
)

PREFLIGHT = [
    "uv",
    "run",
    "--offline",
    "--frozen",
    "--script",
    "src/python/scripts/agent_preflight/script.py",
]


@pytest.mark.parametrize("agents", [["codex"], ["claude"], ["codex", "claude"]])
def test_adding_agents_preserves_tracked_instructions(tmp_path: Path, agents: list[str]) -> None:
    source = snapshot_template(tmp_path / "catalog")
    repo = tmp_path / "project"
    render(source, repo, ref="v0.1.0")
    git(repo, "init", "--quiet", "--initial-branch=main")
    instructions = repo / "AGENTS.md"
    instructions.write_text("# Project rules\n\nKeep these authored instructions.\n")
    commit_all(repo, "docs(project): add authored instructions")

    readme = source / "template/README.md.copier"
    readme.write_text(readme.read_text() + "\nUpgrade fixture.\n")
    commit_all(source, "feat(template): next fixture release")
    git(source, "tag", "v0.2.0")
    selections = tmp_path / "agents.yml"
    selections.write_text(yaml.safe_dump({"agents": agents}))
    update(repo, "--data-file", str(selections))
    commit_all(repo, "feat(project): enable managed agent configuration")
    before = instructions.read_bytes()

    result = run(["just", "agents::apply"], repo, check=False)

    assert result.returncode != 0
    assert "before changing any native targets" in result.stderr
    assert "AGENTS.md" in result.stderr
    assert instructions.read_bytes() == before
    assert not instructions.is_symlink()
    assert not list(repo.rglob("*.bak"))
    assert git(repo, "status", "--porcelain=v1") == ""


@pytest.mark.parametrize(
    ("agent", "target", "directory"),
    [
        ("codex", ".codex/config.toml", False),
        ("codex", ".codex/skills", True),
        ("claude", "CLAUDE.md", False),
        ("claude", ".claude/settings.json", False),
        ("claude", ".claude/skills", True),
    ],
)
def test_late_collisions_stop_before_creating_any_links(
    template_source: Path, tmp_path: Path, agent: str, target: str, directory: bool
) -> None:
    repo = tmp_path / "project"
    render(template_source, repo, {"agents": [agent]})
    destination = repo / target
    destination.parent.mkdir(parents=True, exist_ok=True)
    if directory:
        destination.mkdir()
        authored = destination / "custom.md"
    else:
        authored = destination
    authored.write_text("Keep this authored configuration.\n")
    before = authored.read_bytes()

    result = run(["just", "agents::apply"], repo, check=False)

    assert result.returncode != 0
    assert "before changing any native targets" in result.stderr
    assert target in result.stderr
    assert authored.read_bytes() == before
    assert not (repo / "AGENTS.md").exists()
    assert not list(repo.rglob("*.bak"))


@pytest.mark.parametrize("parent_link", [False, True], ids=["unexpected-target", "parent-link"])
def test_unexpected_symlinks_are_preserved(
    template_source: Path, tmp_path: Path, parent_link: bool
) -> None:
    repo = tmp_path / "project"
    render(template_source, repo, {"agents": ["codex"]})
    outside = tmp_path / "authored"
    outside.mkdir()
    original = outside / "config.toml"
    original.write_text("keep = true\n")
    if parent_link:
        link = repo / ".codex"
        link.symlink_to(outside, target_is_directory=True)
    else:
        (repo / ".codex").mkdir()
        link = repo / ".codex/config.toml"
        link.symlink_to(original)
    target = link.readlink()

    result = run(["just", "agents::apply"], repo, check=False)

    assert result.returncode != 0
    assert "before changing any native targets" in result.stderr
    assert link.readlink() == target
    assert original.read_text() == "keep = true\n"
    assert not (repo / "AGENTS.md").exists()


def test_targets_cannot_claim_the_repository_parent(template_source: Path, tmp_path: Path) -> None:
    repo = tmp_path / "project"
    render(template_source, repo, {"agents": ["codex"]})
    configuration = repo / ".agents/agentsync.toml"
    configuration.write_text(
        configuration.read_text().replace('destination = "AGENTS.md"', 'destination = ".."')
    )

    result = run(["just", "agents::apply"], repo, check=False, timeout=10)

    assert result.returncode != 0
    assert "repository-owned sources" in result.stderr
    assert not (repo / "AGENTS.md").exists()


@pytest.mark.parametrize("agents", [["codex"], ["claude"], ["codex", "claude"]])
def test_preflight_accepts_fresh_and_already_managed_targets(
    template_source: Path, tmp_path: Path, agents: list[str]
) -> None:
    repo = tmp_path / "project"
    render(template_source, repo, {"agents": agents})
    run(PREFLIGHT, repo)
    configuration = tomllib.loads((repo / ".agents/agentsync.toml").read_text())
    for agent in agents:
        for target in configuration["agents"][agent]["targets"].values():
            destination = repo / target["destination"]
            source = repo / ".agents" / target["source"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.symlink_to(source, target_is_directory=source.is_dir())
    before = {path: path.readlink() for path in repo.rglob("*") if path.is_symlink()}

    run(PREFLIGHT, repo)
    run(PREFLIGHT, repo)

    assert {path: path.readlink() for path in before} == before
    assert not list(repo.rglob("*.bak"))


@pytest.mark.parametrize("kind", ["file", "missing", "parent"])
def test_canonical_sources_cannot_escape_through_symlinks(
    template_source: Path, tmp_path: Path, kind: str
) -> None:
    repo = tmp_path / "project"
    render(template_source, repo, {"agents": ["codex"]})
    outside = tmp_path / "authored"
    outside.mkdir()
    authored = outside / "AGENTS.md"
    authored.write_text("Keep this external source.\n")
    source = repo / ".agents/AGENTS.md"
    source.unlink()
    if kind == "parent":
        alias = repo / ".agents/external"
        alias.symlink_to(outside, target_is_directory=True)
        configuration = repo / ".agents/agentsync.toml"
        configuration.write_text(
            configuration.read_text().replace(
                'source = "AGENTS.md"', 'source = "external/AGENTS.md"'
            )
        )
    else:
        source.symlink_to(authored if kind == "file" else outside / "missing.md")
    result = run(["just", "agents::apply"], repo, check=False)
    assert result.returncode != 0
    assert "before changing any native targets" in result.stderr
    assert "is a symlink" in result.stderr
    assert authored.read_text() == "Keep this external source.\n"
    assert not (repo / "AGENTS.md").exists()
    assert not list(repo.rglob("*.bak"))
