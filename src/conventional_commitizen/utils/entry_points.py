"""Entry point utilities for loading python package entry points."""

import sys

if sys.version_info >= (3, 10):
    from importlib import metadata
else:
    import importlib_metadata as metadata


def load_entry_point(name: str, group: str) -> object:
    """Load an entry point by name and group.

    Args:
        name: The name of the entry point to load.
        group: The name of the group to which the entry point belongs.

    Returns:
        The loaded entry point object.

    Raises:
        ValueError:
            If the entry point with the specified name and group is not found.
    """
    try:
        (ep,) = metadata.entry_points(name=name, group=group)
        return ep.load()
    except ValueError as e:
        raise ValueError(
            f"Could not find entry point {name} in group {group}"
        ) from e
