"""
GridStudio AI

Module:
    element.py

Description:
    Defines the foundational electrical element model used
    throughout the GridStudio AI domain.

    ElectricalElement extends ElectricalAsset with phase
    connectivity information required by assets that participate
    directly in the electrical network model.

    The model is solver-independent and supports both balanced and
    unbalanced network representations.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from pydantic import Field

from src.domain.asset import Asset
from src.domain.electrical import (
    PHASE_ABC,
    PhaseSet,
)


# ============================================================================
# Electrical Element
# ============================================================================


class Element(Asset):
    """
    Base class for assets participating in the electrical network.

    ElectricalElement introduces the phase connectivity shared by
    electrically modeled network equipment.

    Examples include:

    * buses,
    * lines,
    * transformers,
    * switches,
    * loads,
    * generators,
    * solar PV,
    * wind generation,
    * batteries,
    * EVs,
    * shunts.

    Parameters
    ----------
    phases
        Electrical phases represented by the element.

    Notes
    -----
    The default phase configuration is three-phase A-B-C because
    this is the most common representation for balanced transmission
    and distribution benchmark networks.

    Unbalanced and phase-specific equipment should explicitly
    provide its actual phase set.

    For example:

        phases=PHASE_A

    or:

        phases=PHASE_ABCN

    ElectricalElement intentionally does not define bus connectivity.

    Connectivity belongs to specialized domain abstractions:

    * Node represents a network connection point.
    * Branch connects two network nodes.
    * Injection attaches power to a network node.

    This separation prevents the base element model from becoming
    dependent on a particular topology representation.
    """

    # ------------------------------------------------------------------
    # Electrical Phases
    # ------------------------------------------------------------------

    phases: PhaseSet = Field(
        default=PHASE_ABC,
        description=(
            "Electrical phases associated with the network element."
        ),
    )

    # ------------------------------------------------------------------
    # Convenience Properties
    # ------------------------------------------------------------------

    @property
    def phase_count(self) -> int:
        """
        Number of energized phase conductors.

        Neutral, when present, is not included in this count.
        """

        return self.phases.phase_count

    @property
    def conductor_count(self) -> int:
        """
        Number of represented conductors including neutral.
        """

        return self.phases.conductor_count

    @property
    def is_single_phase(self) -> bool:
        """
        Return whether the element has one energized phase.
        """

        return self.phases.is_single_phase

    @property
    def is_two_phase(self) -> bool:
        """
        Return whether the element has two energized phases.
        """

        return self.phases.is_two_phase

    @property
    def is_three_phase(self) -> bool:
        """
        Return whether phases A, B, and C are represented.
        """

        return self.phases.is_three_phase

    @property
    def has_neutral(self) -> bool:
        """
        Return whether the element explicitly represents neutral.
        """

        return self.phases.has_neutral


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Element",
]