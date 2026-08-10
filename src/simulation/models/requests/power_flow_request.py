"""
GridStudio AI

Module:
    power_flow_request.py

Description:
    Defines the solver-independent request contract for steady-state
    GridStudio power-flow studies.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from src.domain.network import Network
from src.simulation.models.requests.reference_source import (
    ReferenceSource,
)


class PowerFlowRequest(BaseModel):
    """
    Solver-independent steady-state power-flow request.

    The request combines a physical GridStudio network with
    study-specific electrical reference configuration.

    The physical Network remains independent of solver concepts such
    as pandapower ext_grid or OpenDSS Vsource.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    network: Network = Field(
        ...,
        description=(
            "GridStudio network to solve."
        ),
    )

    reference_sources: tuple[
        ReferenceSource,
        ...,
    ] = Field(
        ...,
        min_length=1,
        description=(
            "Electrical reference sources for the power-flow study."
        ),
    )


__all__ = [
    "PowerFlowRequest",
]