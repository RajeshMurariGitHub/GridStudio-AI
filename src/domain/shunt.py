"""
GridStudio AI

Module:
    shunt.py

Description:
    Defines the electrical shunt model used throughout GridStudio AI.

    A Shunt represents bus-connected reactive compensation or
    shunt-admittance equipment such as capacitor banks and reactors.

    The model is solver-independent and supports both balanced and
    unbalanced electrical networks.

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
# Shunt
# ============================================================================


class Shunt(Injection):
    """
    Electrical shunt connected to a network node.

    A Shunt represents equipment whose principal purpose is to
    exchange reactive power with the network through a shunt
    electrical connection.

    Typical equipment includes:

    * capacitor banks,
    * shunt reactors,
    * fixed reactive compensation,
    * switched capacitor/reactor banks.

    Sign Convention
    ---------------
    GridStudio AI uses the network-injection convention inherited
    from Injection:

    * positive Q = reactive-power injection,
    * negative Q = reactive-power absorption.

    Therefore:

        capacitor bank:
            reactive_power_mvar > 0

        shunt reactor:
            reactive_power_mvar < 0

    ``reactive_power_mvar`` represents the shunt reactive-power
    rating at nominal voltage.

    Physical Shunt Behavior
    -----------------------
    A physical shunt behaves approximately as constant admittance.

    Consequently, its reactive-power exchange varies approximately
    with the square of voltage magnitude:

        Q(V) = Q_nominal * V_pu^2

    The actual solved reactive-power exchange belongs in ShuntState
    or the corresponding simulation result.

    Notes
    -----
    Shunt inherits ``active_power_mw`` from Injection. It is normally
    zero, but a small non-zero value may represent active losses when
    required.

    Engine adapters are responsible for translating this canonical
    representation to pandapower, OpenDSS, or another backend.
    """

    # ------------------------------------------------------------------
    # Electrical Connection
    # ------------------------------------------------------------------

    connection: ElectricalConnection = Field(
        default=GROUNDED_WYE,
        description=(
            "Electrical connection configuration of the shunt."
        ),
    )

    # ------------------------------------------------------------------
    # Nominal Voltage
    # ------------------------------------------------------------------

    nominal_voltage_kv: float | None = Field(
        default=None,
        gt=0.0,
        description=(
            "Optional nominal line-to-line voltage at which the "
            "shunt reactive-power rating is specified."
        ),
    )

    # ------------------------------------------------------------------
    # Switching / Steps
    # ------------------------------------------------------------------

    step_count: int = Field(
        default=1,
        ge=1,
        description=(
            "Total number of equal reactive-power steps available "
            "in the shunt bank."
        ),
    )

    active_steps: int = Field(
        default=1,
        ge=0,
        description=(
            "Number of currently energized shunt-bank steps."
        ),
    )

    # ------------------------------------------------------------------
    # Control Capability
    # ------------------------------------------------------------------

    remotely_controllable: bool = Field(
        default=False,
        description=(
            "Whether the shunt switching state may be controlled "
            "remotely."
        ),
    )

    automatic_control_enabled: bool = Field(
        default=False,
        description=(
            "Whether automatic shunt switching control is enabled."
        ),
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def _validate_shunt_configuration(
        self,
    ) -> Self:
        """
        Validate shunt configuration.
        """

        if self.active_steps > self.step_count:
            raise ValueError(
                "active_steps cannot exceed step_count."
            )

        if (
            self.automatic_control_enabled
            and not self.remotely_controllable
        ):
            raise ValueError(
                "automatic_control_enabled requires "
                "remotely_controllable to be True."
            )

        return self

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def capacitor_bank(
        cls,
        *,
        reactive_power_mvar: float,
        step_count: int = 1,
        active_steps: int | None = None,
        **kwargs,
    ) -> Self:
        """
        Create a capacitor-bank shunt.

        Parameters
        ----------
        reactive_power_mvar
            Positive total reactive-power rating of the bank
            at nominal voltage.

        step_count
            Number of equal capacitor-bank steps.

        active_steps
            Number of initially energized steps. When omitted,
            all steps are energized.

        **kwargs
            Additional Shunt fields.

        Returns
        -------
        Shunt
            Configured capacitor bank.
        """

        if reactive_power_mvar < 0.0:
            raise ValueError(
                "Shunt.capacitor_bank() expects non-negative "
                "reactive_power_mvar."
            )

        if active_steps is None:
            active_steps = step_count

        return cls(
            active_power_mw=0.0,
            reactive_power_mvar=reactive_power_mvar,
            step_count=step_count,
            active_steps=active_steps,
            **kwargs,
        )

    @classmethod
    def reactor(
        cls,
        *,
        reactive_power_mvar: float,
        step_count: int = 1,
        active_steps: int | None = None,
        **kwargs,
    ) -> Self:
        """
        Create a shunt reactor.

        Parameters
        ----------
        reactive_power_mvar
            Positive magnitude of the reactor reactive-power
            absorption at nominal voltage.

        step_count
            Number of equal reactor steps.

        active_steps
            Number of initially energized steps. When omitted,
            all steps are energized.

        **kwargs
            Additional Shunt fields.

        Returns
        -------
        Shunt
            Configured shunt reactor.
        """

        if reactive_power_mvar < 0.0:
            raise ValueError(
                "Shunt.reactor() expects a non-negative reactive "
                "power magnitude."
            )

        if active_steps is None:
            active_steps = step_count

        return cls(
            active_power_mw=0.0,
            reactive_power_mvar=-reactive_power_mvar,
            step_count=step_count,
            active_steps=active_steps,
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Step Properties
    # ------------------------------------------------------------------

    @property
    def energized_fraction(self) -> float:
        """
        Return fraction of the shunt bank currently energized.
        """

        return (
            self.active_steps
            / self.step_count
        )

    @property
    def reactive_power_per_step_mvar(self) -> float:
        """
        Return rated reactive power of one shunt step.

        The value uses GridStudio's network-injection sign
        convention.
        """

        return (
            self.reactive_power_mvar
            / self.step_count
        )

    @property
    def configured_reactive_power_mvar(self) -> float:
        """
        Return reactive-power rating of currently energized steps
        at nominal voltage.

        Scaling inherited from Injection is included.
        """

        return (
            self.reactive_power_per_step_mvar
            * self.active_steps
            * self.scaling
        )

    # ------------------------------------------------------------------
    # Voltage-Dependent Behavior
    # ------------------------------------------------------------------

    def reactive_power_at_voltage_mvar(
        self,
        voltage_pu: float,
    ) -> float:
        """
        Estimate shunt reactive-power exchange at a given voltage.

        Parameters
        ----------
        voltage_pu
            Voltage magnitude in per unit.

        Returns
        -------
        float
            Reactive-power exchange in MVAr using the GridStudio
            network-injection sign convention.

        Notes
        -----
        The calculation assumes constant shunt admittance:

            Q = Q_nominal * V_pu^2
        """

        if voltage_pu < 0.0:
            raise ValueError(
                "voltage_pu cannot be negative."
            )

        return (
            self.configured_reactive_power_mvar
            * voltage_pu**2
        )

    # ------------------------------------------------------------------
    # Equipment Properties
    # ------------------------------------------------------------------

    @property
    def is_capacitive(self) -> bool:
        """
        Return whether the shunt supplies reactive power.
        """

        return self.reactive_power_mvar > 0.0

    @property
    def is_inductive(self) -> bool:
        """
        Return whether the shunt absorbs reactive power.
        """

        return self.reactive_power_mvar < 0.0

    @property
    def is_energized(self) -> bool:
        """
        Return whether at least one shunt step is energized.
        """

        return self.active_steps > 0

    @property
    def is_fully_energized(self) -> bool:
        """
        Return whether all available shunt steps are energized.
        """

        return self.active_steps == self.step_count

    @property
    def is_switched_bank(self) -> bool:
        """
        Return whether the shunt contains multiple switching steps.
        """

        return self.step_count > 1

    @property
    def supports_automatic_control(self) -> bool:
        """
        Return whether automatic shunt control is enabled.
        """

        return (
            self.remotely_controllable
            and self.automatic_control_enabled
        )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Shunt",
]