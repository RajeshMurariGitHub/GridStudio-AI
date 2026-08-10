"""
GridStudio AI

Package:
    domain.electrical

Description:
    Public API for solver-independent electrical value objects used
    throughout the GridStudio AI domain.

    This package provides common representations for electrical
    phases and connection configurations shared by buses, lines,
    transformers, loads, generators, DERs, and other network
    equipment.

    Domain code should normally import these objects from
    ``src.domain.electrical`` rather than from individual modules.

Example:
    from src.domain.electrical import (
        DELTA,
        GROUNDED_WYE,
        PHASE_ABC,
        ElectricalConnection,
        PhaseSet,
    )

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations


# ============================================================================
# Electrical Phases
# ============================================================================

from .phases import (
    PHASE_A,
    PHASE_AB,
    PHASE_ABC,
    PHASE_ABCN,
    PHASE_B,
    PHASE_BC,
    PHASE_C,
    PHASE_CA,
    PhaseSet,
)


# ============================================================================
# Electrical Connections
# ============================================================================

from .connection import (
    DELTA,
    GROUNDED_WYE,
    WYE,
    ElectricalConnection,
)


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    # ------------------------------------------------------------------------
    # Electrical Phases
    # ------------------------------------------------------------------------
    "PHASE_A",
    "PHASE_AB",
    "PHASE_ABC",
    "PHASE_ABCN",
    "PHASE_B",
    "PHASE_BC",
    "PHASE_C",
    "PHASE_CA",
    "PhaseSet",

    # ------------------------------------------------------------------------
    # Electrical Connections
    # ------------------------------------------------------------------------
    "DELTA",
    "GROUNDED_WYE",
    "WYE",
    "ElectricalConnection",
]