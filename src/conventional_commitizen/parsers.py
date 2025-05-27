"""Parser module for processing commit messages."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from conventional_commitizen.utils.entry_points import load_entry_point

if TYPE_CHECKING:
    from conventional_commitizen.commit import Commit


class BaseParser(ABC):
    """Abstract base class for commit message parsers.

    This class defines the interface for commit message parsers. It requires
    subclasses to implement the `setup` and `parse` methods. The `setup` method
    is called once when the parser is initialized to preprocess configuration
    options, and the `parse` method is called to parse a commit message and
    return structured data.

    Attributes:
        config: A dictionary containing configuration options for the parser.
    """

    def __init__(self, config: dict) -> None:
        """Initialize the parser with a configuration.

        Args:
            config:
                A dictionary containing configuration options for the parser.
        """
        self.config = config
        for option, value in self.config["parser"].items():
            setattr(self, option, value)
        self.setup()

    @abstractmethod
    def setup(self) -> None:
        """Setup the parser.

        This function is run once when the parser is initialized.

        Assert parser configuration options have been collected from
        configuration file.

        Preprocess parser configuration options for use in the parser function.
        """
        pass

    @abstractmethod
    def parse(self, commit: Commit) -> dict:
        """Parse the commit message and return a dict with structured data.

        Args:
            commit: The commit object containing the raw commit message.

        Returns:
            A dictionary with structured data parsed from the commit message.
        """
        pass


class Parser:
    """Parser factory for creating parser instances.

    This class is responsible for loading the appropriate parser based on the
    configuration provided. It uses entry points to dynamically load the parser
    class specified in the configuration.
    """

    def __new__(cls, config: dict) -> Parser:
        """Create a new instance of the parser class.

        Args:
            config: The conventional-commitizen configuration dictionary.

        Returns:
            An instance of the parser class.
        """
        parser_name = config.get("parser", {}).get("name", "generic")
        parser_class = load_entry_point(
            parser_name, "conventional-commitizen.parsers"
        )
        return parser_class(config)


class GenericParser(BaseParser):
    """A generic parser.

    The parser breaks down a commit into elements as defined by the config.
    There are two locations where elements are defined: the header and the
    body/footer.

    The header is the first line of the commit message. Elements are extracted
    from the header using named regular expression groups.

    The remaining lines of the commit message contain the body and footers.
    The body is any part of the commit message that is not a footer and a
    footer is any section of text that begins with a predefined marker. The
    parser collects the footer start markers as regular expressions from the
    configuration file. Then the parser iterates through the lines of the
    commit message, checking each line against the footer patterns. Until a
    footer pattern is matched, the line is added to the body element. Once a
    footer pattern is matched, the parser switches to that footer element and
    continues to add lines to that footer until another footer pattern is
    matched or the end of the commit message is reached.

    The regular expression patterns for the header and footers are defined in
    the parser configuration element in the conventional-changelog config file.

    Attributes:
        header:
            Regular expression pattern for the commit header. The regular
            expression should contain named groups corresponding to the
            elements to be extracted from the header.
        footers:
            Dictionary of regular expression patterns for commit footers.
            The regular expression is used to identify the first line of
            the footer. After the footers are assembled the regular
            expressions are applied again to the footers and any
            named groups in the expressions are saved to the elements
            dictionary under the group name.
    """

    def setup(self) -> None:
        """Setup the parser.

        This function is run once when the parser is initialized.

        Assert parser configuration options have been collected from
        configuration file.

        Preprocess parser configuration options for use in the parser function.
        """
        assert getattr(self, "header", None) is not None, (
            "Header pattern must be defined"
        )
        assert isinstance(getattr(self, "footers", None), dict), (
            "Footer patterns must be defined as a dictionary."
        )
        self.header = re.compile(self.header, re.MULTILINE)
        self.footers = {
            name: re.compile(pattern, re.MULTILINE)
            for name, pattern in self.footers.items()
        }

    def parse(self, commit: Commit) -> dict:
        """Parse the commit message and return a dict with structured data.

        Args:
            commit: The commit object containing the raw commit message.

        Returns:
            A dictionary with structured data parsed from the commit message.
        """
        elements = {}
        lines = commit.raw.splitlines(keepends=True)
        elements["header"] = lines[0].strip()
        match = self.header.match(elements["header"])
        groups = match.groupdict() if match else {}
        groups = {k: v for k, v in groups.items() if v is not None}
        elements.update(groups)
        element = "body"
        for line in lines[1:]:
            for name, pattern in self.footers.items():
                if pattern.match(line):
                    element = name
                    break
            elements[element] = elements.get(element, "") + line
        for element, value in elements.items():
            elements[element] = value.strip()
        for name, pattern in self.footers.items():
            if name not in elements:
                continue
            else:
                match = pattern.match(elements[name])
                groups = match.groupdict() if match else {}
                groups = {k: v for k, v in groups.items() if v is not None}
                elements.update(groups)
        return {k: v for k, v in elements.items() if v}
