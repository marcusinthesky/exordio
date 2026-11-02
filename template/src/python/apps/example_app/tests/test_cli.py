import subprocess
import sys


def test_module_entry_point() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "example_app", "Grace"],
        check=True,
        text=True,
        capture_output=True,
    )
    assert result.stdout == "Hello, Grace!\n"
