"""Copy the current template into Git without modifying the working branch."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.support import snapshot_template


@pytest.fixture(scope="session")
def template_source(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return snapshot_template(tmp_path_factory.mktemp("source") / "catalog")
