"""
GridStudio AI

Module:
    builder.py

Description:
    IEEE 33-Bus benchmark builder.

    Provides the IEEE 33-bus benchmark dataset to the
    reusable benchmark builder.

    All network construction is performed by
    BenchmarkBuilder.
    
    Conversion into GridStudio domain objects is performed by 
    BenchmarkBuilder via IEEE33Builder.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from src.network.benchmarks.common.builder import (
    BenchmarkBuilder,
)

from .data import (
    IEEE33_DATASET,
)

from .metadata import (
    IEEE33_METADATA,
)


class IEEE33Builder(BenchmarkBuilder):
    """
    Builder for the IEEE 33-bus benchmark network.
    """

    def __init__(self) -> None:
        """
        Initialize the IEEE 33-bus benchmark builder.
        """

        super().__init__(
            dataset=IEEE33_DATASET,
            metadata=IEEE33_METADATA,
        )

