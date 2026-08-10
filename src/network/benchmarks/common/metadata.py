"""
GridStudio AI

Module:
    metadata.py

Description:
    Common metadata definitions for benchmark networks.

    Metadata describes a benchmark network but contains no
    topology or electrical reference results.

Author:
    Rajesh Murari

License:
    MIT
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BenchmarkMetadata:
    """
    Metadata describing a benchmark network.
    """

    #
    # Identification
    #

    name: str

    description: str

    version: str

    reference: str

    #
    # Electrical base values
    #

    base_power_mva: float

    base_voltage_kv: float

    base_frequency_hz: float = 50.0

    #
    # Optional information
    #

    country: str | None = None

    organization: str | None = None

    publication_year: int | None = None

    doi: str | None = None

    notes: str = ""