"""Exercise the two TypeScript variants and safe tagged update behavior."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

from tests.support import (
    LANGUAGES,
    answers,
    commit_all,
    git,
    render,
    run,
    snapshot_template,
    update,
)


def check_rendered_text(repo: Path) -> None:
    """Run the production whitespace gate before any runtime is installed."""
    files: list[str] = []
    for path in repo.rglob("*"):
        if not path.is_file():
            continue
        try:
            contents = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "\0" not in contents:
            files.append(str(path.relative_to(repo)))
    run(["bash", "infra/nix/check-text.sh", *files], repo)


@pytest.mark.parametrize("components", [False, True])
def test_typescript_has_two_complete_variants(
    template_source: Path, tmp_path: Path, components: bool
) -> None:
    repo = tmp_path / "project"
    render(
        template_source,
        repo,
        {"languages": ["typescript"], "typescript_components": components},
    )
    workspace = repo / "src/typescript"
    assert answers(repo)["typescript_components"] is components
    assert sorted(path.name for path in (repo / "src").iterdir()) == ["typescript"]
    assert sorted(path.name for path in (workspace / "apps").iterdir()) == (
        ["web"] if components else ["example-app"]
    )
    assert sorted(path.name for path in (workspace / "packages").iterdir()) == (
        ["ui"] if components else ["core"]
    )
    manifest = json.loads((workspace / "package.json").read_text())
    assert manifest["private"] is True
    assert manifest["workspaces"] == ["apps/*", "packages/*"]
    for name in (
        "scripts",
        "tests",
        "vitest.config.ts",
        "playwright.config.ts",
        "playwright.visual.config.ts",
    ):
        assert (workspace / name).exists() is components
    assert not (workspace / "apps/web/.env.local").exists()
    assert not (workspace / "node_modules").exists()
    assert not (workspace / "apps/web/.next").exists()
    assert not (repo / ".devenv").exists()
    for path in repo.rglob("*.json"):
        json.loads(path.read_text())
    assert not list(repo.rglob("*.copier"))
    check_rendered_text(repo)
    run(["just", "--list"], repo)
    run(["nixfmt", "--check", "devenv.nix", "infra/nix/devenv.nix"], repo)
    run(["statix", "check", "infra/nix"], repo)
    run(["actionlint", *map(str, (repo / ".github/workflows").glob("*.yml"))], repo)
    run(["rumdl", "check", "."], repo)


def test_components_coexist_with_other_languages_and_workflows(
    template_source: Path, tmp_path: Path
) -> None:
    repo = tmp_path / "project"
    render(
        template_source,
        repo,
        {
            "languages": list(LANGUAGES),
            "workflows": ["planning", "reference"],
            "agents": ["codex", "claude"],
            "secrets": True,
            "typescript_components": True,
        },
    )
    assert (repo / "src/typescript/apps/web/src/app/layout.tsx").is_file()
    assert (repo / "src/typescript/packages/ui/src/styles/tokens.css").is_file()
    assert (repo / ".context/plan").is_dir()
    assert (repo / ".context/reference").is_dir()
    assert (repo / ".agents").is_dir()
    for language in LANGUAGES:
        assert (repo / "src" / language).is_dir()
    check_rendered_text(repo)
    run(["just", "--list"], repo)
    run(["nixfmt", "--check", "devenv.nix", "infra/nix/devenv.nix"], repo)
    run(["statix", "check", "infra/nix"], repo)
    run(["actionlint", *map(str, (repo / ".github/workflows").glob("*.yml"))], repo)
    run(["rumdl", "check", "."], repo)


@pytest.mark.parametrize("languages", [[], ["python"]])
def test_components_require_typescript(
    template_source: Path, tmp_path: Path, languages: list[str]
) -> None:
    repo = tmp_path / "invalid"
    result = render(
        template_source,
        repo,
        {"languages": languages, "typescript_components": True},
        check=False,
    )
    assert result.returncode != 0
    assert "Select TypeScript" in result.stdout + result.stderr
    assert not (repo / ".copier-answers.yml").exists()


def test_components_question_is_absent_without_typescript(
    template_source: Path, tmp_path: Path
) -> None:
    repo = tmp_path / "project"
    render(template_source, repo)
    assert "typescript_components" not in answers(repo)
    assert not (repo / "src/typescript").exists()


def test_web_sources_are_tracked_but_generated_outputs_are_not(
    template_source: Path, tmp_path: Path
) -> None:
    repo = tmp_path / "project"
    render(
        template_source,
        repo,
        {"languages": ["typescript", "lean"], "typescript_components": True},
    )
    git(repo, "init", "--quiet", "--initial-branch=main")
    commit_all(repo, "feat(project): initialize")
    source = "src/typescript/apps/web/src/app/layout.tsx"
    assert source in git(repo, "ls-files").splitlines()
    for relative in (
        "src/typescript/apps/web/.env.local",
        "src/typescript/apps/web/next-env.d.ts",
        "src/typescript/apps/web/.next/server/app.js",
        "src/typescript/packages/ui/storybook-static/index.html",
        "src/typescript/playwright-report/index.html",
        "src/typescript/test-results/example/actual.png",
        "src/lean/blueprint/web/index.html",
        "src/lean/blueprint/print/blueprint.pdf",
    ):
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("generated output\n")
        assert git(repo, "check-ignore", relative) == relative
    assert not git(repo, "status", "--porcelain")


def next_release(source: Path) -> None:
    guide = source / "template/README.md.copier"
    guide.write_text(guide.read_text() + "\nUpdated project guidance.\n")
    commit_all(source, "docs(template): next guidance")
    git(source, "tag", "v0.2.0")


@pytest.mark.parametrize("components", [False, True])
def test_tagged_updates_preserve_typescript_variant_and_authored_code(
    tmp_path: Path, components: bool
) -> None:
    source = snapshot_template(tmp_path / "catalog")
    repo = tmp_path / "project"
    render(
        source,
        repo,
        {"languages": ["typescript"], "typescript_components": components},
        ref="v0.1.0",
    )
    git(repo, "init", "--quiet", "--initial-branch=main")
    target = (
        repo
        / "src/typescript"
        / ("packages/ui/src/styles/tokens.css" if components else "packages/core/src/index.ts")
    )
    target.write_text(target.read_text() + "\n/* Authored extension: preserve it. */\n")
    feature = (
        repo
        / "src/typescript"
        / (
            "apps/web/src/features/authored.ts"
            if components
            else "apps/example-app/src/authored.ts"
        )
    )
    feature.write_text('export const authored = "keep me";\n')
    commit_all(repo, "feat(project): authored feature and design")
    before = {path: path.read_bytes() for path in (target, feature)}
    # A changed template default must not silently migrate existing applications.
    config_path = source / "copier.yml"
    config = yaml.safe_load(config_path.read_text())
    config["typescript_components"]["default"] = not components
    config_path.write_text(yaml.safe_dump(config, sort_keys=False))
    next_release(source)
    update(repo)
    assert answers(repo)["_commit"] == "v0.2.0"
    assert answers(repo)["typescript_components"] is components
    assert {path: path.read_bytes() for path in before} == before
    assert "Updated project guidance." in (repo / "README.md").read_text()
    assert not git(repo, "diff", "--name-only", "--diff-filter=U")


@pytest.mark.parametrize(
    ("components", "legacy_answers"), [(False, False), (True, False), (False, True)]
)
def test_switching_existing_typescript_variant_fails_without_modifying_files(
    tmp_path: Path, components: bool, legacy_answers: bool
) -> None:
    source = snapshot_template(tmp_path / "catalog")
    repo = tmp_path / "project"
    render(
        source,
        repo,
        {"languages": ["typescript"], "typescript_components": components},
        ref="v0.1.0",
    )
    git(repo, "init", "--quiet", "--initial-branch=main")
    if legacy_answers:
        # Projects made before this option existed have no saved boolean.
        saved = answers(repo)
        del saved["typescript_components"]
        (repo / ".copier-answers.yml").write_text(yaml.safe_dump(saved, sort_keys=False))
    authored = (
        repo
        / "src/typescript"
        / ("packages/ui/src/styles/tokens.css" if components else "packages/core/src/index.ts")
    )
    authored.write_text(authored.read_text() + "\n/* Authored application extension. */\n")
    notes = repo / "authored.md"
    notes.write_text("# Project decisions\n\nKeep this authored content.\n")
    commit_all(repo, "feat(project): initialize with authored content")
    before = {
        relative: (repo / relative).read_bytes() for relative in git(repo, "ls-files").splitlines()
    }
    next_release(source)
    result = run(
        [
            sys.executable,
            "-m",
            "copier",
            "update",
            "--defaults",
            "-d",
            f"typescript_components={str(not components).lower()}",
        ],
        repo,
        check=False,
    )
    assert result.returncode != 0
    assert "Switching TypeScript variants requires a manual migration" in (
        result.stdout + result.stderr
    )
    assert not git(repo, "status", "--porcelain")
    assert {relative: (repo / relative).read_bytes() for relative in before} == before
    assert answers(repo)["_commit"] == "v0.1.0"


def test_adding_typescript_components_to_a_project_without_typescript(tmp_path: Path) -> None:
    source = snapshot_template(tmp_path / "catalog")
    repo = tmp_path / "project"
    render(source, repo, ref="v0.1.0")
    git(repo, "init", "--quiet", "--initial-branch=main")
    notes = repo / "authored.md"
    notes.write_text("# Project decisions\n\nKeep this content.\n")
    commit_all(repo, "docs(project): authored content")
    next_release(source)
    selection = tmp_path / "selection.yml"
    selection.write_text(
        yaml.safe_dump({"languages": ["typescript"], "typescript_components": True})
    )
    update(repo, "--data-file", str(selection))
    assert answers(repo)["typescript_components"] is True
    assert (repo / "src/typescript/apps/web/src/app/layout.tsx").is_file()
    assert not (repo / "src/typescript/apps/example-app").exists()
    assert notes.read_text() == "# Project decisions\n\nKeep this content.\n"
