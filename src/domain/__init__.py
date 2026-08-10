"""
GridStudio AI

Package:
    src.domain

Description:
    Public interface for the canonical GridStudio electrical domain.

    The domain package contains solver-independent representations of
    electrical assets, equipment, flexible resources, electrical
    properties, and network structure.

    Major architectural areas:

        Core domain models
            Base domain abstractions and electrical equipment.

        Electrical models
            Phase, connection, and electrical parameter models.

        Network models
            Canonical Network, electrical Topology, and generic Graph.

    The domain layer must remain independent of simulation engines,
    optimization algorithms, forecasting models, visualization
    frameworks, and external solver implementations.

License:
    MIT
"""

from __future__ import annotations


# ============================================================================
# Base Domain Hierarchy
# ============================================================================

from .base import DomainModel
from .asset import Asset
from .element import Element
from .node import Node
from .branch import Branch
from .injection import Injection


# ============================================================================
# Network Equipment
# ============================================================================

from .bus import Bus
from .line import Line
from .transformer import Transformer
from .switch import Switch
from .shunt import Shunt


# ============================================================================
# Loads and Generation
# ============================================================================

from .load import Load
from .generator import Generator


# ============================================================================
# Distributed Energy Resources and Flexible Resources
# ============================================================================

from .solar import Solar
from .wind import Wind
from .battery import Battery
from .ev import EV


# ============================================================================
# Electrical Models
# ============================================================================

from src.core.enums.electrical import (
    Phase,
    ConnectionType,
)
from src.domain.electrical.line_parameters import (
    LineParameters,
)


# ============================================================================
# Network Architecture
# ============================================================================

from .network import (
    Edge,
    Graph,
    Network,
    Topology,
)

from src.core.enums.equipment import (
    LoadType, 
    LoadModel,
)

# ============================================================================
# Public API
# ============================================================================

__all__ = [
    # ------------------------------------------------------------------
    # Base hierarchy
    # ------------------------------------------------------------------
    "DomainModel",
    "Asset",
    "Element",
    "Node",
    "Branch",
    "Injection",

    # ------------------------------------------------------------------
    # Network equipment
    # ------------------------------------------------------------------
    "Bus",
    "Line",
    "Transformer",
    "Switch",
    "Shunt",

    # ------------------------------------------------------------------
    # Loads and generation
    # ------------------------------------------------------------------
    "Load",
    "Generator",
    "LoadModel",
    "LoadType",

    # ------------------------------------------------------------------
    # DER and flexible resources
    # ------------------------------------------------------------------
    "Solar",
    "Wind",
    "Battery",
    "EV",

    # ------------------------------------------------------------------
    # Electrical models
    # ------------------------------------------------------------------
    "Phase",
    "ConnectionType",
    "LineParameters",

    # ------------------------------------------------------------------
    # Network architecture
    # ------------------------------------------------------------------
    "Edge",
    "Graph",
    "Network",
    "Topology",
]