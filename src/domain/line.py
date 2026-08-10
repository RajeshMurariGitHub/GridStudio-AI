"""
GridStudio AI

Module:
    line.py

Description:
    Defines the electrical line model used throughout GridStudio AI.

    A Line represents a two-terminal overhead or underground
    electrical branch connecting two network nodes.

    Electrical characteristics are represented through
    solver-independent line parameter models so that the same
    domain object can support both balanced and unbalanced
    simulation engines.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from typing import Self

from pydantic import Field
from pydantic import model_validator

from src.domain.branch import Branch
from src.domain.electrical.line_parameters import (
    LineParameters,
)


# ============================================================================
# Line
# ============================================================================


class Line(Branch):
    """
    Electrical transmission or distribution line.

    A Line specializes Branch by adding physical length, electrical
    parameters, and optional continuous-current rating.

    The model is solver-independent.

    Parameters
    ----------
    length_km
        Physical line length in kilometers.

    parameters
        Electrical line parameters.

    maximum_current_ka
        Optional continuous-current rating in kA.

    parallel_count
        Number of electrically equivalent parallel circuits
        represented by this line object.

    Notes
    -----
    Line topology is inherited from Branch:

        from_node_id
        to_node_id

    Phase connectivity is inherited from ElectricalElement:

        phases

    Electrical impedance and shunt characteristics are contained
    in ``LineParameters``.

    This separation allows GridStudio AI to represent both:

    * balanced positive-sequence line models, and
    * unbalanced phase-domain line models.

    Conversion to pandapower, OpenDSS, or another simulation engine
    belongs in the corresponding engine adapter.
    """

    # ------------------------------------------------------------------
    # Physical Properties
    # ------------------------------------------------------------------

    length_km: float = Field(
        ...,
        gt=0.0,
        description="Physical length of the line in kilometers.",
    )

    # ------------------------------------------------------------------
    # Electrical Parameters
    # ------------------------------------------------------------------

    parameters: LineParameters = Field(
        ...,
        description=(
            "Solver-independent electrical parameters of the line."
        ),
    )

    # ------------------------------------------------------------------
    # Rating
    # ------------------------------------------------------------------

    maximum_current_ka: float | None = Field(
        default=None,
        gt=0.0,
        description=(
            "Optional continuous-current rating of one circuit "
            "in kA."
        ),
    )

    # ------------------------------------------------------------------
    # Parallel Circuits
    # ------------------------------------------------------------------

    parallel_count: int = Field(
        default=1,
        ge=1,
        description=(
            "Number of electrically equivalent parallel circuits "
            "represented by this line."
        ),
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def _validate_line_configuration(
        self,
    ) -> Self:
        """
        Validate consistency between line phases and parameters.
        """

        parameter_phases = self.parameters.phases

        if parameter_phases is not None:
            for phase in self.phases:
                if phase not in parameter_phases:
                    raise ValueError(
                        "Line phases must be represented by the "
                        "associated LineParameters."
                    )

        return self

    # ------------------------------------------------------------------
    # Rating Properties
    # ------------------------------------------------------------------

    @property
    def has_current_rating(self) -> bool:
        """
        Return whether a continuous-current rating is defined.
        """

        return self.maximum_current_ka is not None

    @property
    def total_current_capacity_ka(
        self,
    ) -> float | None:
        """
        Return aggregate current capacity of parallel circuits.

        Returns
        -------
        float | None
            Aggregate current capacity in kA when a rating exists.
        """

        if self.maximum_current_ka is None:
            return None

        return (
            self.maximum_current_ka
            * self.parallel_count
        )

    # ------------------------------------------------------------------
    # Parameter Representation
    # ------------------------------------------------------------------

    @property
    def is_balanced_parameter_model(self) -> bool:
        """
        Return whether the line uses balanced parameters.
        """

        return self.parameters.is_balanced

    @property
    def is_phase_domain_parameter_model(self) -> bool:
        """
        Return whether the line uses phase-domain parameters.
        """

        return self.parameters.is_phase_domain


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Line",
]