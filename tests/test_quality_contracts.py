"""The catalog and generated project must agree on portable quality contracts."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from tests.support import ROOT, render


def test_renovate_policy_is_shared_by_catalog_and_generated_projects() -> None:
    catalog = json.loads((ROOT / "renovate.json").read_text())
    generated = json.loads((ROOT / "template/renovate.json").read_text())
    assert catalog == generated
    assert "config:recommended" in catalog["extends"]
    assert catalog["dependencyDashboard"] is True


def test_generated_workflow_skips_drafts_and_supports_ready_review(
    template_source: Path, tmp_path: Path
) -> None:
    destination = tmp_path / "project"
    render(template_source, destination, {"languages": ["typescript"]})
    workflow = (destination / ".github/workflows/ci.yml").read_text()
    assert "ready_for_review" in workflow
    assert "converted_to_draft" in workflow
    assert "github.event.pull_request.draft == false" in workflow
    assert "branches: [main]" in workflow
    assert not (destination / "QUALITY.md").exists()
    assert (destination / "src/typescript/knip.json").exists()
    assert json.loads((destination / "renovate.json").read_text())["dependencyDashboard"]


def test_catalog_quality_config_is_valid_yaml() -> None:
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    assert isinstance(workflow["jobs"], dict)
    assert "check" in workflow["jobs"]
