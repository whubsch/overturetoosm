"""Useful functions for the project."""

from .objects import Sources


def source_statement(source: list[Sources]) -> str:
    """Return a source statement from a list of sources."""
    return ", ".join(i.dataset.strip(", ") for i in source) + " via overturetoosm"
