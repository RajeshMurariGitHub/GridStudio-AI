"""
Pandapower dependency loading for the GridStudio Pandapower engine.
"""

from __future__ import annotations

from typing import Any


def import_pandapower() -> Any:  
    """
    Import pandapower lazily.

    Returns
    -------
    module
        Imported pandapower module.

    Raises
    ------
    ImportError
        If pandapower is not installed.
    """

    try:
        import pandapower as pp
    except ImportError as exc:
        raise ImportError(
            "The pandapower simulation engine requires the "
            "'pandapower' package to be installed."
        ) from exc

    return pp


__all__ = [
    "import_pandapower",
]