"""
GridStudio AI

Module:
    battery.py

Description:
    Defines the battery energy storage system (BESS) model used
    throughout GridStudio AI.

    Battery represents a bidirectional electrical energy-storage
    resource connected to the network through a power-electronic
    converter.

    The model stores energy capacity, state of charge, charging and
    discharging limits, efficiencies, inverter capability, and basic
    operating constraints while remaining independent of dispatch
    algorithms, optimization methods, time-series engines,
    pandapower, and OpenDSS.

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
# Battery
# ============================================================================


class Battery(Injection):
    """
    Battery energy storage system.

    Battery specializes Injection because it may either inject active
    power into the network or absorb active power from the network.

    Sign Convention
    ---------------
    GridStudio AI uses the canonical network-injection convention:

    * positive active power = discharge into the network,
    * negative active power = charging from the network,
    * zero active power = electrically idle,
    * positive reactive power = reactive-power injection,
    * negative reactive power = reactive-power absorption.

    Therefore:

        active_power_mw > 0
            battery is discharging

        active_power_mw < 0
            battery is charging

        active_power_mw == 0
            battery has no active-power exchange

    Energy State
    ------------
    ``energy_capacity_mwh`` represents the nominal usable energy
    capacity represented by this model.

    ``state_of_charge`` is represented as a fraction in the range
    0..1.

    Operational SOC limits may further restrict the usable range:

        minimum_state_of_charge
        maximum_state_of_charge

    Converter
    ---------
    ``rated_power_mva`` represents the apparent-power capability of
    the battery inverter/converter.

    The converter may exchange reactive power while charging,
    discharging, or potentially while active-power output is zero,
    depending on the future control model.

    Time-Series Operation
    ---------------------
    Battery SOC evolves with time and therefore requires sequential
    simulation.

    The domain model stores the current/base SOC and equipment
    constraints. Future time-series services should calculate SOC
    transitions between simulation intervals.

    Notes
    -----
    This model intentionally does not contain:

    * electricity prices,
    * optimization objectives,
    * dispatch schedules,
    * forecast data,
    * degradation models,
    * cycle-counting algorithms,
    * control policies.

    Those belong in dedicated forecasting, control, optimization,
    and time-series layers.
    """

    # ------------------------------------------------------------------
    # Electrical Connection
    # ------------------------------------------------------------------

    connection: ElectricalConnection = Field(
        default=GROUNDED_WYE,
        description=(
            "Electrical connection configuration of the battery "
            "converter."
        ),
    )

    # ------------------------------------------------------------------
    # Energy Capacity
    # ------------------------------------------------------------------

    energy_capacity_mwh: float = Field(
        ...,
        gt=0.0,
        description=(
            "Nominal usable energy capacity of the battery in MWh."
        ),
    )

    # ------------------------------------------------------------------
    # State of Charge
    # ------------------------------------------------------------------

    state_of_charge: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description=(
            "Current/base battery state of charge as a fraction "
            "from 0 to 1."
        ),
    )

    minimum_state_of_charge: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description=(
            "Minimum permitted operating state of charge."
        ),
    )

    maximum_state_of_charge: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description=(
            "Maximum permitted operating state of charge."
        ),
    )

    # ------------------------------------------------------------------
    # Active-Power Limits
    # ------------------------------------------------------------------

    maximum_charge_power_mw: float = Field(
        ...,
        gt=0.0,
        description=(
            "Maximum active power that may be absorbed from the "
            "network while charging, expressed as a positive "
            "magnitude in MW."
        ),
    )

    maximum_discharge_power_mw: float = Field(
        ...,
        gt=0.0,
        description=(
            "Maximum active power that may be injected into the "
            "network while discharging, in MW."
        ),
    )

    # ------------------------------------------------------------------
    # Efficiency
    # ------------------------------------------------------------------

    charge_efficiency: float = Field(
        default=0.95,
        gt=0.0,
        le=1.0,
        description=(
            "Charging efficiency expressed as a fraction."
        ),
    )

    discharge_efficiency: float = Field(
        default=0.95,
        gt=0.0,
        le=1.0,
        description=(
            "Discharging efficiency expressed as a fraction."
        ),
    )

    # ------------------------------------------------------------------
    # Converter Rating
    # ------------------------------------------------------------------

    rated_power_mva: float | None = Field(
        default=None,
        gt=0.0,
        description=(
            "Optional apparent-power rating of the battery "
            "converter in MVA."
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

    reactive_power_control_enabled: bool = Field(
        default=False,
        description=(
            "Whether reactive-power control through the battery "
            "converter is enabled."
        ),
    )

    # ------------------------------------------------------------------
    # Operating Capability
    # ------------------------------------------------------------------

    charging_enabled: bool = Field(
        default=True,
        description=(
            "Whether battery charging is currently permitted."
        ),
    )

    discharging_enabled: bool = Field(
        default=True,
        description=(
            "Whether battery discharging is currently permitted."
        ),
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def _validate_battery_configuration(
        self,
    ) -> Self:
        """
        Validate battery configuration and operating setpoint.
        """

        if (
            self.minimum_state_of_charge
            >= self.maximum_state_of_charge
        ):
            raise ValueError(
                "minimum_state_of_charge must be less than "
                "maximum_state_of_charge."
            )

        if (
            self.state_of_charge
            < self.minimum_state_of_charge
            or self.state_of_charge
            > self.maximum_state_of_charge
        ):
            raise ValueError(
                "state_of_charge must lie between "
                "minimum_state_of_charge and "
                "maximum_state_of_charge."
            )

        if (
            self.active_power_mw
            < -self.maximum_charge_power_mw
        ):
            raise ValueError(
                "Charging active_power_mw exceeds "
                "maximum_charge_power_mw."
            )

        if (
            self.active_power_mw
            > self.maximum_discharge_power_mw
        ):
            raise ValueError(
                "Discharging active_power_mw exceeds "
                "maximum_discharge_power_mw."
            )

        if (
            self.active_power_mw < 0.0
            and not self.charging_enabled
        ):
            raise ValueError(
                "Battery cannot have a charging setpoint when "
                "charging_enabled is False."
            )

        if (
            self.active_power_mw > 0.0
            and not self.discharging_enabled
        ):
            raise ValueError(
                "Battery cannot have a discharging setpoint when "
                "discharging_enabled is False."
            )

        if (
            self.state_of_charge
            <= self.minimum_state_of_charge
            and self.active_power_mw > 0.0
        ):
            raise ValueError(
                "Battery cannot discharge at or below "
                "minimum_state_of_charge."
            )

        if (
            self.state_of_charge
            >= self.maximum_state_of_charge
            and self.active_power_mw < 0.0
        ):
            raise ValueError(
                "Battery cannot charge at or above "
                "maximum_state_of_charge."
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
            self.reactive_power_control_enabled
            and self.rated_power_mva is None
        ):
            raise ValueError(
                "rated_power_mva is required when "
                "reactive_power_control_enabled is True."
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
                    "Battery operating apparent power cannot "
                    "exceed rated_power_mva."
                )

            if (
                self.maximum_charge_power_mw
                > self.rated_power_mva
            ):
                raise ValueError(
                    "maximum_charge_power_mw cannot exceed "
                    "rated_power_mva."
                )

            if (
                self.maximum_discharge_power_mw
                > self.rated_power_mva
            ):
                raise ValueError(
                    "maximum_discharge_power_mw cannot exceed "
                    "rated_power_mva."
                )

        return self

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def storage(
        cls,
        *,
        energy_capacity_mwh: float,
        maximum_charge_power_mw: float,
        maximum_discharge_power_mw: float,
        state_of_charge: float = 0.5,
        active_power_mw: float = 0.0,
        reactive_power_mvar: float = 0.0,
        rated_power_mva: float | None = None,
        **kwargs,
    ) -> Self:
        """
        Create a battery energy-storage resource.

        Parameters
        ----------
        energy_capacity_mwh
            Nominal usable battery energy capacity in MWh.

        maximum_charge_power_mw
            Maximum charging-power magnitude in MW.

        maximum_discharge_power_mw
            Maximum discharging power in MW.

        state_of_charge
            Initial/base SOC as a fraction from 0 to 1.

        active_power_mw
            Initial active-power setpoint.

            Positive means discharge.
            Negative means charge.

        reactive_power_mvar
            Initial reactive-power setpoint.

        rated_power_mva
            Optional battery-converter apparent-power rating.

        **kwargs
            Additional Battery fields.

        Returns
        -------
        Battery
            Configured battery energy-storage system.
        """

        return cls(
            energy_capacity_mwh=energy_capacity_mwh,
            maximum_charge_power_mw=maximum_charge_power_mw,
            maximum_discharge_power_mw=(
                maximum_discharge_power_mw
            ),
            state_of_charge=state_of_charge,
            active_power_mw=active_power_mw,
            reactive_power_mvar=reactive_power_mvar,
            rated_power_mva=rated_power_mva,
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Operating Mode
    # ------------------------------------------------------------------

    @property
    def is_charging(self) -> bool:
        """
        Return whether the battery is currently charging.
        """

        return self.effective_active_power_mw < 0.0

    @property
    def is_discharging(self) -> bool:
        """
        Return whether the battery is currently discharging.
        """

        return self.effective_active_power_mw > 0.0

    @property
    def is_idle(self) -> bool:
        """
        Return whether the battery has zero active-power exchange.
        """

        return self.effective_active_power_mw == 0.0

    # ------------------------------------------------------------------
    # Power Properties
    # ------------------------------------------------------------------

    @property
    def charging_power_mw(self) -> float:
        """
        Return positive charging-power magnitude in MW.
        """

        return max(
            0.0,
            -self.effective_active_power_mw,
        )

    @property
    def discharging_power_mw(self) -> float:
        """
        Return positive discharging-power magnitude in MW.
        """

        return max(
            0.0,
            self.effective_active_power_mw,
        )

    @property
    def apparent_power_mva(self) -> float:
        """
        Return configured apparent-power magnitude.
        """

        return abs(
            complex(
                self.effective_active_power_mw,
                self.effective_reactive_power_mvar,
            )
        )

    # ------------------------------------------------------------------
    # Energy Properties
    # ------------------------------------------------------------------

    @property
    def stored_energy_mwh(self) -> float:
        """
        Return energy currently stored in the battery.
        """

        return (
            self.energy_capacity_mwh
            * self.state_of_charge
        )

    @property
    def minimum_stored_energy_mwh(self) -> float:
        """
        Return minimum permitted stored energy.
        """

        return (
            self.energy_capacity_mwh
            * self.minimum_state_of_charge
        )

    @property
    def maximum_stored_energy_mwh(self) -> float:
        """
        Return maximum permitted stored energy.
        """

        return (
            self.energy_capacity_mwh
            * self.maximum_state_of_charge
        )

    @property
    def available_discharge_energy_mwh(self) -> float:
        """
        Return stored energy available above minimum SOC.

        This is battery-side stored energy before discharge losses.
        """

        return max(
            0.0,
            (
                self.stored_energy_mwh
                - self.minimum_stored_energy_mwh
            ),
        )

    @property
    def available_charge_capacity_mwh(self) -> float:
        """
        Return remaining battery-side energy capacity before
        maximum SOC is reached.
        """

        return max(
            0.0,
            (
                self.maximum_stored_energy_mwh
                - self.stored_energy_mwh
            ),
        )

    # ------------------------------------------------------------------
    # Efficiency Properties
    # ------------------------------------------------------------------

    @property
    def round_trip_efficiency(self) -> float:
        """
        Return charge-discharge round-trip efficiency.
        """

        return (
            self.charge_efficiency
            * self.discharge_efficiency
        )

    # ------------------------------------------------------------------
    # Converter Capability
    # ------------------------------------------------------------------

    @property
    def reactive_capability_mvar(
        self,
    ) -> float | None:
        """
        Return theoretical symmetric reactive-power capability at
        the current active-power setpoint.

        Returns
        -------
        float | None
            Reactive capability magnitude in MVAr when converter
            rating is defined.

        Notes
        -----
        The calculation uses the simplified converter capability
        circle:

            |Q|max = sqrt(Srated^2 - P^2)

        Explicit reactive limits may impose tighter restrictions.
        """

        if self.rated_power_mva is None:
            return None

        active_power = abs(
            self.effective_active_power_mw
        )

        if active_power >= self.rated_power_mva:
            return 0.0

        capability = (
            (
                self.rated_power_mva**2
                - active_power**2
            )
            ** 0.5
        )

        if self.maximum_reactive_power_mvar is not None:
            capability = min(
                capability,
                self.maximum_reactive_power_mvar,
            )

        if self.minimum_reactive_power_mvar is not None:
            capability = min(
                capability,
                abs(self.minimum_reactive_power_mvar),
            )

        return capability

    @property
    def converter_utilization(self) -> float | None:
        """
        Return apparent-power utilization of the converter.
        """

        if self.rated_power_mva is None:
            return None

        return (
            self.apparent_power_mva
            / self.rated_power_mva
        )

    # ------------------------------------------------------------------
    # SOC Capability
    # ------------------------------------------------------------------

    @property
    def can_charge(self) -> bool:
        """
        Return whether charging is presently possible.
        """

        return (
            self.charging_enabled
            and self.state_of_charge
            < self.maximum_state_of_charge
        )

    @property
    def can_discharge(self) -> bool:
        """
        Return whether discharging is presently possible.
        """

        return (
            self.discharging_enabled
            and self.state_of_charge
            > self.minimum_state_of_charge
        )

    # ------------------------------------------------------------------
    # Time-Step Energy Calculation
    # ------------------------------------------------------------------

    def projected_state_of_charge(
        self,
        duration_hours: float,
    ) -> float:
        """
        Estimate SOC after maintaining the current active-power
        setpoint for a specified duration.

        Parameters
        ----------
        duration_hours
            Duration of the interval in hours.

        Returns
        -------
        float
            Projected battery state of charge.

        Notes
        -----
        Positive active power represents discharge:

            energy_removed =
                P_discharge * duration / discharge_efficiency

        Negative active power represents charge:

            energy_added =
                P_charge * duration * charge_efficiency

        This method does not mutate the Battery object. It provides
        a deterministic calculation that may later be used by the
        time-series simulation layer.
        """

        if duration_hours < 0.0:
            raise ValueError(
                "duration_hours cannot be negative."
            )

        stored_energy = self.stored_energy_mwh

        if self.is_charging:
            stored_energy += (
                self.charging_power_mw
                * duration_hours
                * self.charge_efficiency
            )

        elif self.is_discharging:
            stored_energy -= (
                self.discharging_power_mw
                * duration_hours
                / self.discharge_efficiency
            )

        return (
            stored_energy
            / self.energy_capacity_mwh
        )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Battery",
]