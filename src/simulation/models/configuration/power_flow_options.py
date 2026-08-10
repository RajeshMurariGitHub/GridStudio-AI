# src/simulation/models/configuration/power_flow_options.py

"""
GridStudio AI

Module:
    power_flow_options.py

Description:
    Defines solver-independent power-flow study configuration.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from pydantic import Field

from src.domain.base import DomainModel
from src.simulation.models.configuration.reference_source import (
    ReferenceSource,
)


class PowerFlowOptions(DomainModel):
    """
    Solver-independent power-flow configuration.

    The physical Network remains unchanged between studies while
    reference-source selection and other study-specific settings
    may vary.
    """

    reference_sources: tuple[
        ReferenceSource,
        ...,
    ] = Field(
        default_factory=tuple,
        description=(
            "Electrical reference sources used by the power-flow "
            "study."
        ),
    )