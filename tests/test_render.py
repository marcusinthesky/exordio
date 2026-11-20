"""Render the supported choices through Copier's real public interface."""

from __future__ import annotations

import json
import os
import sys
import tomllib
from pathlib import Path

import pytest
import yaml

from tests.support import LANGUAGES, ROOT, WORKFLOWS, answers, render, run

CASES = [
    ([], []),
    (["planning"], []),
    (["reference"], []),
    (["planning", "reference"], []),
    *[([], [language]) for language in LANGUAGES],
    (["reference"], ["latex"]),
    (["planning"], ["lean"]),
    (["planning"], ["typescript"]),
    (["planning"], ["go"]),
    (["reference"], ["go"]),
    (["planning", "reference"], list(LANGUAGES)),
]


@pytest.mark.parametrize(("workflows", "languages"), CASES)
def test_supported_compositions(
    template_source: Path, tmp_path: Path, workflows: list[str], languages: list[str]
) -> None:
    repo = tmp_path / "project"
    maximal = set(workflows) == set(WORKFLOWS) and set(languages) == set(LANGUAGES)
    render(
        template_source,
        repo,
        {
            "workflows": workflows,
            "languages": languages,
            "agents": ["codex", "claude"] if maximal else [],
            "secrets": maximal,
        },
    )
    # Generated CI must skip compute-heavy jobs while a PR remains a draft.
    ci = (repo / ".github/workflows/ci.yml").read_text()
    assert not (repo / "QUALITY.md").exists()
    assert "ready_for_review" in ci
    assert "github.event.pull_request.draft == false" in ci
    data = (repo / ".copier-answers.yml").read_bytes()
    assert data.endswith(b"\n") and not data.endswith(b"\n\n")
    assert answers(repo)["workflows"] == workflows
    assert answers(repo)["languages"] == languages
    for language in LANGUAGES:
        assert (repo / "src" / language).is_dir() == (
            language in languages or language == "python" and bool(workflows)
        )
    assert (repo / "ROADMAP.md").exists() == ("planning" in workflows)
    assert (repo / ".context/plan").exists() == ("planning" in workflows)
    assert (repo / ".context/reference").exists() == ("reference" in workflows)
    assert (repo / "src/python/scripts/workflow/script.py").exists() == bool(workflows)
    assert (repo / "src/python/apps").exists() == ("python" in languages)
    assert not (repo / "AGENTS.md").exists()
    assert (repo / ".agents").is_dir() == maximal
    assert (repo / "secretspec.toml").exists() == maximal
    assert not any(
        (repo / name).exists()
        for name in ("infra/terraform", "infra/k8s", ".template.json", "tools")
    )
    for path in repo.rglob("*"):
        if not path.is_file():
            continue
        assert path.suffix != ".copier", path
        if path.suffix == ".json":
            json.loads(path.read_text())
        elif path.suffix in {".yml", ".yaml"}:
            list(yaml.safe_load_all(path.read_text()))
        elif path.suffix == ".toml" or path.name in {"uv.lock", "Cargo.lock"}:
            tomllib.loads(path.read_text())
    run(["nixfmt", "--check", "devenv.nix", *map(str, (repo / "infra/nix").rglob("*.nix"))], repo)
    run(["statix", "check", "infra/nix"], repo)
    run(["actionlint", *map(str, (repo / ".github/workflows").glob("*.yml"))], repo)
    run(["rumdl", "check", "."], repo)
    run(["just", "--list"], repo)
    entries = ["README.md"]
    if maximal:
        entries.append(".agents/AGENTS.md")
    if "planning" in workflows:
        entries.append("ROADMAP.md")
    run(
        [
            "schematter",
            "validate",
            "--schema",
            str(ROOT / "template/infra/schemas/documents/budget.document-schema.yaml"),
            *entries,
        ],
        repo,
    )
    if workflows:
        assert "{{" in "".join(p.read_text() for p in (repo / "insitu").rglob("*.j2"))
    assert "${{" in (repo / ".github/workflows/ci.yml").read_text()


def test_rust_selection_has_no_implicit_workflow_or_other_language(
    template_source: Path, tmp_path: Path
) -> None:
    repo = tmp_path / "project"
    render(template_source, repo, {"languages": ["rust"]})

    assert answers(repo)["workflows"] == []
    assert sorted(path.name for path in (repo / "src").iterdir()) == ["rust"]
    manifest = tomllib.loads((repo / "src/rust/Cargo.toml").read_text())
    lock = tomllib.loads((repo / "src/rust/Cargo.lock").read_text())
    assert manifest["package"]["name"] == "example-app"
    assert lock["package"] == [{"name": "example-app", "version": "0.1.0"}]
    assert not (repo / "src/rust/target").exists(), "Rendering must not run Cargo"


@pytest.mark.parametrize(
    "values",
    [
        {"project_slug": "../outside"},
        {"project_slug": "has spaces"},
        {"workflows": ["unknown"]},
        {"languages": ["unknown"]},
        {"languages": ["go"], "go_module": "https://github.com/acme/project"},
        {"languages": ["go"], "go_module": "example.com/../project"},
        {"languages": ["go"], "go_module": "example.com/project\nreplace bad => ./bad"},
    ],
)
def test_invalid_answers_do_not_create_a_project(
    template_source: Path, tmp_path: Path, values: dict[str, object]
) -> None:
    repo = tmp_path / "invalid"
    assert render(template_source, repo, values, check=False).returncode != 0
    assert not (repo / ".copier-answers.yml").exists()


def test_defaults_and_quoted_identity(template_source: Path, tmp_path: Path) -> None:
    repo = tmp_path / "project"
    render(
        template_source,
        repo,
        {
            "project_name": 'Café & "Research"',
            "project_slug": "custom-project",
            "description": 'A "quoted" purpose.',
        },
    )
    assert answers(repo)["workflows"] == []
    assert answers(repo)["languages"] == []
    assert "go_module" not in answers(repo)
    assert 'Café & "Research"' in (repo / "README.md").read_text()


@pytest.mark.parametrize(
    "module", ["github.com/acme/project/src/go", "example.com/Team/project/v2"]
)
def test_go_module_identity_is_saved_and_used_by_the_cli(
    template_source: Path, tmp_path: Path, module: str
) -> None:
    repo = tmp_path / "project"
    render(template_source, repo, {"languages": ["go"], "go_module": module})

    assert answers(repo)["go_module"] == module
    assert f"module {module}\n" in (repo / "src/go/go.mod").read_text()
    assert f'"{module}/greet"' in (repo / "src/go/cmd/example-app/main.go").read_text()
    assert not (repo / "src/go/go.sum").exists()
    assert not (repo / "src/go/go.work").exists()
    assert not (repo / "src/python").exists()
    assert not (repo / "src/typescript").exists()


def test_go_default_module_uses_the_project_slug(template_source: Path, tmp_path: Path) -> None:
    repo = tmp_path / "project"
    render(template_source, repo, {"languages": ["go"], "project_slug": "custom-project"})

    assert answers(repo)["go_module"] == "example.com/custom-project"
    assert "module example.com/custom-project\n" in (repo / "src/go/go.mod").read_text()


def test_secret_run_preserves_literal_arguments(template_source: Path, tmp_path: Path) -> None:
    repo = tmp_path / "project"
    render(template_source, repo, {"secrets": True})
    binary = tmp_path / "bin/secretspec"
    binary.parent.mkdir()
    binary.write_text(f"#!{sys.executable}\nimport json, sys\nprint(json.dumps(sys.argv[1:]))\n")
    binary.chmod(0o755)
    arguments = ["printf", "%s", "two words", "literal$token"]
    result = run(
        ["just", "secret-run", *arguments],
        repo,
        extra_env={"PATH": str(binary.parent) + os.pathsep + os.environ["PATH"]},
    )
    assert json.loads(result.stdout) == ["run", "--", *arguments]
