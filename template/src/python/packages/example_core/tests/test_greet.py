import pytest
from example_core import greet


def test_greeting_trims_input() -> None:
    assert greet(" Ada ") == "Hello, Ada!"


def test_greeting_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="non-whitespace"):
        greet("  ")
