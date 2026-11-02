"""Runnable consumer of the example library."""

import argparse

from example_core import greet


def main() -> None:
    parser = argparse.ArgumentParser(description="Print a greeting")
    parser.add_argument("name", nargs="?", default="world")
    args = parser.parse_args()
    print(greet(args.name))
