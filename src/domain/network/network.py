"""
GridStudio AI

Module:
    network.py

Description:
    Defines the canonical solver-independent electrical Network model
    used throughout GridStudio AI.

    Network is the authoritative owner of physical electrical elements.
    All typed collections are derived from one element registry.

    Connectivity interpretation and graph algorithms belong to
    Topology and Graph respectively.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import TypeVar
from uuid import UUID

from pydantic import Field, model_validator

from src.domain.base import DomainModel
from src.domain.element import Element

from src.domain.bus import Bus

from src.domain.branch import Branch
from src.domain.line import Line
from src.domain.transformer import Transformer
from src.domain.switch import Switch

from src.domain.injection import Injection
from src.domain.load import Load
from src.domain.generator import Generator
from src.domain.shunt import Shunt

from src.domain.solar import Solar
from src.domain.wind import Wind
from src.domain.battery import Battery
from src.domain.ev import EV

from src.domain.network.exceptions import (
    DuplicateElementError,
    ElementNotFoundError,
    InvalidBranchReferenceError,
    InvalidElementReferenceError,
    InvalidElementTypeError,
)


# ============================================================================
# Type Variables
# ============================================================================


ElementT = TypeVar(
    "ElementT",
    bound=Element,
)


# ============================================================================
# Network
# ============================================================================


class Network(DomainModel):
    """
    Canonical GridStudio electrical network.

    Network is the authoritative owner of physical electrical
    elements.

    A single registry is maintained:

        elements[element_id] -> Element

    Typed views such as buses, lines, transformers, loads,
    generators, batteries, and EVs are derived from this registry.

    Responsibilities
    ----------------
    Network is responsible for:

    * element ownership,
    * element uniqueness,
    * element lookup,
    * typed element access,
    * add/remove operations,
    * basic reference integrity.

    Network is not responsible for:

    * electrical topology interpretation,
    * graph traversal,
    * island detection,
    * radiality analysis,
    * power-flow execution,
    * solver conversion,
    * optimization,
    * forecasting,
    * time-series simulation.

    Those responsibilities belong to higher-level GridStudio
    services.
    """

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    name: str = Field(
        ...,
        min_length=1,
        description="Human-readable network name.",
    )

    description: str | None = Field(
        default=None,
        description="Optional network description.",
    )

    base_frequency_hz: float = Field(
        default=50.0,
        gt=0.0,
        description="Nominal network frequency in Hz.",
    )

    # ------------------------------------------------------------------
    # Authoritative Element Registry
    # ------------------------------------------------------------------

    elements: dict[UUID, Element] = Field(
        default_factory=dict,
        description=(
            "Authoritative registry of electrical elements indexed "
            "by element identifier."
        ),
    )

    # ------------------------------------------------------------------
    # Pydantic Validation
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def _validate_registry_keys(
        self,
    ) -> "Network":
        """
        Validate registry key consistency.

        The dictionary key must always equal the identifier stored
        by the corresponding element.

        Detailed cross-element reference validation is deliberately
        not performed automatically here because networks may be
        constructed incrementally.
        """

        for element_id, element in self.elements.items():

            if element.id != element_id:
                raise ValueError(
                    "Network element registry key "
                    f"{element_id!r} does not match "
                    f"element.id {element.id!r}."
                )

        return self

    # ------------------------------------------------------------------
    # Python Container Protocol
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """
        Return total number of network elements.
        """

        return len(self.elements)

    def __iter__(self) -> Iterator[Element]:
        """
        Iterate over network elements.
        """

        return iter(
            self.elements.values()
        )

    def __contains__(
        self,
        element_or_id: Element | UUID,
    ) -> bool:
        """
        Return whether an element or identifier belongs to the
        network.
        """

        if isinstance(
            element_or_id,
            Element,
        ):
            return (
                element_or_id.id
                in self.elements
            )

        return (
            element_or_id
            in self.elements
        )

    # ------------------------------------------------------------------
    # Element Management
    # ------------------------------------------------------------------

    def add(
        self,
        element: Element,
    ) -> None:
        """
        Add an element to the network.

        Raises
        ------
        DuplicateElementError
            If the element identifier already exists.
        """

        if element.id in self.elements:
            raise DuplicateElementError(
                element.id
            )

        self.elements[
            element.id
        ] = element

    def add_many(
        self,
        elements: Iterable[Element],
    ) -> None:
        """
        Add multiple elements atomically with respect to duplicate-ID
        validation.

        All supplied identifiers are checked before the network is
        modified.

        Raises
        ------
        DuplicateElementError
            If an identifier already exists in the network or occurs
            more than once in the supplied collection.
        """

        candidates = tuple(elements)

        candidate_ids: set[UUID] = set()

        for element in candidates:

            if element.id in self.elements:
                raise DuplicateElementError(
                    element.id
                )

            if element.id in candidate_ids:
                raise DuplicateElementError(
                    element.id
                )

            candidate_ids.add(
                element.id
            )

        for element in candidates:

            self.elements[
                element.id
            ] = element

    def remove(
        self,
        element_id: UUID,
    ) -> Element:
        """
        Remove and return an element.

        Notes
        -----
        This method performs registry removal only.

        Dependency-aware removal policies belong to network
        integrity services.

        Raises
        ------
        ElementNotFoundError
            If the requested element does not exist.
        """

        if element_id not in self.elements:
            raise ElementNotFoundError(
                element_id
            )

        return self.elements.pop(
            element_id
        )

    def clear(self) -> None:
        """
        Remove all network elements.
        """

        self.elements.clear()

    # ------------------------------------------------------------------
    # Basic Lookup
    # ------------------------------------------------------------------

    def get(
        self,
        element_id: UUID,
    ) -> Element | None:
        """
        Return an element by identifier.

        None is returned when the identifier does not exist.
        """

        return self.elements.get(
            element_id
        )

    def require(
        self,
        element_id: UUID,
    ) -> Element:
        """
        Return an element and require that it exists.

        Raises
        ------
        ElementNotFoundError
            If the identifier does not exist.
        """

        element = self.get(
            element_id
        )

        if element is None:
            raise ElementNotFoundError(
                element_id
            )

        return element

    # ------------------------------------------------------------------
    # Typed Lookup
    # ------------------------------------------------------------------

    def get_as(
        self,
        element_id: UUID,
        element_type: type[ElementT],
    ) -> ElementT | None:
        """
        Return an element when it exists and matches a requested
        type.

        None is returned when the identifier does not exist or when
        the element has a different type.

        Use require_as() when absence or a type mismatch should be
        treated as an error.
        """

        element = self.get(
            element_id
        )

        if element is None:
            return None

        if not isinstance(
            element,
            element_type,
        ):
            return None

        return element

    def require_as(
        self,
        element_id: UUID,
        element_type: type[ElementT],
    ) -> ElementT:
        """
        Return an element and require a specific type.

        Raises
        ------
        ElementNotFoundError
            If the identifier does not exist.

        InvalidElementTypeError
            If the element exists but is not of the requested type.
        """

        element = self.require(
            element_id
        )

        if not isinstance(
            element,
            element_type,
        ):
            raise InvalidElementTypeError(
                element_id=element_id,
                expected_type=element_type,
                actual_type=type(element),
            )

        return element

    # ============================================================================
    # Bus Operations
    # ============================================================================
    def bus_by_name(
        self,
        name: str,
    ) -> Bus:
        """
        Return the bus having the specified name.

        Raises
        ------
        KeyError
            If no bus with the given name exists.
        """

        for bus in self.buses:

            if bus.name == name:

                return bus

        raise KeyError(
            f"No bus named '{name}' exists."
        )

    def bus_by_number(
        self,
        bus_number: int,
    ) -> Bus:
        """
        Return the bus having the specified benchmark bus number.

        Raises
        ------
        KeyError
            If no matching bus exists.
        """

        for bus in self.buses:

            if getattr(bus, "bus_number", None) == bus_number:
                return bus

        raise KeyError(
            f"No bus numbered {bus_number} exists."
        )


    # ------------------------------------------------------------------
    # Generic Type Queries
    # ------------------------------------------------------------------

    def elements_of_type(
        self,
        element_type: type[ElementT],
        *,
        exact: bool = False,
    ) -> tuple[ElementT, ...]:
        """
        Return elements matching a requested class.

        Parameters
        ----------
        element_type
            Element class to select.

        exact
            When False, subclasses are included.

            When True, only elements whose concrete class exactly
            equals ``element_type`` are returned.
        """

        if exact:
            return tuple(
                element
                for element
                in self.elements.values()
                if type(element)
                is element_type
            )

        return tuple(
            element
            for element
            in self.elements.values()
            if isinstance(
                element,
                element_type,
            )
        )

    # ------------------------------------------------------------------
    # Fundamental Typed Views
    # ------------------------------------------------------------------

    @property
    def buses(
        self,
    ) -> tuple[Bus, ...]:
        """
        Return all buses.
        """

        return self.elements_of_type(
            Bus
        )

    @property
    def branches(
        self,
    ) -> tuple[Branch, ...]:
        """
        Return all branch-family elements.
        """

        return self.elements_of_type(
            Branch
        )

    @property
    def injections(
        self,
    ) -> tuple[Injection, ...]:
        """
        Return all injection-family elements.
        """

        return self.elements_of_type(
            Injection
        )

    # ------------------------------------------------------------------
    # Branch Views
    # ------------------------------------------------------------------

    @property
    def lines(
        self,
    ) -> tuple[Line, ...]:
        """
        Return all lines.
        """

        return self.elements_of_type(
            Line
        )

    @property
    def transformers(
        self,
    ) -> tuple[Transformer, ...]:
        """
        Return all transformers.
        """

        return self.elements_of_type(
            Transformer
        )

    @property
    def switches(
        self,
    ) -> tuple[Switch, ...]:
        """
        Return all switches.
        """

        return self.elements_of_type(
            Switch
        )

    # ------------------------------------------------------------------
    # Injection Views
    # ------------------------------------------------------------------

    @property
    def loads(
        self,
    ) -> tuple[Load, ...]:
        """
        Return all loads.
        """

        return self.elements_of_type(
            Load
        )

    @property
    def generators(
        self,
    ) -> tuple[Generator, ...]:
        """
        Return all Generator-family resources.

        Specialized subclasses such as Solar and Wind are included.
        """

        return self.elements_of_type(
            Generator
        )

    @property
    def conventional_generators(
        self,
    ) -> tuple[Generator, ...]:
        """
        Return exact Generator instances.

        Specialized Generator subclasses such as Solar and Wind are
        excluded.
        """

        return self.elements_of_type(
            Generator,
            exact=True,
        )

    @property
    def shunts(
        self,
    ) -> tuple[Shunt, ...]:
        """
        Return all shunts.
        """

        return self.elements_of_type(
            Shunt
        )

    @property
    def batteries(
        self,
    ) -> tuple[Battery, ...]:
        """
        Return all battery energy-storage resources.
        """

        return self.elements_of_type(
            Battery
        )

    @property
    def evs(
        self,
    ) -> tuple[EV, ...]:
        """
        Return all electric-vehicle resources.
        """

        return self.elements_of_type(
            EV
        )

    # ------------------------------------------------------------------
    # Renewable Views
    # ------------------------------------------------------------------

    @property
    def solar(
        self,
    ) -> tuple[Solar, ...]:
        """
        Return all solar resources.
        """

        return self.elements_of_type(
            Solar
        )

    @property
    def wind(
        self,
    ) -> tuple[Wind, ...]:
        """
        Return all wind resources.
        """

        return self.elements_of_type(
            Wind
        )

    @property
    def renewables(
        self,
    ) -> tuple[Solar | Wind, ...]:
        """
        Return solar and wind renewable resources.
        """

        return tuple(
            element
            for element
            in self.elements.values()
            if isinstance(
                element,
                (Solar, Wind),
            )
        )

    # ------------------------------------------------------------------
    # Counts
    # ------------------------------------------------------------------

    @property
    def element_count(self) -> int:
        """
        Return total number of elements.
        """

        return len(self.elements)

    @property
    def bus_count(self) -> int:
        """
        Return number of buses.
        """

        return len(self.buses)

    @property
    def branch_count(self) -> int:
        """
        Return number of branch-family elements.
        """

        return len(self.branches)

    @property
    def injection_count(self) -> int:
        """
        Return number of injection-family elements.
        """

        return len(
            self.injections
        )

    # ------------------------------------------------------------------
    # Element-to-Node Queries
    # ------------------------------------------------------------------

    def injections_at(
        self,
        node_id: UUID,
    ) -> tuple[Injection, ...]:
        """
        Return injections referencing a node.

        Notes
        -----
        This is a physical/reference query, not a topology query.

        The method does not require the referenced bus to exist,
        allowing integrity tools to inspect partially constructed
        networks.
        """

        return tuple(
            injection
            for injection
            in self.injections
            if injection.node_id
            == node_id
        )

    def branches_at(
        self,
        node_id: UUID,
    ) -> tuple[Branch, ...]:
        """
        Return physical branches incident on a node.

        Open switches remain included because Network represents
        physical equipment.

        Electrical connectivity belongs to Topology.
        """

        return tuple(
            branch
            for branch
            in self.branches
            if (
                branch.from_node_id
                == node_id
                or branch.to_node_id
                == node_id
            )
        )

    def line_between(
        self,
        from_bus_name: str,
        to_bus_name: str,
    ):
        """
        Return the line connecting two buses.

        Raises
        ------
        KeyError
            If no such line exists.
        """

        from_bus = self.bus_by_name(
            from_bus_name,
        )

        to_bus = self.bus_by_name(
            to_bus_name,
        )

        for line in self.lines:

            if (
                line.from_bus_id == from_bus.id
                and
                line.to_bus_id == to_bus.id
            ):
                return line

        raise KeyError(
            f"No line between "
            f"{from_bus_name} and {to_bus_name}."
        )

    # ------------------------------------------------------------------
    # Reference Integrity
    # ------------------------------------------------------------------

    @property
    def bus_ids(
        self,
    ) -> frozenset[UUID]:
        """
        Return identifiers of all buses.
        """

        return frozenset(
            bus.id
            for bus
            in self.buses
        )

    def missing_node_references(
        self,
    ) -> dict[UUID, tuple[UUID, ...]]:
        """
        Return unresolved node references.

        Returns
        -------
        dict
            Mapping:

                element_id -> missing node IDs

        Branch terminal references and injection node references are
        checked against buses contained in this Network.

        An empty mapping means all currently supported node
        references resolve.
        """

        bus_ids = self.bus_ids

        missing: dict[
            UUID,
            tuple[UUID, ...],
        ] = {}

        # --------------------------------------------------------------
        # Branch references
        # --------------------------------------------------------------

        for branch in self.branches:

            missing_ids: list[UUID] = []

            if (
                branch.from_node_id
                not in bus_ids
            ):
                missing_ids.append(
                    branch.from_node_id
                )

            if (
                branch.to_node_id
                not in bus_ids
                and branch.to_node_id
                not in missing_ids
            ):
                missing_ids.append(
                    branch.to_node_id
                )

            if missing_ids:
                missing[
                    branch.id
                ] = tuple(
                    missing_ids
                )

        # --------------------------------------------------------------
        # Injection references
        # --------------------------------------------------------------

        for injection in self.injections:

            if (
                injection.node_id
                not in bus_ids
            ):
                missing[
                    injection.id
                ] = (
                    injection.node_id,
                )

        return missing

    @property
    def has_complete_node_references(
        self,
    ) -> bool:
        """
        Return whether all supported node references resolve.
        """

        return not bool(
            self.missing_node_references()
        )

    def validate_references(
        self,
    ) -> None:
        """
        Validate branch and injection node references.

        Raises
        ------
        InvalidBranchReferenceError
            If a branch references a nonexistent bus.

        InvalidElementReferenceError
            If an injection references a nonexistent bus.

        Notes
        -----
        Validation stops at the first invalid reference.

        A later validation-report subsystem can collect multiple
        errors without changing this strict validation API.
        """

        bus_ids = self.bus_ids

        # --------------------------------------------------------------
        # Branch references
        # --------------------------------------------------------------

        for branch in self.branches:

            if (
                branch.from_node_id
                not in bus_ids
            ):
                raise InvalidBranchReferenceError(
                    branch_id=branch.id,
                    node_id=branch.from_node_id,
                    terminal="from",
                )

            if (
                branch.to_node_id
                not in bus_ids
            ):
                raise InvalidBranchReferenceError(
                    branch_id=branch.id,
                    node_id=branch.to_node_id,
                    terminal="to",
                )

        # --------------------------------------------------------------
        # Injection references
        # --------------------------------------------------------------

        for injection in self.injections:

            if (
                injection.node_id
                not in bus_ids
            ):
                raise InvalidElementReferenceError(
                    element_id=injection.id,
                    referenced_id=(
                        injection.node_id
                    ),
                    reference_name="node_id",
                )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Network",
]