"""
GridStudio AI

Module:
    generator.py

Description:
    Defines the conventional electrical generator model used
    throughout GridStudio AI.

    A Generator represents a controllable source of active and
    reactive power connected to a network node.

    The model supports balanced and unbalanced electrical networks
    and remains independent of pandapower, OpenDSS, and other
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

from src.domain.electrical import (
    GROUNDED_WYE,
    ElectricalConnection,
)
from src.domain.injection import Injection


# ============================================================================
# Generator
# ============================================================================


class Generator(Injection):
    """
    Conventional electrical generator.

    Generator specializes Injection with generator operating limits,
    voltage-control information, and electrical connection data.

    Sign Convention
    ---------------
    GridStudio AI uses the network-injection convention inherited
    from Injection:

    * positive active power means generation into the network,
    * negative active power means absorption from the network,
    * positive reactive power means reactive-power injection,
    * negative reactive power means reactive-power absorption.

    A conventional generating unit therefore normally has:

        active_power_mw >= 0

    Reactive power may be either positive or negative depending on
    operating conditions and voltage-control requirements.

    Notes
    -----
    This model represents generator equipment.

    Slack/reference-bus behavior is not inherently a property of
    Generator. The network and simulation layers determine how a
    reference source is represented by a particular simulation
    engine.

    For example:

    * pandapower may represent a reference source using ``ext_grid``;
    * OpenDSS may represent the feeder source using ``Vsource``.

    Those mappings belong in engine adapters rather than this
    domain model.

    Solar PV and wind generation should specialize the injection
    architecture separately because they require resource-dependent
    availability and time-series behavior.
    """

    # ------------------------------------------------------------------
    # Electrical Connection
    # ------------------------------------------------------------------

    connection: ElectricalConnection = Field(
        default=GROUNDED_WYE,
        description=(
            "Electrical connection configuration of the generator."
        ),
    )

    # ------------------------------------------------------------------
    # Active-Power Limits
    # ------------------------------------------------------------------

    minimum_active_power_mw: float = Field(
        default=0.0,
        description=(
            "Minimum active-power operating limit in MW."
        ),
    )

    maximum_active_power_mw: float | None = Field(
        default=None,
        ge=0.0,
        description=(
            "Optional maximum active-power operating limit in MW."
        ),
    )

    # ------------------------------------------------------------------
    # Reactive-Power Limits
    # ------------------------------------------------------------------

    minimum_reactive_power_mvar: float | None = Field(
        default=None,
        description=(
            "Optional minimum reactive-power operating limit "
            "in MVAr."
        ),
    )

    maximum_reactive_power_mvar: float | None = Field(
        default=None,
        description=(
            "Optional maximum reactive-power operating limit "
            "in MVAr."
        ),
    )

    # ------------------------------------------------------------------
    # Voltage Control
    # ------------------------------------------------------------------

    voltage_setpoint_pu: float | None = Field(
        default=None,
        gt=0.0,
        description=(
            "Optional terminal voltage-magnitude setpoint "
            "in per unit."
        ),
    )

    voltage_control_enabled: bool = Field(
        default=False,
        description=(
            "Whether the generator is configured to regulate "
            "terminal voltage."
        ),
    )

    # ------------------------------------------------------------------
    # Rating
    # ------------------------------------------------------------------

    rated_power_mva: float | None = Field(
        default=None,
        gt=0.0,
        description=(
            "Optional apparent-power rating of the generator "
            "in MVA."
        ),
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def _validate_generator_configuration(
        self,
    ) -> Self:
        """
        Validate generator operating configuration.
        """

        if self.active_power_mw < 0.0:
            raise ValueError(
                "Generator active_power_mw must be greater than "
                "or equal to zero under the GridStudio "
                "network-injection sign convention."
            )

        if (
            self.maximum_active_power_mw is not None
            and self.minimum_active_power_mw
            > self.maximum_active_power_mw
        ):
            raise ValueError(
                "minimum_active_power_mw cannot exceed "
                "maximum_active_power_mw."
            )

        if (
            self.active_power_mw
            < self.minimum_active_power_mw
        ):
            raise ValueError(
                "active_power_mw cannot be below "
                "minimum_active_power_mw."
            )

        if (
            self.maximum_active_power_mw is not None
            and self.active_power_mw
            > self.maximum_active_power_mw
        ):
            raise ValueError(
                "active_power_mw cannot exceed "
                "maximum_active_power_mw."
            )

        if (
            self.minimum_reactive_power_mvar is not None
            and self.maximum_reactive_power_mvar is not None
            and self.minimum_reactive_power_mvar
            > self.maximum_reactive_power_mvar
        ):
            raise ValueError(
                "minimum_reactive_power_mvar cannot exceed "
                "maximum_reactive_power_mvar."
            )

        if (
            self.minimum_reactive_power_mvar is not None
            and self.reactive_power_mvar
            < self.minimum_reactive_power_mvar
        ):
            raise ValueError(
                "reactive_power_mvar cannot be below "
                "minimum_reactive_power_mvar."
            )

        if (
            self.maximum_reactive_power_mvar is not None
            and self.reactive_power_mvar
            > self.maximum_reactive_power_mvar
        ):
            raise ValueError(
                "reactive_power_mvar cannot exceed "
                "maximum_reactive_power_mvar."
            )

        if (
            self.voltage_control_enabled
            and self.voltage_setpoint_pu is None
        ):
            raise ValueError(
                "voltage_setpoint_pu is required when "
                "voltage_control_enabled is True."
            )

        if self.rated_power_mva is not None:
            apparent_power = abs(
                complex(
                    self.active_power_mw,
                    self.reactive_power_mvar,
                )
            )

            if apparent_power > self.rated_power_mva:
                raise ValueError(
                    "Generator operating apparent power cannot "
                    "exceed rated_power_mva."
                )

        return self

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def generation(
        cls,
        *,
        active_power_mw: float,
        reactive_power_mvar: float = 0.0,
        **kwargs,
    ) -> Self:
        """
        Create a conventional generating unit.

        Parameters
        ----------
        active_power_mw
            Non-negative active-power generation in MW.

        reactive_power_mvar
            Reactive-power exchange in MVAr.

            Positive values represent reactive-power injection.
            Negative values represent reactive-power absorption.

        **kwargs
            Additional Generator fields.

        Returns
        -------
        Generator
            Configured generator.
        """

        if active_power_mw < 0.0:
            raise ValueError(
                "Generator.generation() expects non-negative "
                "active_power_mw."
            )

        return cls(
            active_power_mw=active_power_mw,
            reactive_power_mvar=reactive_power_mvar,
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Generation Properties
    # ------------------------------------------------------------------

    @property
    def active_generation_mw(self) -> float:
        """
        Return scaled active-power generation.
        """

        return max(
            0.0,
            self.effective_active_power_mw,
        )

    @property
    def reactive_generation_mvar(self) -> float:
        """
        Return scaled reactive-power injection.

        Negative values indicate reactive-power absorption.
        """

        return self.effective_reactive_power_mvar

    @property
    def apparent_generation_mva(self) -> float:
        """
        Return apparent-power magnitude at the current setpoint.
        """

        return abs(
            complex(
                self.active_generation_mw,
                self.reactive_generation_mvar,
            )
        )

    # ------------------------------------------------------------------
    # Limit Properties
    # ------------------------------------------------------------------

    @property
    def has_active_power_limit(self) -> bool:
        """
        Return whether a maximum active-power limit exists.
        """

        return self.maximum_active_power_mw is not None

    @property
    def has_reactive_power_limits(self) -> bool:
        """
        Return whether both reactive-power limits are defined.
        """

        return (
            self.minimum_reactive_power_mvar is not None
            and self.maximum_reactive_power_mvar is not None
        )

    @property
    def has_rating(self) -> bool:
        """
        Return whether an apparent-power rating is defined.
        """

        return self.rated_power_mva is not None

    @property
    def is_voltage_controlled(self) -> bool:
        """
        Return whether voltage regulation is enabled.
        """

        return (
            self.voltage_control_enabled
            and self.voltage_setpoint_pu is not None
        )

    # ------------------------------------------------------------------
    # Utilization
    # ------------------------------------------------------------------

    @property
    def apparent_power_utilization(self) -> float | None:
        """
        Return apparent-power utilization as a fraction of rating.

        Returns
        -------
        float | None
            Apparent-power utilization when rated_power_mva is
            defined, otherwise None.
        """

        if self.rated_power_mva is None:
            return None

        return (
            self.apparent_generation_mva
            / self.rated_power_mva
        )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Generator",
]