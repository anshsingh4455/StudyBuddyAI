"""
utils/formatters.py

Helper functions for formatting text and Markdown in StudyBuddy AI.
Currently minimal, but centralizing here makes it easy to extend later.
"""

from __future__ import annotations


def ensure_markdown_headings(text: str) -> str:
    """
    Best-effort post-processing to ensure the response has at least one heading.

    If the text does not appear to contain a Markdown heading, prepend a generic one.
    """
    if not text:
        return text
    stripped = text.lstrip()
    if stripped.startswith("#"):
        return text
    return "### Answer\n\n" + text

