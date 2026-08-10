# src/simulation/models/configuration/reference_source.py

"""
GridStudio AI

Module:
    reference_source.py

Description:
    Defines solver-independent reference-source configuration used
    by steady-state power-flow simulations.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from src.domain.base import DomainModel


class ReferenceSource(DomainModel):
    """
    Solver-independent electrical reference source.

    A reference source identifies a network bus whose voltage
    magnitude and phase angle are fixed for a power-flow study.

    This is simulation configuration rather than physical network
    equipment.

    Solver adapters may represent this configuration differently.

    Examples
    --------
    pandapower:
        ext_grid

    OpenDSS:
        Vsource

    Notes
    -----
    Reference-source selection is deliberately separate from
    Generator voltage control.

    A voltage-controlled generator regulates voltage magnitude but
    does not automatically define the global/reference phase angle.
    """

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