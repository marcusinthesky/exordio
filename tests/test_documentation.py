"""Exercise the printed first-project journey and native local previews."""

from __future__ import annotations

import re
import shlex
from pathlib import Path

from tests.support import COPIER, ROOT, git, run, snapshot_template


def test_printed_walkthrough_delivers_current_parent_views(
    template_source: Path, tmp_path: Path
) -> None:
    guide = (ROOT / "docs/index.md").read_text()
    lines = [
        line
        for block in re.findall(r"```bash\n(.*?)```", guide, re.DOTALL)
        for line in block.splitlines()
    ]
    creation = shlex.split(next(line for line in lines if "copier copy" in line))
    assert "copier==9.16.0" in creation
    arguments = creation[creation.index("copier") + 1 :]
    repo = tmp_path / "project's tutorial"
    arguments[-2:] = [str(template_source), str(repo)]
    run([*COPIER, *arguments], template_source)
    git(repo, "init", "--quiet", "--initial-branch=main")
    for line in lines:
        if line.startswith("just "):
            run(shlex.split(line), repo, extra_env={"UV_OFFLINE": "1"})
    task = repo / ".context/plan/project/tasks/first-step/README.md"
    parent = repo / ".context/plan/project/README.md"
    assert "Make the first useful change" in parent.read_text()
    task.write_text(task.read_text().replace("status: backlog", "status: in-progress"))
    run(["just", "sync"], repo)
    run(["just", "check"], repo, extra_env={"UV_OFFLINE": "1"})
    assert "in-progress" in parent.read_text()
    assert "Project plan" in (repo / "ROADMAP.md").read_text()


def test_native_preview_includes_dirty_changes_without_changing_source_index(
    tmp_path: Path,
) -> None:
    source = snapshot_template(tmp_path / "source")
    path = source / "template/preview-proof.txt"
    path.write_text("Committed.\n")
    git(source, "add", "template/preview-proof.txt")
    git(source, "commit", "--quiet", "--message", "test: preview fixture")
    path.write_text("Dirty tracked content.\n")
    added = source / "template/untracked-proof.txt"
    added.write_text("New content.\n")
    before = (source / ".git/index").read_bytes()
    destination = tmp_path / "preview"
    run(
        [
            *COPIER,
            "copy",
            "--defaults",
            "--vcs-ref",
            "HEAD",
            str(source),
            str(destination),
        ],
        source,
    )
    assert (destination / path.name).read_text() == "Dirty tracked content.\n"
    assert (destination / added.name).read_text() == "New content.\n"
    assert (source / ".git/index").read_bytes() == before
    assert run(["just", "render", str(destination)], ROOT, check=False).returncode != 0
    assert (destination / path.name).read_text() == "Dirty tracked content.\n"
