"""Exercise the Nix-built CLI in agent-only projects without a Bun fallback."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.support import commit_all, git, render, run


@pytest.mark.parametrize("agents", [["codex"], ["claude"], ["codex", "claude"]])
def test_native_agentsync_needs_no_npm_setup(
    template_source: Path, tmp_path: Path, agents: list[str]
) -> None:
    repo = tmp_path / "project"
    render(template_source, repo, {"agents": agents})
    assert not (repo / "tools/agents").exists()
    assert not (repo / "src/python/apps").exists()
    assert not (repo / "src/typescript").exists()
    module = (repo / "infra/nix/devenv.nix").read_text()
    assert "agentsync.nix" in module and "bun" not in module and "patchelf" not in module
    git(repo, "init", "--quiet", "--initial-branch=main")
    commit_all(repo, "test: native AgentSync fixture")
    environment = {"UV_OFFLINE": "1", "HTTPS_PROXY": "http://127.0.0.1:9"}
    run(["just", "setup"], repo, extra_env=environment)
    run(["just", "agents::apply"], repo, extra_env=environment)
    run(["just", "agents::check"], repo, extra_env=environment)
    assert (repo / "AGENTS.md").is_symlink()
    assert not list(repo.rglob("*.bak"))
    assert git(repo, "status", "--porcelain=v1") == ""
