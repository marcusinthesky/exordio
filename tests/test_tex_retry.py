"""TeX setup retries transient server failures without hiding other errors."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "template/infra/nix/retry-tex-setup.sh"


@pytest.mark.parametrize(
    ("message", "failures", "expected", "attempts"),
    [
        ("unexpected HTTP response code 429", 2, 0, 3),
        ("HTTP 503 Service Unavailable", 9, 7, 4),
        ("Undefined control sequence", 9, 7, 1),
    ],
)
def test_retry(tmp_path: Path, message: str, failures: int, expected: int, attempts: int) -> None:
    command = tmp_path / "command"
    command.write_text(
        "#!/usr/bin/env bash\n"
        'n=$(cat "$COUNT" 2>/dev/null || echo 0)\n'
        'n=$((n + 1)); echo "$n" > "$COUNT"\n'
        f'if (( n <= {failures} )); then echo "{message}" >&2; exit 7; fi\n'
    )
    command.chmod(0o755)
    sleeper = tmp_path / "sleep"
    sleeper.write_text("#!/usr/bin/env bash\nexit 0\n")
    sleeper.chmod(0o755)
    count = tmp_path / "count"
    env = {**os.environ, "PATH": f"{tmp_path}:{os.environ['PATH']}", "COUNT": str(count)}
    result = subprocess.run(["bash", str(SCRIPT), str(command)], env=env, capture_output=True)
    assert result.returncode == expected
    assert int(count.read_text()) == attempts
    assert message.encode() in result.stdout
