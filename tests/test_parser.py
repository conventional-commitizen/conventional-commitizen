"""PyTest module for testing the parser."""

import pytest

from conventional_commitizen.commit import Commit
from conventional_commitizen.parsers import Parser


@pytest.mark.parametrize(
    "raw_message, config, skeleton",
    [
        (
            "fix: add new feature",
            {
                "parser": {
                    "name": "generic",
                    "header": (
                        r"^(?P<type>[a-z]+)"
                        r"(?:\((?P<scope>\S+)\))?"
                        r"(?P<breaking_change_header>!)?"
                        r": (?P<subject>.+)$"
                    ),
                    "footers": {
                        "breaking_change_footer": r"^BREAKING CHANGE:.+$",
                    },
                }
            },
            {
                "header": "fix: add new feature",
                "type": "fix",
                "subject": "add new feature",
            },
        ),
        (
            (
                "feat(main)!: add new feature\n"
                "\n"
                "This is the body of the commit message.\n"
                "\n"
                "BREAKING CHANGE: This is a breaking change.\n"
            ),
            {
                "parser": {
                    "name": "generic",
                    "header": (
                        r"^(?P<type>[a-z]+)"
                        r"(?:\((?P<scope>\S+)\))?"
                        r"(?P<breaking_change_header>!)?"
                        r": (?P<subject>.+)$"
                    ),
                    "footers": {
                        "breaking_change_footer": r"^BREAKING CHANGE:.+$",
                    },
                }
            },
            {
                "header": "feat(main)!: add new feature",
                "type": "feat",
                "subject": "add new feature",
                "scope": "main",
                "body": "This is the body of the commit message.",
                "breaking_change_header": "!",
                "breaking_change_footer": "BREAKING CHANGE: "
                "This is a breaking change.",
            },
        ),
        (
            (
                "\n"
                "feat(main)!: add new feature\n"
                "\n"
                "BREAKING CHANGE: This is a breaking change.\n\n"
            ),
            {
                "parser": {
                    "name": "generic",
                    "header": (
                        r"^(?P<type>[a-z]+)"
                        r"(?:\((?P<scope>\S+)\))?"
                        r"(?P<breaking_change_header>!)?"
                        r": (?P<subject>.+)$"
                    ),
                    "footers": {
                        "breaking_change_footer": r"^BREAKING CHANGE:.+$",
                    },
                }
            },
            {
                "header": "feat(main)!: add new feature",
                "type": "feat",
                "subject": "add new feature",
                "scope": "main",
                "breaking_change_header": "!",
                "breaking_change_footer": (
                    "BREAKING CHANGE: This is a breaking change."
                ),
            },
        ),
        (
            (
                "\n"
                "feat(main)!: add new feature\n"
                "\n"
                "BREAKING CHANGE: This is a breaking change.\n\n"
            ),
            {
                "parser": {
                    "name": "generic",
                    "header": (
                        r"^(?P<type>[a-z]+)"
                        r"(?:\((?P<scope>\S+)\))?"
                        r"(?P<breaking_change_header>!)?"
                        r": (?P<subject>.+)$"
                    ),
                    "footers": {
                        "breaking_change_footer": (
                            r"^BREAKING CHANGE: "
                            r"(?P<breaking_change_description>.+)$"
                        ),
                    },
                }
            },
            {
                "header": "feat(main)!: add new feature",
                "type": "feat",
                "subject": "add new feature",
                "scope": "main",
                "breaking_change_header": "!",
                "breaking_change_footer": (
                    "BREAKING CHANGE: This is a breaking change."
                ),
                "breaking_change_description": ("This is a breaking change."),
            },
        ),
        (
            (
                "\n"
                "feat(main)!: add new feature\n"
                "\n"
                "BREAKING CHANGE: This is a breaking change.\n\n"
            ),
            {
                "parser": {
                    "name": "generic",
                    "header": (
                        r"^(?P<type>[a-z]+)"
                        r"(?:\((?P<scope>\S+)\))?"
                        r"(?P<breaking_change_header>!)?"
                        r": (?P<subject>.+)$"
                    ),
                    "footers": {},
                }
            },
            {
                "header": "feat(main)!: add new feature",
                "type": "feat",
                "subject": "add new feature",
                "scope": "main",
                "breaking_change_header": "!",
                "body": "BREAKING CHANGE: This is a breaking change.",
            },
        ),
    ],
)
def test_generic_parser(raw_message: str, config: dict, skeleton: dict) -> None:
    """Test the GenericParser class.

    Args:
        raw_message: The raw commit message to be parsed.
        config: The configuration dictionary for the parser.
        skeleton: The expected parsed output as a dictionary.
    """
    parser = Parser(config)
    commit = Commit(raw_message)
    parsed_commit = parser.parse(commit)
    assert parsed_commit == skeleton
