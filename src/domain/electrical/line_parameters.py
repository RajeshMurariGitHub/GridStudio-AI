"""
GridStudio AI

Module:
    line_parameters.py

Description:
    Defines solver-independent electrical parameter models for
    transmission and distribution lines.

    LineParameters supports two electrical representations:

    1. Balanced positive-sequence parameters for balanced
       transmission and distribution studies.

    2. Phase-domain impedance and shunt-admittance matrices for
       unbalanced multi-phase distribution studies.

    The model is independent of pandapower, OpenDSS, and other
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

from src.core.models import BaseModel
from src.domain.electrical.phases import (
    PHASE_ABC,
    PhaseSet,
)


# ============================================================================
# Type Aliases
# ============================================================================


ComplexMatrix = tuple[
    tuple[complex, ...],
    ...,
]


# ============================================================================
# Line Parameters
# ============================================================================


class LineParameters(BaseModel):
    """
    Electrical parameters of a transmission or distribution line.

    Two representations are supported.

    Balanced Representation
    -----------------------
    A balanced line may be described using positive-sequence
    quantities per unit length:

        r1_ohm_per_km
        x1_ohm_per_km
        c1_nf_per_km

    Optional zero-sequence parameters may also be supplied:

        r0_ohm_per_km
        x0_ohm_per_km
        c0_nf_per_km

    Phase-Domain Representation
    ---------------------------
    An unbalanced line may instead be described using matrices:

        impedance_matrix_ohm_per_km
        shunt_admittance_matrix_s_per_km

    Matrix rows and columns correspond to the phase ordering stored
    in ``phases``.

    For example, for phases A-B-C:

        Z = [
            [Zaa, Zab, Zac],
            [Zba, Zbb, Zbc],
            [Zca, Zcb, Zcc],
        ]

    where diagonal entries represent self impedance and off-diagonal
    entries represent mutual impedance.

    Notes
    -----
    Exactly one primary representation must be supplied:

    * sequence parameters, or
    * phase-domain impedance matrix.

    This prevents ambiguous line definitions.

    Parameters are expressed per kilometer. Physical line length
    belongs to the Line model rather than this reusable parameter
    model.
    """

    # ------------------------------------------------------------------
    # Phase Definition
    # ------------------------------------------------------------------

    phases: PhaseSet | None = Field(
        default=None,
        description=(
            "Phase ordering associated with phase-domain matrices. "
            "May also document the intended phases of balanced "
            "parameters."
        ),
    )

    # ------------------------------------------------------------------
    # Positive-Sequence Parameters
    # ------------------------------------------------------------------

    r1_ohm_per_km: float | None = Field(
        default=None,
        ge=0.0,
        description=(
            "Positive-sequence resistance in ohms per kilometer."
        ),
    )

    x1_ohm_per_km: float | None = Field(
        default=None,
        description=(
            "Positive-sequence reactance in ohms per kilometer."
        ),
    )

    c1_nf_per_km: float | None = Field(
        default=None,
        ge=0.0,
        description=(
            "Positive-sequence capacitance in nanofarads per "
            "kilometer."
        ),
    )

    # ------------------------------------------------------------------
    # Zero-Sequence Parameters
    # ------------------------------------------------------------------

    r0_ohm_per_km: float | None = Field(
        default=None,
        ge=0.0,
        description=(
            "Optional zero-sequence resistance in ohms per "
            "kilometer."
        ),
    )

    x0_ohm_per_km: float | None = Field(
        default=None,
        description=(
            "Optional zero-sequence reactance in ohms per "
            "kilometer."
        ),
    )

    c0_nf_per_km: float | None = Field(
        default=None,
        ge=0.0,
        description=(
            "Optional zero-sequence capacitance in nanofarads per "
            "kilometer."
        ),
    )

    # ------------------------------------------------------------------
    # Phase-Domain Parameters
    # ------------------------------------------------------------------

    impedance_matrix_ohm_per_km: ComplexMatrix | None = Field(
        default=None,
        description=(
            "Phase-domain series impedance matrix in ohms per "
            "kilometer."
        ),
    )

    shunt_admittance_matrix_s_per_km: ComplexMatrix | None = Field(
        default=None,
        description=(
            "Optional phase-domain shunt-admittance matrix in "
            "siemens per kilometer."
        ),
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def _validate_representation(
        self,
    ) -> Self:
        """
        Validate the selected line-parameter representation.
        """

        has_positive_sequence = (
            self.r1_ohm_per_km is not None
            or self.x1_ohm_per_km is not None
            or self.c1_nf_per_km is not None
        )

        has_phase_domain = (
            self.impedance_matrix_ohm_per_km is not None
        )

        if not has_positive_sequence and not has_phase_domain:
            raise ValueError(
                "LineParameters requires either positive-sequence "
                "parameters or a phase-domain impedance matrix."
            )

        if has_positive_sequence and has_phase_domain:
            raise ValueError(
                "LineParameters cannot define both sequence and "
                "phase-domain representations simultaneously."
            )

        if has_positive_sequence:
            self._validate_sequence_parameters()

        if has_phase_domain:
            self._validate_phase_domain_parameters()

        return self

    # ------------------------------------------------------------------
    # Sequence Validation
    # ------------------------------------------------------------------

    def _validate_sequence_parameters(
        self,
    ) -> None:
        """
        Validate balanced sequence parameters.
        """

        if self.r1_ohm_per_km is None:
            raise ValueError(
                "Balanced line parameters require "
                "r1_ohm_per_km."
            )

        if self.x1_ohm_per_km is None:
            raise ValueError(
                "Balanced line parameters require "
                "x1_ohm_per_km."
            )

        zero_sequence_values = (
            self.r0_ohm_per_km,
            self.x0_ohm_per_km,
            self.c0_nf_per_km,
        )

        has_any_zero_sequence = any(
            value is not None
            for value in zero_sequence_values
        )

        if has_any_zero_sequence:
            if self.r0_ohm_per_km is None:
                raise ValueError(
                    "Zero-sequence parameters require "
                    "r0_ohm_per_km."
                )

            if self.x0_ohm_per_km is None:
                raise ValueError(
                    "Zero-sequence parameters require "
                    "x0_ohm_per_km."
                )

    # ------------------------------------------------------------------
    # Phase-Domain Validation
    # ------------------------------------------------------------------

    def _validate_phase_domain_parameters(
        self,
    ) -> None:
        """
        Validate phase-domain matrix dimensions.
        """

        if self.phases is None:
            raise ValueError(
                "Phase-domain line parameters require phases."
            )

        expected_size = self.phases.conductor_count

        self._validate_square_matrix(
            matrix=self.impedance_matrix_ohm_per_km,
            expected_size=expected_size,
            field_name="impedance_matrix_ohm_per_km",
        )

        if self.shunt_admittance_matrix_s_per_km is not None:
            self._validate_square_matrix(
                matrix=self.shunt_admittance_matrix_s_per_km,
                expected_size=expected_size,
                field_name=(
                    "shunt_admittance_matrix_s_per_km"
                ),
            )

    @staticmethod
    def _validate_square_matrix(
        *,
        matrix: ComplexMatrix | None,
        expected_size: int,
        field_name: str,
    ) -> None:
        """
        Validate matrix dimensions.

        Parameters
        ----------
        matrix
            Matrix to validate.

        expected_size
            Required row and column count.

        field_name
            Name used in validation messages.
        """

        if matrix is None:
            raise ValueError(
                f"{field_name} cannot be None."
            )

        if len(matrix) != expected_size:
            raise ValueError(
                f"{field_name} must contain "
                f"{expected_size} rows."
            )

        for row in matrix:
            if len(row) != expected_size:
                raise ValueError(
                    f"{field_name} must be a "
                    f"{expected_size}x{expected_size} matrix."
                )

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def balanced(
        cls,
        *,
        r1_ohm_per_km: float,
        x1_ohm_per_km: float,
        c1_nf_per_km: float = 0.0,
        r0_ohm_per_km: float | None = None,
        x0_ohm_per_km: float | None = None,
        c0_nf_per_km: float | None = None,
        phases: PhaseSet = PHASE_ABC,
    ) -> Self:
        """
        Create balanced sequence-based line parameters.
        """

        return cls(
            phases=phases,
            r1_ohm_per_km=r1_ohm_per_km,
            x1_ohm_per_km=x1_ohm_per_km,
            c1_nf_per_km=c1_nf_per_km,
            r0_ohm_per_km=r0_ohm_per_km,
            x0_ohm_per_km=x0_ohm_per_km,
            c0_nf_per_km=c0_nf_per_km,
        )

    @classmethod
    def phase_domain(
        cls,
        *,
        phases: PhaseSet,
        impedance_matrix_ohm_per_km: ComplexMatrix,
        shunt_admittance_matrix_s_per_km: (
            ComplexMatrix | None
        ) = None,
    ) -> Self:
        """
        Create phase-domain line parameters.
        """

        return cls(
            phases=phases,
            impedance_matrix_ohm_per_km=(
                impedance_matrix_ohm_per_km
            ),
            shunt_admittance_matrix_s_per_km=(
                shunt_admittance_matrix_s_per_km
            ),
        )

    # ------------------------------------------------------------------
    # Representation Properties
    # ------------------------------------------------------------------

    @property
    def is_balanced(self) -> bool:
        """
        Return whether sequence parameters are used.
        """

        return (
            self.impedance_matrix_ohm_per_km
            is None
        )

    @property
    def is_phase_domain(self) -> bool:
        """
        Return whether phase-domain parameters are used.
        """

        return (
            self.impedance_matrix_ohm_per_km
            is not None
        )

    @property
    def has_zero_sequence(self) -> bool:
        """
        Return whether zero-sequence impedance is defined.
        """

        return (
            self.r0_ohm_per_km is not None
            and self.x0_ohm_per_km is not None
        )

    @property
    def has_shunt_admittance_matrix(self) -> bool:
        """
        Return whether phase-domain shunt admittance is defined.
        """

        return (
            self.shunt_admittance_matrix_s_per_km
            is not None
        )

    # ------------------------------------------------------------------
    # Sequence Impedance
    # ------------------------------------------------------------------

    @property
    def positive_sequence_impedance_ohm_per_km(
        self,
    ) -> complex | None:
        """
        Return positive-sequence series impedance per kilometer.
        """

        if not self.is_balanced:
            return None

        return complex(
            self.r1_ohm_per_km,
            self.x1_ohm_per_km,
        )

    @property
    def zero_sequence_impedance_ohm_per_km(
        self,
    ) -> complex | None:
        """
        Return zero-sequence series impedance per kilometer.
        """

        if not self.has_zero_sequence:
            return None

        return complex(
            self.r0_ohm_per_km,
            self.x0_ohm_per_km,
        )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "ComplexMatrix",
    "LineParameters",
]