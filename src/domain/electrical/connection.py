"""
GridStudio AI

Module:
    connection.py

Description:
    Defines solver-independent electrical connection value objects
    used throughout the GridStudio AI domain.

    ElectricalConnection describes how an electrical device or
    winding is connected to the network, including its fundamental
    connection topology and grounding method.

    The model is suitable for balanced and unbalanced networks and
    remains independent of pandapower, OpenDSS, and other simulation
    engines.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from typing import Self

from pydantic import Field
from pydantic import model_validator

from src.core.enums import (
    ConnectionType,
    GroundingType,
)
from src.core.models import BaseModel


# ============================================================================
# Electrical Connection
# ============================================================================


class ElectricalConnection(BaseModel):
    """
    Electrical connection configuration of equipment or a winding.

    Parameters
    ----------
    connection_type
        Fundamental electrical connection topology.

    grounding
        Grounding method associated with the connection.

    grounding_resistance_ohm
        Optional grounding resistance.

    grounding_reactance_ohm
        Optional grounding reactance.

    Notes
    -----
    Connection topology and grounding are intentionally represented
    separately.

    For example, a grounded-wye connection is represented as:

        connection_type = ConnectionType.WYE
        grounding = GroundingType.SOLID

    rather than introducing a separate GROUNDED_WYE connection type.

    This avoids combining independent electrical concepts into a
    single enumeration and supports future grounding models more
    naturally.

    Transformer vector groups and phase displacement are not
    represented here. Those belong to transformer-specific models.
    """

    # ------------------------------------------------------------------
    # Connection Topology
    # ------------------------------------------------------------------

    connection_type: ConnectionType = Field(
        default=ConnectionType.WYE,
        description=(
            "Fundamental electrical connection topology."
        ),
    )

    # ------------------------------------------------------------------
    # Grounding
    # ------------------------------------------------------------------

    grounding: GroundingType = Field(
        default=GroundingType.NONE,
        description=(
            "Grounding method associated with the connection."
        ),
    )

    grounding_resistance_ohm: float | None = Field(
        default=None,
        ge=0.0,
        description=(
            "Grounding resistance in ohms, when applicable."
        ),
    )

    grounding_reactance_ohm: float | None = Field(
        default=None,
        ge=0.0,
        description=(
            "Magnitude of grounding reactance in ohms, when "
            "applicable."
        ),
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def _validate_grounding(
        self,
    ) -> Self:
        """
        Validate grounding configuration consistency.
        """

        if self.grounding == GroundingType.NONE:
            if (
                self.grounding_resistance_ohm is not None
                or self.grounding_reactance_ohm is not None
            ):
                raise ValueError(
                    "Grounding impedance cannot be specified when "
                    "grounding is GroundingType.NONE."
                )

        if self.grounding == GroundingType.SOLID:
            if (
                self.grounding_resistance_ohm not in (None, 0.0)
                or self.grounding_reactance_ohm not in (None, 0.0)
            ):
                raise ValueError(
                    "Solid grounding cannot have a non-zero "
                    "grounding impedance."
                )

        if self.grounding == GroundingType.RESISTANCE:
            if self.grounding_resistance_ohm is None:
                raise ValueError(
                    "Resistance grounding requires "
                    "grounding_resistance_ohm."
                )

        if self.grounding == GroundingType.REACTANCE:
            if self.grounding_reactance_ohm is None:
                raise ValueError(
                    "Reactance grounding requires "
                    "grounding_reactance_ohm."
                )

        return self

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def wye(
        cls,
    ) -> Self:
        """
        Create an ungrounded wye connection.
        """

        return cls(
            connection_type=ConnectionType.WYE,
            grounding=GroundingType.NONE,
        )

    @classmethod
    def grounded_wye(
        cls,
    ) -> Self:
        """
        Create a solidly grounded wye connection.
        """

        return cls(
            connection_type=ConnectionType.WYE,
            grounding=GroundingType.SOLID,
        )

    @classmethod
    def resistance_grounded_wye(
        cls,
        resistance_ohm: float,
    ) -> Self:
        """
        Create a resistance-grounded wye connection.

        Parameters
        ----------
        resistance_ohm
            Neutral grounding resistance in ohms.
        """

        return cls(
            connection_type=ConnectionType.WYE,
            grounding=GroundingType.RESISTANCE,
            grounding_resistance_ohm=resistance_ohm,
        )

    @classmethod
    def reactance_grounded_wye(
        cls,
        reactance_ohm: float,
    ) -> Self:
        """
        Create a reactance-grounded wye connection.

        Parameters
        ----------
        reactance_ohm
            Neutral grounding reactance magnitude in ohms.
        """

        return cls(
            connection_type=ConnectionType.WYE,
            grounding=GroundingType.REACTANCE,
            grounding_reactance_ohm=reactance_ohm,
        )

    @classmethod
    def delta(
        cls,
    ) -> Self:
        """
        Create an ungrounded delta connection.
        """

        return cls(
            connection_type=ConnectionType.DELTA,
            grounding=GroundingType.NONE,
        )

    # ------------------------------------------------------------------
    # Connection Properties
    # ------------------------------------------------------------------

    @property
    def is_wye(self) -> bool:
        """
        Return whether this is a wye connection.
        """

        return self.connection_type == ConnectionType.WYE

    @property
    def is_delta(self) -> bool:
        """
        Return whether this is a delta connection.
        """

        return self.connection_type == ConnectionType.DELTA

    @property
    def is_grounded(self) -> bool:
        """
        Return whether an explicit grounding method is present.
        """

        return self.grounding != GroundingType.NONE

    @property
    def is_solidly_grounded(self) -> bool:
        """
        Return whether the connection is solidly grounded.
        """

        return self.grounding == GroundingType.SOLID

    @property
    def has_grounding_impedance(self) -> bool:
        """
        Return whether explicit grounding impedance is present.
        """

        return (
            self.grounding_resistance_ohm is not None
            or self.grounding_reactance_ohm is not None
        )

    # ------------------------------------------------------------------
    # String Representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """
        Return a compact human-readable connection description.
        """

        if self.grounding == GroundingType.NONE:
            return self.connection_type.value

        return (
            f"{self.connection_type.value}-"
            f"{self.grounding.value}"
        )


# ============================================================================
# Common Connections
# ============================================================================


WYE = ElectricalConnection.wye()

GROUNDED_WYE = ElectricalConnection.grounded_wye()

DELTA = ElectricalConnection.delta()


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "DELTA",
    "GROUNDED_WYE",
    "WYE",
    "ElectricalConnection",
]