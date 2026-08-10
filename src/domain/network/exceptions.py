"""
GridStudio AI

Module:
    exceptions.py

Description:
    Defines exceptions for the canonical GridStudio electrical
    network domain.

    These exceptions describe failures involving:

    * network elements,
    * element references,
    * network integrity,
    * electrical topology.

    Generic graph errors remain standard Python exceptions.

    Solver-specific failures such as power-flow convergence,
    pandapower execution, OpenDSS execution, conversion, optimization,
    forecasting, and time-series simulation do not belong here.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from uuid import UUID


# ============================================================================
# Base Network Exception
# ============================================================================


class NetworkError(Exception):
    """
    Base exception for canonical network-domain failures.

    All GridStudio exceptions that specifically describe invalid
    network-domain operations should derive from this class.

    This allows callers to either catch all network failures:

        except NetworkError:

    or catch a more specific subclass.
    """


# ============================================================================
# Element Errors
# ============================================================================


class NetworkElementError(NetworkError):
    """
    Base exception for failures involving network elements.
    """


class ElementNotFoundError(NetworkElementError):
    """
    Raised when a requested network element does not exist.
    """

    def __init__(
        self,
        element_id: UUID,
    ) -> None:
        self.element_id = element_id

        super().__init__(
            f"Network element with ID "
            f"{element_id} was not found."
        )


class DuplicateElementError(NetworkElementError):
    """
    Raised when an element identifier already exists in the network.
    """

    def __init__(
        self,
        element_id: UUID,
    ) -> None:
        self.element_id = element_id

        super().__init__(
            f"Network element with ID "
            f"{element_id} already exists."
        )


class InvalidElementTypeError(NetworkElementError):
    """
    Raised when an existing network element has an unexpected type.
    """

    def __init__(
        self,
        *,
        element_id: UUID,
        expected_type: type,
        actual_type: type,
    ) -> None:
        self.element_id = element_id
        self.expected_type = expected_type
        self.actual_type = actual_type

        super().__init__(
            f"Network element {element_id} has type "
            f"{actual_type.__name__}; expected "
            f"{expected_type.__name__}."
        )


# ============================================================================
# Reference Errors
# ============================================================================


class NetworkReferenceError(NetworkError):
    """
    Base exception for invalid references between network elements.

    Examples include:

    * a line referencing a nonexistent bus,
    * a transformer referencing a nonexistent bus,
    * a switch referencing a nonexistent bus,
    * a load referencing a nonexistent bus,
    * a generator referencing a nonexistent bus.
    """


class InvalidElementReferenceError(NetworkReferenceError):
    """
    Raised when an element references another element that cannot be
    resolved.
    """

    def __init__(
        self,
        *,
        element_id: UUID,
        referenced_id: UUID,
        reference_name: str | None = None,
    ) -> None:
        self.element_id = element_id
        self.referenced_id = referenced_id
        self.reference_name = reference_name

        if reference_name is None:
            message = (
                f"Network element {element_id} references "
                f"unknown element {referenced_id}."
            )
        else:
            message = (
                f"Network element {element_id} contains invalid "
                f"{reference_name!r} reference "
                f"{referenced_id}."
            )

        super().__init__(
            message
        )


class InvalidBranchReferenceError(
    InvalidElementReferenceError
):
    """
    Raised when a branch references an invalid terminal node.

    This exception applies to branch-family equipment such as:

    * lines,
    * transformers,
    * switches,
    * future branch-like equipment.
    """

    def __init__(
        self,
        *,
        branch_id: UUID,
        node_id: UUID,
        terminal: str | None = None,
    ) -> None:
        self.branch_id = branch_id
        self.node_id = node_id
        self.terminal = terminal

        if terminal is None:
            reference_name = (
                "terminal node"
            )
        else:
            reference_name = (
                f"{terminal}_node_id"
            )

        super().__init__(
            element_id=branch_id,
            referenced_id=node_id,
            reference_name=reference_name,
        )


# ============================================================================
# Integrity Errors
# ============================================================================


class NetworkIntegrityError(NetworkError):
    """
    Base exception for network structural-integrity violations.

    Integrity failures describe a network whose elements may exist
    individually but whose combined structure violates an electrical
    network invariant.
    """


class InvalidNetworkStructureError(
    NetworkIntegrityError
):
    """
    Raised when network structure violates a required invariant.

    More specific structural exceptions should derive from this class
    where possible.
    """


class SelfLoopError(
    InvalidNetworkStructureError
):
    """
    Raised when a branch connects a node to itself.

    Notes
    -----
    The generic Graph abstraction intentionally permits self-loops.

    Whether a self-loop is valid is an electrical-domain integrity
    decision and is therefore represented by this network exception.
    """

    def __init__(
        self,
        *,
        branch_id: UUID,
        node_id: UUID,
    ) -> None:
        self.branch_id = branch_id
        self.node_id = node_id

        super().__init__(
            f"Branch {branch_id} forms an invalid "
            f"self-loop at node {node_id}."
        )


# ============================================================================
# Topology Errors
# ============================================================================


class TopologyError(NetworkError):
    """
    Base exception for electrical-topology failures.

    These exceptions describe electrical interpretation of a valid
    physical network rather than generic graph operations.
    """


class DisconnectedNetworkError(TopologyError):
    """
    Raised when an operation requires one connected electrical
    network but multiple electrical components exist.
    """

    def __init__(
        self,
        component_count: int | None = None,
    ) -> None:
        self.component_count = component_count

        if component_count is None:
            message = (
                "The electrical network is disconnected."
            )
        else:
            message = (
                "The electrical network is disconnected "
                f"and contains {component_count} "
                "connected components."
            )

        super().__init__(
            message
        )


class IsolatedBusError(TopologyError):
    """
    Raised when an operation requires an electrically connected bus
    but the requested bus has zero electrical degree.
    """

    def __init__(
        self,
        bus_id: UUID,
    ) -> None:
        self.bus_id = bus_id

        super().__init__(
            f"Bus {bus_id} is electrically isolated."
        )


class NoPathError(TopologyError):
    """
    Raised when no electrical path exists between two buses.
    """

    def __init__(
        self,
        source_bus_id: UUID,
        target_bus_id: UUID,
    ) -> None:
        self.source_bus_id = (
            source_bus_id
        )
        self.target_bus_id = (
            target_bus_id
        )

        super().__init__(
            f"No electrical path exists between "
            f"bus {source_bus_id} and "
            f"bus {target_bus_id}."
        )


class MeshedNetworkError(TopologyError):
    """
    Raised when an operation requires radial topology but the
    electrical network contains one or more cycles.
    """

    def __init__(
        self,
        message: str | None = None,
    ) -> None:
        super().__init__(
            message
            or (
                "The electrical network is meshed; "
                "a radial topology is required."
            )
        )


class RadialityError(TopologyError):
    """
    Raised when a required radiality condition is not satisfied.

    This exception is broader than MeshedNetworkError.

    For example, a network may fail a strict radial-network
    requirement because it is disconnected even though every
    individual island is acyclic.
    """

    def __init__(
        self,
        message: str | None = None,
    ) -> None:
        super().__init__(
            message
            or (
                "The electrical network does not satisfy "
                "the required radiality condition."
            )
        )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    # Base
    "NetworkError",

    # Elements
    "NetworkElementError",
    "ElementNotFoundError",
    "DuplicateElementError",
    "InvalidElementTypeError",

    # References
    "NetworkReferenceError",
    "InvalidElementReferenceError",
    "InvalidBranchReferenceError",

    # Integrity
    "NetworkIntegrityError",
    "InvalidNetworkStructureError",
    "SelfLoopError",

    # Topology
    "TopologyError",
    "DisconnectedNetworkError",
    "IsolatedBusError",
    "NoPathError",
    "MeshedNetworkError",
    "RadialityError",
]