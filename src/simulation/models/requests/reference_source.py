"""
GridStudio AI

Module:
    reference_source.py

Description:
    Defines solver-independent electrical reference-source
    configuration for GridStudio power-flow studies.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class ReferenceSource(BaseModel):
    """
    Solver-independent electrical reference source.

    A reference source identifies a network bus whose voltage
    magnitude and phase angle establish an electrical reference for
    a power-flow study.

    This object is simulation configuration, not physical network
    equipment.

    Solver adapters translate it into their native representation,
    for example:

        pandapower -> ext_grid
        OpenDSS    -> Vsource

    Notes
    -----
    Reference-source designation is intentionally separate from
    Generator voltage control.

    A voltage-controlled Generator regulates its terminal voltage
    magnitude but does not automatically establish the global
    voltage-angle reference for the study.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    bus_id: UUID = Field(
        ...,
        description=(
            "GridStudio bus used as the electrical reference."
        ),
    )

    voltage_magnitude_pu: float = Field(
        default=1.0,
        gt=0.0,
        description=(
            "Reference voltage magnitude in per-unit."
        ),
    )

    voltage_angle_deg: float = Field(
        default=0.0,
        description=(
            "Reference voltage phase angle in degrees."
        ),
    )


__all__ = [
    "ReferenceSource",
]