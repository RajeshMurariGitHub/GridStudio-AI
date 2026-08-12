"""
GridStudio AI

Module:
    metadata.py

Description:
    Metadata for the IEEE 33-Bus benchmark network.

    This module defines immutable descriptive metadata for
    the IEEE 33-bus benchmark. The metadata is independent
    of the benchmark dataset and is consumed by the generic
    BenchmarkBuilder.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from src.network.benchmarks.common.types import (
    BenchmarkMetadata,
)

from src.network.benchmarks.common.constants import (
    DEFAULT_BASE_POWER_MVA,
)

IEEE33_METADATA = BenchmarkMetadata(
    name="IEEE 33-Bus Distribution Test Feeder",

    description=(
        "IEEE 33-bus radial distribution system benchmark."
    ),

    reference=(
        "Baran, M. E., and Wu, F. F. "
        "'Network Reconfiguration in Distribution Systems "
        "for Loss Reduction and Load Balancing', "
        "IEEE Transactions on Power Delivery, 1989."
    ),

    version="Baran-Wu Original",

    base_power_mva=DEFAULT_BASE_POWER_MVA,

    base_voltage_kv=12.66,

    base_frequency_hz=50.0,
)


__all__ = [
    "IEEE33_METADATA",
]