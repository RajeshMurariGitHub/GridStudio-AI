"""
GridStudio AI

Module:
    exceptions.py

Description:
    Defines benchmark-specific exceptions used by the
    GridStudio benchmark framework.

    These exceptions are raised during benchmark dataset
    validation and benchmark network construction.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations


class BenchmarkError(Exception):
    """
    Base class for all benchmark-related exceptions.
    """


class BenchmarkValidationError(BenchmarkError):
    """
    Raised when a benchmark dataset fails structural
    validation.

    Examples
    --------
    - Duplicate bus numbers.
    - Duplicate branch numbers.
    - Branch references an unknown bus.
    - Load references an unknown bus.
    - Generator references an unknown bus.
    """


class BenchmarkBuilderError(BenchmarkError):
    """
    Raised when a benchmark network cannot be constructed
    from a valid dataset.

    This typically indicates an internal builder error
    rather than an invalid benchmark dataset.
    """