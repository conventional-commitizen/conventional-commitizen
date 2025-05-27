"""Module for tracking commit messages and their metadata."""

from __future__ import annotations


class Commit:
    """Class representing a commit message.

    Attributes:
        raw: The raw commit message as a string.
    """

    def __init__(self, raw_message: str) -> None:
        """Initialize the Commit object with a raw commit message.

        Args:
            raw_message: The raw commit message as a string.
        """
        self.raw = raw_message.strip()
