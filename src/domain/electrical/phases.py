"""
GridStudio AI

Module:
    phases.py

Description:
    Defines immutable phase-set value objects used throughout the
    GridStudio AI electrical domain.

    PhaseSet provides a canonical representation of the electrical
    phases associated with buses, branches, loads, generators,
    transformers, DERs, and other network equipment.

    The representation is solver-independent and supports both
    balanced and unbalanced electrical networks.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Self

from pydantic import Field
from pydantic import field_validator

from src.core.enums.electrical import Phase
from src.core.models import BaseModel

# ============================================================================
# Phase Ordering
# ============================================================================


_PHASE_ORDER: tuple[Phase, ...] = (
    Phase.A,
    Phase.B,
    Phase.C,
    Phase.N,
)


# ============================================================================
# Phase Set
# ============================================================================


class PhaseSet(BaseModel):
    """
    Immutable collection of electrical phases.

    PhaseSet provides a common solver-independent representation
    for phase connectivity throughout GridStudio AI.

    Examples
    --------
    Three-phase network element:

        PhaseSet.three_phase()

    Single-phase phase-A element:

        PhaseSet.single(Phase.A)

    Two-phase element:

        PhaseSet.from_phases(
            Phase.A,
            Phase.B,
        )

    Three-phase four-wire element:

        PhaseSet.three_phase_with_neutral()

    Notes
    -----
    The ordering of phases is canonical:

        A, B, C, N

    This is important when mapping GridStudio models to external
    simulation engines such as OpenDSS and when interpreting
    phase-specific simulation results.

    PhaseSet describes physical phase connectivity.

    It does not indicate whether the network should be solved using
    a balanced or unbalanced formulation. That distinction belongs
    to NetworkRepresentation.
    """

    phases: tuple[Phase, ...] = Field(
        ...,
        min_length=1,
        description=(
            "Ordered electrical phases associated with the "
            "network component."
        ),
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @field_validator(
        "phases",
        mode="before",
    )
    @classmethod
    def _normalize_phases(
        cls,
        value: object,
    ) -> tuple[Phase, ...]:
        """
        Normalize input into canonical phase order.

        Duplicate phases are removed automatically.

        Parameters
        ----------
        value
            Iterable containing Phase values or compatible strings.

        Returns
        -------
        tuple[Phase, ...]
            Unique phases in canonical A-B-C-N order.
        """

        if value is None:
            raise ValueError(
                "PhaseSet requires at least one phase."
            )

        if isinstance(value, Phase):
            raw_phases = [value]

        elif isinstance(value, str):
            raw_phases = [value]

        elif isinstance(value, Iterable):
            raw_phases = list(value)

        else:
            raise TypeError(
                "phases must be a Phase or an iterable of phases."
            )

        if not raw_phases:
            raise ValueError(
                "PhaseSet requires at least one phase."
            )

        normalized: set[Phase] = set()

        for phase in raw_phases:
            try:
                normalized.add(Phase(phase))
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid electrical phase: {phase!r}."
                ) from exc

        return tuple(
            phase
            for phase in _PHASE_ORDER
            if phase in normalized
        )

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def single(
        cls,
        phase: Phase,
    ) -> Self:
        """
        Create a single-phase PhaseSet.

        Parameters
        ----------
        phase
            Electrical phase.

        Returns
        -------
        PhaseSet
            Single-phase phase set.
        """

        return cls(
            phases=(phase,),
        )

    @classmethod
    def from_phases(
        cls,
        *phases: Phase,
    ) -> Self:
        """
        Create a PhaseSet from individual phase arguments.

        Parameters
        ----------
        *phases
            Electrical phases.

        Returns
        -------
        PhaseSet
            Normalized phase set.
        """

        return cls(
            phases=phases,
        )

    @classmethod
    def three_phase(cls) -> Self:
        """
        Create the standard three-phase A-B-C phase set.
        """

        return cls(
            phases=(
                Phase.A,
                Phase.B,
                Phase.C,
            ),
        )

    @classmethod
    def three_phase_with_neutral(cls) -> Self:
        """
        Create a three-phase four-wire A-B-C-N phase set.
        """

        return cls(
            phases=(
                Phase.A,
                Phase.B,
                Phase.C,
                Phase.N,
            ),
        )

    # ------------------------------------------------------------------
    # Membership
    # ------------------------------------------------------------------

    def contains(
        self,
        phase: Phase,
    ) -> bool:
        """
        Return whether the phase is present.
        """

        return phase in self.phases

    def contains_all(
        self,
        *phases: Phase,
    ) -> bool:
        """
        Return whether all requested phases are present.
        """

        return all(
            phase in self.phases
            for phase in phases
        )

    # ------------------------------------------------------------------
    # Phase Properties
    # ------------------------------------------------------------------

    @property
    def count(self) -> int:
        """
        Number of phases including neutral.
        """

        return len(self.phases)

    @property
    def conductor_count(self) -> int:
        """
        Number of represented conductors.

        For the current phase model this is equivalent to count.
        """

        return len(self.phases)

    @property
    def phase_count(self) -> int:
        """
        Number of energized phase conductors excluding neutral.
        """

        return sum(
            phase in {
                Phase.A,
                Phase.B,
                Phase.C,
            }
            for phase in self.phases
        )

    @property
    def has_neutral(self) -> bool:
        """
        Return whether a neutral conductor is represented.
        """

        return Phase.N in self.phases

    @property
    def is_single_phase(self) -> bool:
        """
        Return whether exactly one energized phase is present.
        """

        return self.phase_count == 1

    @property
    def is_two_phase(self) -> bool:
        """
        Return whether exactly two energized phases are present.
        """

        return self.phase_count == 2

    @property
    def is_three_phase(self) -> bool:
        """
        Return whether phases A, B, and C are present.
        """

        return self.contains_all(
            Phase.A,
            Phase.B,
            Phase.C,
        )

    @property
    def is_three_phase_four_wire(self) -> bool:
        """
        Return whether A, B, C, and neutral are present.
        """

        return (
            self.is_three_phase
            and self.has_neutral
        )

    # ------------------------------------------------------------------
    # Collection Behavior
    # ------------------------------------------------------------------

    def __contains__(
        self,
        phase: object,
    ) -> bool:
        """
        Support ``phase in phase_set`` syntax.
        """

        return phase in self.phases

    def __iter__(self):
        """
        Iterate through phases in canonical order.
        """

        return iter(self.phases)

    def __len__(self) -> int:
        """
        Return the number of represented conductors.
        """

        return len(self.phases)

    # ------------------------------------------------------------------
    # String Representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Return compact phase notation.

        Examples
        --------
        A

        ABC

        ABCN
        """

        return "".join(
            phase.value.upper()
            for phase in self.phases
        )


# ============================================================================
# Common Phase Sets
# ============================================================================


PHASE_A = PhaseSet.single(
    Phase.A,
)

PHASE_B = PhaseSet.single(
    Phase.B,
)

PHASE_C = PhaseSet.single(
    Phase.C,
)

PHASE_AB = PhaseSet.from_phases(
    Phase.A,
    Phase.B,
)

PHASE_BC = PhaseSet.from_phases(
    Phase.B,
    Phase.C,
)

PHASE_CA = PhaseSet.from_phases(
    Phase.C,
    Phase.A,
)

PHASE_ABC = PhaseSet.three_phase()

PHASE_ABCN = PhaseSet.three_phase_with_neutral()


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "PHASE_A",
    "PHASE_AB",
    "PHASE_ABC",
    "PHASE_ABCN",
    "PHASE_B",
    "PHASE_BC",
    "PHASE_C",
    "PHASE_CA",
    "PhaseSet",
]