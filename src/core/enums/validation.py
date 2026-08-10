"""
GridStudio AI

Module:
    validation.py

Description:
    Defines solver-independent validation states used by GridStudio
    simulation and result models.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from enum import StrEnum


class ValidationStatus(StrEnum):
    """
    Validation state of a calculated simulation object.
    """

    VALID = "valid"
    WARNING = "warning"
    INVALID = "invalid"


__all__ = [
    "ValidationStatus",
]