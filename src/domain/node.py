"""
GridStudio AI

Module:
    node.py

Description:
    Defines the foundational electrical node model used throughout
    the GridStudio AI domain.

    A Node represents an electrical connection point in the network
    topology. Branches connect nodes, while injections and other
    electrical equipment may attach to nodes.

    The model is solver-independent and supports both balanced and
    unbalanced electrical networks.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from pydantic import Field

from src.domain.element import Element


# ============================================================================
# Node
# ============================================================================


class Node(Element):
    """
    Base class for electrical network connection points.

    A Node represents a topological point at which electrical
    equipment may connect.

    Nodes form the vertices of the GridStudio network graph.

    Examples
    --------
    Specialized node types may represent:

    * electrical buses,
    * internal equipment terminals,
    * future phase-specific connectivity points.

    Notes
    -----
    Node intentionally contains only topology-independent
    connection-point information.

    Power-flow-specific properties such as:

    * bus type,
    * nominal voltage,
    * voltage limits,
    * voltage setpoint,
    * slack/reference behavior,

    belong to the Bus model rather than this generic base class.

    Similarly, geographic coordinates are optional descriptive
    information and do not affect electrical connectivity.
    """

    # ------------------------------------------------------------------
    # Geographic / Diagram Position
    # ------------------------------------------------------------------

    x: float | None = Field(
        default=None,
        description=(
            "Optional horizontal coordinate used for geographic "
            "or schematic visualization."
        ),
    )

    y: float | None = Field(
        default=None,
        description=(
            "Optional vertical coordinate used for geographic "
            "or schematic visualization."
        ),
    )

    # ------------------------------------------------------------------
    # Convenience Properties
    # ------------------------------------------------------------------

    @property
    def has_coordinates(self) -> bool:
        """
        Return whether both node coordinates are available.
        """

        return (
            self.x is not None
            and self.y is not None
        )

    @property
    def coordinates(
        self,
    ) -> tuple[float, float] | None:
        """
        Return node coordinates when available.

        Returns
        -------
        tuple[float, float] | None
            ``(x, y)`` when both coordinates are defined,
            otherwise ``None``.
        """

        if not self.has_coordinates:
            return None

        return (
            self.x,
            self.y,
        )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Node",
]