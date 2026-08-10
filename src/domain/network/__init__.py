"""
GridStudio AI

Package:
    src.domain.network

Description:
    Public API for the canonical GridStudio electrical network
    subsystem.

    The package separates three primary responsibilities:

        Network
            Owns canonical physical electrical equipment.

        Topology
            Interprets electrical connectivity and topology semantics.

        Graph
            Provides generic dependency-free graph structure and
            algorithms.

    Network-domain exceptions are also exposed here so callers do
    not need to depend on internal module paths.

    This package is solver-independent and contains no pandapower,
    OpenDSS, optimization, forecasting, or time-series implementation.

Author:
    Rajesh Murari

License:
    MIT
"""

# ============================================================================
# Canonical Network
# ============================================================================

from src.domain.network.network import Network


# ============================================================================
# Electrical Topology
# ============================================================================

from src.domain.network.topology import Topology


# ============================================================================
# Generic Graph
# ============================================================================

from src.domain.network.graph import (
    Edge,
    Graph,
)


# ============================================================================
# Network-Domain Exceptions
# ============================================================================

from src.domain.network.exceptions import (
    DisconnectedNetworkError,
    DuplicateElementError,
    ElementNotFoundError,
    InvalidBranchReferenceError,
    InvalidElementReferenceError,
    InvalidElementTypeError,
    InvalidNetworkStructureError,
    IsolatedBusError,
    MeshedNetworkError,
    NetworkElementError,
    NetworkError,
    NetworkIntegrityError,
    NetworkReferenceError,
    NoPathError,
    RadialityError,
    SelfLoopError,
    TopologyError,
)


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    # ------------------------------------------------------------------
    # Core network abstractions
    # ------------------------------------------------------------------
    "Network",
    "Topology",

    # ------------------------------------------------------------------
    # Generic graph abstractions
    # ------------------------------------------------------------------
    "Edge",
    "Graph",

    # ------------------------------------------------------------------
    # Base network exception
    # ------------------------------------------------------------------
    "NetworkError",

    # ------------------------------------------------------------------
    # Element exceptions
    # ------------------------------------------------------------------
    "NetworkElementError",
    "ElementNotFoundError",
    "DuplicateElementError",
    "InvalidElementTypeError",

    # ------------------------------------------------------------------
    # Reference exceptions
    # ------------------------------------------------------------------
    "NetworkReferenceError",
    "InvalidElementReferenceError",
    "InvalidBranchReferenceError",

    # ------------------------------------------------------------------
    # Integrity exceptions
    # ------------------------------------------------------------------
    "NetworkIntegrityError",
    "InvalidNetworkStructureError",
    "SelfLoopError",

    # ------------------------------------------------------------------
    # Topology exceptions
    # ------------------------------------------------------------------
    "TopologyError",
    "DisconnectedNetworkError",
    "IsolatedBusError",
    "NoPathError",
    "MeshedNetworkError",
    "RadialityError",
]