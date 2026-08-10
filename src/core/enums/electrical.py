"""
GridStudio AI

Module:
    electrical.py

Description:
    Core enumerations describing solver-independent electrical
    network concepts used throughout GridStudio AI.

    These enumerations define the common electrical vocabulary
    shared by domain models, simulation engines, time-series
    studies, optimization workflows, and future digital-twin
    applications.

    Solver-specific concepts must not be introduced into this
    module.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from enum import StrEnum


# ============================================================================
# Network Representation
# ============================================================================


class NetworkRepresentation(StrEnum):
    """
    Electrical representation used by a network model.

    BALANCED
        Positive-sequence or equivalent balanced representation.

    UNBALANCED
        Explicit multiphase representation where individual
        phase quantities may differ.

    Notes
    -----
    This enumeration describes the electrical representation of
    the network, not the simulation engine used to solve it.

    For example, a balanced network may be solved by pandapower,
    while an unbalanced network may be solved by OpenDSS.
    """

    BALANCED = "balanced"
    UNBALANCED = "unbalanced"


# ============================================================================
# Electrical Phases
# ============================================================================


class Phase(StrEnum):
    """
    Individual electrical conductor phase.

    N represents the neutral conductor.

    Notes
    -----
    Phase membership for an electrical asset should normally be
    represented as a collection of Phase values rather than by
    solver-specific strings such as ``"1.2.3"`` or ``"ABC"``.
    """

    A = "a"
    B = "b"
    C = "c"
    N = "n"


# ============================================================================
# Electrical Connections
# ============================================================================


class ConnectionType(StrEnum):
    """
    Electrical connection configuration.

    WYE
        Star-connected electrical equipment.

    DELTA
        Delta-connected electrical equipment.

    Notes
    -----
    Grounding is intentionally not encoded into ConnectionType.
    Grounding and winding connection are separate electrical
    properties and may evolve independently in the domain model.
    """

    WYE = "wye"
    DELTA = "delta"


# ============================================================================
# Grounding
# ============================================================================


class GroundingType(StrEnum):
    """
    Electrical grounding configuration.

    NONE
        No explicit grounding configuration is specified.

    SOLID
        Direct or effectively solid grounding.

    RESISTANCE
        Grounding through resistance.

    REACTANCE
        Grounding through reactance.

    RESONANT
        Resonant grounding, such as Petersen-coil grounding.

    Notes
    -----
    This enumeration represents the grounding method. Detailed
    grounding impedances belong in equipment/domain models rather
    than in the enumeration.
    """

    NONE = "none"
    SOLID = "solid"
    RESISTANCE = "resistance"
    REACTANCE = "reactance"
    RESONANT = "resonant"


# ============================================================================
# Bus Classification
# ============================================================================


class BusType(StrEnum):
    """
    Electrical bus classification used by power-flow studies.

    PQ
        Active and reactive power are specified.

    PV
        Active power and voltage magnitude are specified.

    SLACK
        Reference bus that establishes the voltage angle reference
        and balances the network power mismatch.

    Notes
    -----
    BusType is retained because it is useful for balanced
    power-flow studies and benchmark networks.

    It does not determine whether a network is balanced or
    unbalanced.
    """

    PQ = "pq"
    PV = "pv"
    SLACK = "slack"


# ============================================================================
# Voltage Classification
# ============================================================================


class VoltageLevel(StrEnum):
    """
    Broad nominal-voltage classification.

    Notes
    -----
    Exact voltage thresholds vary between utilities, standards,
    countries, and applications. GridStudio AI therefore treats
    this enumeration as a semantic classification rather than
    deriving it automatically from fixed voltage thresholds.

    The exact nominal voltage remains stored on the electrical
    asset.
    """

    LV = "lv"
    MV = "mv"
    HV = "hv"
    EHV = "ehv"
    UHV = "uhv"


# ============================================================================
# Power Direction
# ============================================================================


class PowerDirection(StrEnum):
    """
    Direction of active or reactive power exchange.

    IMPORT
        Power is being absorbed from the network.

    EXPORT
        Power is being supplied to the network.

    BIDIRECTIONAL
        Equipment is capable of both importing and exporting power.

    Notes
    -----
    This describes equipment capability or operating semantics.
    Numerical sign conventions remain the responsibility of the
    corresponding domain or simulation contract.
    """

    IMPORT = "import"
    EXPORT = "export"
    BIDIRECTIONAL = "bidirectional"


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "BusType",
    "ConnectionType",
    "GroundingType",
    "NetworkRepresentation",
    "Phase",
    "PowerDirection",
    "VoltageLevel",
]