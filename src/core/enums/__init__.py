"""
GridStudio AI

Package:
    core.enums

Description:
    Public enumeration API for GridStudio AI.

    This package provides solver-independent enumerations describing
    electrical networks, equipment classifications, simulation and
    study concepts, operational states, and external data formats.

    Application and domain code should normally import enumerations
    from ``src.core.enums`` rather than from individual enum modules.

Example:
    from src.core.enums import (
        BusType,
        NetworkRepresentation,
        Phase,
        SimulationMode,
        StudyType,
    )

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations


# ============================================================================
# Electrical Network
# ============================================================================

from .electrical import (
    BusType,
    ConnectionType,
    GroundingType,
    NetworkRepresentation,
    Phase,
    PowerDirection,
    VoltageLevel,
)


# ============================================================================
# Electrical Equipment
# ============================================================================

from src.core.enums.equipment import (
    BatteryTechnology,
    EVType,
    GeneratorType,
    LoadModel,
    LoadType,
    ShuntType,
    SolarTechnology,
    SwitchType,
    TransformerType,
    WindTechnology,
)


# ============================================================================
# Simulation and Engineering Studies
# ============================================================================

from .simulation import (
    ConvergenceStatus,
    ResultStatus,
    SimulationMode,
    SimulationStatus,
    StudyType,
)


# ============================================================================
# Operations
# ============================================================================

from .operation import (
    AssetStatus,
    AvailabilityState,
    DispatchState,
    OperatingMode,
    SwitchState,
)


# ============================================================================
# Input / Output
# ============================================================================

from .io import (
    DataEncoding,
    ExportMode,
    FileFormat,
    ImportMode,
    NetworkFormat,
)


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    # ------------------------------------------------------------------------
    # Electrical Network
    # ------------------------------------------------------------------------
    "BusType",
    "ConnectionType",
    "GroundingType",
    "NetworkRepresentation",
    "Phase",
    "PowerDirection",
    "VoltageLevel",

    # ------------------------------------------------------------------------
    # Electrical Equipment
    # ------------------------------------------------------------------------
    "BatteryTechnology",
    "EVType",
    "GeneratorType",
    "LoadModel",
    "LoadType",
    "ShuntType",
    "SolarTechnology",
    "SwitchType",
    "TransformerType",
    "WindTechnology",

    # ------------------------------------------------------------------------
    # Simulation and Engineering Studies
    # ------------------------------------------------------------------------
    "ConvergenceStatus",
    "ResultStatus",
    "SimulationMode",
    "SimulationStatus",
    "StudyType",

    # ------------------------------------------------------------------------
    # Operations
    # ------------------------------------------------------------------------
    "AssetStatus",
    "AvailabilityState",
    "DispatchState",
    "OperatingMode",
    "SwitchState",

    # ------------------------------------------------------------------------
    # Input / Output
    # ------------------------------------------------------------------------
    "DataEncoding",
    "ExportMode",
    "FileFormat",
    "ImportMode",
    "NetworkFormat",
]