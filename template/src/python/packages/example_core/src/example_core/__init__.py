"""A small typed library used by the example application."""


def greet(name: str) -> str:
    """Return a greeting after rejecting an empty display name."""
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("name must contain a non-whitespace character")
    return f"Hello, {cleaned}!"
