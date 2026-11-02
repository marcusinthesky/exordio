"""Check native runtime preparation against a real hard-linked ELF fixture."""

from __future__ import annotations

import os
import shutil
import stat
from pathlib import Path

import pytest

from tests.support import ROOT, run


@pytest.mark.integration
def test_runtime_preparation_preserves_the_package_cache_and_is_idempotent(
    tmp_path: Path,
) -> None:
    script = ROOT / "template/infra/nix/prepare-runtime.sh"
    patchelf = shutil.which("patchelf")
    executable = shutil.which("true")
    assert patchelf is not None and executable is not None, "Enter the pinned devenv shell"

    cached = tmp_path / "cache/true"
    cached.parent.mkdir()
    shutil.copy2(Path(executable).resolve(), cached)
    source_mode = cached.stat().st_mode
    cached.chmod(source_mode | stat.S_IWUSR)
    interpreter = run([patchelf, "--print-interpreter", str(cached)], tmp_path).stdout.strip()
    assert "ld-linux" in interpreter, "The fixture must be a GNU/Linux dynamic executable"
    original_rpath = run([patchelf, "--print-rpath", str(cached)], tmp_path).stdout.strip()
    # Force a preparation step even when the host executable already uses Nix.
    run(
        [patchelf, "--set-rpath", "/template-test-unprepared:" + original_rpath, str(cached)],
        tmp_path,
    )
    cached.chmod(source_mode)
    cached_content = cached.read_bytes()
    cached_mode = cached.stat().st_mode
    installed = tmp_path / "installed/true"
    installed.parent.mkdir()
    os.link(cached, installed)
    assert installed.stat().st_ino == cached.stat().st_ino

    linker = os.environ.get("PROJECT_RUNTIME_LINKER", interpreter)
    libraries = os.environ.get("PROJECT_RUNTIME_LIBRARIES", str(Path(interpreter).parent))
    environment = {
        "PROJECT_RUNTIME_LINKER": linker,
        "PROJECT_RUNTIME_LIBRARIES": libraries,
    }
    run(["bash", str(script), str(installed)], tmp_path, extra_env=environment)

    assert cached.read_bytes() == cached_content
    assert cached.stat().st_mode == cached_mode
    assert installed.stat().st_ino != cached.stat().st_ino
    assert run([patchelf, "--print-interpreter", str(installed)], tmp_path).stdout.strip() == linker
    assert (
        run([patchelf, "--print-rpath", str(installed)], tmp_path)
        .stdout.strip()
        .startswith(libraries + ":")
    )
    run([str(installed)], tmp_path)

    prepared_content = installed.read_bytes()
    prepared_inode = installed.stat().st_ino
    repeated = run(["bash", str(script), str(installed)], tmp_path, extra_env=environment)
    assert repeated.stdout == ""
    assert installed.read_bytes() == prepared_content
    assert installed.stat().st_ino == prepared_inode
    assert cached.read_bytes() == cached_content
