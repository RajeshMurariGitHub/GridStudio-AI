"""
GridStudio AI

Module:
    ev.py

Description:
    Defines the electric vehicle (EV) model used throughout
    GridStudio AI.

    EV represents an electric vehicle connected to the electrical
    network through charging equipment.

    The model supports conventional grid-to-vehicle charging and
    optional vehicle-to-grid (V2G) operation while remaining
    independent of mobility schedules, charging optimization,
    forecasting, time-series profiles, pandapower, and OpenDSS.

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
# EV
# ============================================================================


class EV(Injection):
    """
    Electric vehicle connected to the electrical network.

    EV specializes Injection because an electric vehicle may either
    absorb active power while charging or inject active power during
    vehicle-to-grid operation.

    Sign Convention
    ---------------
    GridStudio AI uses the canonical network-injection convention:

    * negative active power = EV charging from the grid,
    * positive active power = EV discharging into the grid through
      vehicle-to-grid operation,
    * zero active power = no active-power exchange,
    * positive reactive power = reactive-power injection,
    * negative reactive power = reactive-power absorption.

    Therefore:

        active_power_mw < 0
            charging

        active_power_mw > 0
            V2G discharge

        active_power_mw == 0
            electrically idle

    Grid Connection
    ---------------
    An EV may exchange electrical power only while connected to its
    charging equipment.

    ``is_connected`` represents the current/base connection state.

    Future mobility and charging profiles should update connection
    state through time-series state/dispatch models rather than
    storing complete arrival/departure schedules inside this entity.

    Energy State
    ------------
    ``battery_capacity_mwh`` represents vehicle battery energy
    capacity.

    ``state_of_charge`` represents current/base SOC as a fraction
    between 0 and 1.

    Operational SOC limits may restrict charging and V2G operation.

    Charger
    -------
    Charging and discharging power limits describe the grid-side
    charger/converter capability.

    V2G operation is explicitly controlled by ``v2g_enabled``.

    Notes
    -----
    This domain model intentionally does not contain:

    * arrival/departure schedules,
    * trip schedules,
    * driving distance,
    * transportation routing,
    * charging tariffs,
    * charging optimization objectives,
    * fleet aggregation,
    * charging-station queues,
    * forecast models.

    Those belong in future mobility, time-series, forecasting, and
    optimization layers.
    """

    # ------------------------------------------------------------------
    # Electrical Connection
    # ------------------------------------------------------------------

    connection: ElectricalConnection = Field(
        default=GROUNDED_WYE,
        description=(
            "Electrical connection configuration of the EV charger."
        ),
    )

    # ------------------------------------------------------------------
    # Vehicle Battery
    # ------------------------------------------------------------------

    battery_capacity_mwh: float = Field(
        ...,
        gt=0.0,
        description=(
            "Usable electric-vehicle battery capacity in MWh."
        ),
    )

    state_of_charge: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description=(
            "Current/base vehicle battery state of charge as a "
            "fraction from 0 to 1."
        ),
    )

    minimum_state_of_charge: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description=(
            "Minimum permitted EV battery state of charge."
        ),
    )

    maximum_state_of_charge: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description=(
            "Maximum permitted EV battery state of charge."
        ),
    )

    # ------------------------------------------------------------------
    # Charger Power Limits
    # ------------------------------------------------------------------

    maximum_charge_power_mw: float = Field(
        ...,
        gt=0.0,
        description=(
            "Maximum grid-to-vehicle charging-power magnitude "
            "in MW."
        ),
    )

    maximum_discharge_power_mw: float = Field(
        default=0.0,
        ge=0.0,
        description=(
            "Maximum vehicle-to-grid active-power discharge "
            "in MW."
        ),
    )

    # ------------------------------------------------------------------
    # Charger / Converter Rating
    # ------------------------------------------------------------------

    rated_power_mva: float | None = Field(
        default=None,
        gt=0.0,
        description=(
            "Optional apparent-power rating of the EV charger "
            "or bidirectional converter in MVA."
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
            "Grid-to-battery charging efficiency."
        ),
    )

    discharge_efficiency: float = Field(
        default=0.95,
        gt=0.0,
        le=1.0,
        description=(
            "Battery-to-grid V2G discharge efficiency."
        ),
    )

    # ------------------------------------------------------------------
    # Connection / Availability
    # ------------------------------------------------------------------

    is_connected: bool = Field(
        default=True,
        description=(
            "Whether the EV is currently connected to charging "
            "equipment and available for electrical exchange."
        ),
    )

    charging_enabled: bool = Field(
        default=True,
        description=(
            "Whether grid-to-vehicle charging is currently "
            "permitted."
        ),
    )

    # ------------------------------------------------------------------
    # Vehicle-to-Grid
    # ------------------------------------------------------------------

    v2g_enabled: bool = Field(
        default=False,
        description=(
            "Whether vehicle-to-grid active-power discharge is "
            "permitted."
        ),
    )

    # ------------------------------------------------------------------
    # Reactive-Power Capability
    # ------------------------------------------------------------------

    reactive_power_control_enabled: bool = Field(
        default=False,
        description=(
            "Whether charger/inverter reactive-power control "
            "is enabled."
        ),
    )

    minimum_reactive_power_mvar: float | None = Field(
        default=None,
        description=(
            "Optional minimum charger reactive-power limit "
            "in MVAr."
        ),
    )

    maximum_reactive_power_mvar: float | None = Field(
        default=None,
        description=(
            "Optional maximum charger reactive-power limit "
            "in MVAr."
        ),
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def _validate_ev_configuration(
        self,
    ) -> Self:
        """
        Validate EV battery, charger, and operating configuration.
        """

        if (
            self.minimum_state_of_charge
            >= self.maximum_state_of_charge
        ):
            raise ValueError(
                "minimum_state_of_charge must be less than "
                "maximum_state_of_charge."
            )

        if not (
            self.minimum_state_of_charge
            <= self.state_of_charge
            <= self.maximum_state_of_charge
        ):
            raise ValueError(
                "state_of_charge must lie between "
                "minimum_state_of_charge and "
                "maximum_state_of_charge."
            )

        if not self.is_connected:
            if (
                self.active_power_mw != 0.0
                or self.reactive_power_mvar != 0.0
            ):
                raise ValueError(
                    "A disconnected EV cannot exchange active "
                    "or reactive power with the network."
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
                "V2G active_power_mw exceeds "
                "maximum_discharge_power_mw."
            )

        if (
            self.active_power_mw < 0.0
            and not self.charging_enabled
        ):
            raise ValueError(
                "EV cannot have a charging setpoint when "
                "charging_enabled is False."
            )

        if (
            self.active_power_mw > 0.0
            and not self.v2g_enabled
        ):
            raise ValueError(
                "Positive active_power_mw requires "
                "v2g_enabled to be True."
            )

        if (
            self.maximum_discharge_power_mw > 0.0
            and not self.v2g_enabled
        ):
            raise ValueError(
                "maximum_discharge_power_mw must be zero when "
                "v2g_enabled is False."
            )

        if (
            self.state_of_charge
            <= self.minimum_state_of_charge
            and self.active_power_mw > 0.0
        ):
            raise ValueError(
                "EV cannot perform V2G discharge at or below "
                "minimum_state_of_charge."
            )

        if (
            self.state_of_charge
            >= self.maximum_state_of_charge
            and self.active_power_mw < 0.0
        ):
            raise ValueError(
                "EV cannot charge at or above "
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
                    "EV operating apparent power cannot exceed "
                    "rated_power_mva."
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
    def charger(
        cls,
        *,
        battery_capacity_mwh: float,
        maximum_charge_power_mw: float,
        state_of_charge: float = 0.5,
        active_power_mw: float = 0.0,
        rated_power_mva: float | None = None,
        **kwargs,
    ) -> Self:
        """
        Create a conventional unidirectional EV charger.

        Parameters
        ----------
        battery_capacity_mwh
            Vehicle battery capacity in MWh.

        maximum_charge_power_mw
            Maximum charging-power magnitude in MW.

        state_of_charge
            Initial/base vehicle SOC.

        active_power_mw
            Initial EV active-power setpoint.

            This should normally be zero or negative because this
            constructor creates a non-V2G EV.

        rated_power_mva
            Optional charger apparent-power rating.

        **kwargs
            Additional EV fields.

        Returns
        -------
        EV
            Configured electric vehicle.
        """

        if active_power_mw > 0.0:
            raise ValueError(
                "EV.charger() does not support positive active "
                "power. Use EV.bidirectional() for V2G operation."
            )

        return cls(
            battery_capacity_mwh=battery_capacity_mwh,
            maximum_charge_power_mw=maximum_charge_power_mw,
            maximum_discharge_power_mw=0.0,
            state_of_charge=state_of_charge,
            active_power_mw=active_power_mw,
            rated_power_mva=rated_power_mva,
            v2g_enabled=False,
            **kwargs,
        )

    @classmethod
    def bidirectional(
        cls,
        *,
        battery_capacity_mwh: float,
        maximum_charge_power_mw: float,
        maximum_discharge_power_mw: float,
        state_of_charge: float = 0.5,
        active_power_mw: float = 0.0,
        reactive_power_mvar: float = 0.0,
        rated_power_mva: float | None = None,
        **kwargs,
    ) -> Self:
        """
        Create a bidirectional V2G-capable electric vehicle.
        """

        if maximum_discharge_power_mw <= 0.0:
            raise ValueError(
                "EV.bidirectional() requires "
                "maximum_discharge_power_mw greater than zero."
            )

        return cls(
            battery_capacity_mwh=battery_capacity_mwh,
            maximum_charge_power_mw=maximum_charge_power_mw,
            maximum_discharge_power_mw=(
                maximum_discharge_power_mw
            ),
            state_of_charge=state_of_charge,
            active_power_mw=active_power_mw,
            reactive_power_mvar=reactive_power_mvar,
            rated_power_mva=rated_power_mva,
            v2g_enabled=True,
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Operating Mode
    # ------------------------------------------------------------------

    @property
    def is_charging(self) -> bool:
        """
        Return whether the EV is currently charging.
        """

        return (
            self.is_connected
            and self.effective_active_power_mw < 0.0
        )

    @property
    def is_discharging(self) -> bool:
        """
        Return whether the EV is currently performing V2G discharge.
        """

        return (
            self.is_connected
            and self.effective_active_power_mw > 0.0
        )

    @property
    def is_idle(self) -> bool:
        """
        Return whether the EV has zero active-power exchange.
        """

        return (
            not self.is_connected
            or self.effective_active_power_mw == 0.0
        )

    # ------------------------------------------------------------------
    # Power Properties
    # ------------------------------------------------------------------

    @property
    def charging_power_mw(self) -> float:
        """
        Return positive charging-power magnitude.
        """

        if not self.is_connected:
            return 0.0

        return max(
            0.0,
            -self.effective_active_power_mw,
        )

    @property
    def discharging_power_mw(self) -> float:
        """
        Return positive V2G discharging-power magnitude.
        """

        if not self.is_connected:
            return 0.0

        return max(
            0.0,
            self.effective_active_power_mw,
        )

    @property
    def apparent_power_mva(self) -> float:
        """
        Return charger apparent-power magnitude.
        """

        if not self.is_connected:
            return 0.0

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
        Return current vehicle battery stored energy.
        """

        return (
            self.battery_capacity_mwh
            * self.state_of_charge
        )

    @property
    def minimum_stored_energy_mwh(self) -> float:
        """
        Return minimum permitted stored energy.
        """

        return (
            self.battery_capacity_mwh
            * self.minimum_state_of_charge
        )

    @property
    def maximum_stored_energy_mwh(self) -> float:
        """
        Return maximum permitted stored energy.
        """

        return (
            self.battery_capacity_mwh
            * self.maximum_state_of_charge
        )

    @property
    def available_v2g_energy_mwh(self) -> float:
        """
        Return battery-side energy available above minimum SOC.

        This value is before V2G discharge losses.
        """

        if not self.v2g_enabled:
            return 0.0

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
        Return remaining battery-side charging capacity.
        """

        return max(
            0.0,
            (
                self.maximum_stored_energy_mwh
                - self.stored_energy_mwh
            ),
        )

    # ------------------------------------------------------------------
    # Capability Properties
    # ------------------------------------------------------------------

    @property
    def can_charge(self) -> bool:
        """
        Return whether the EV can currently charge.
        """

        return (
            self.is_connected
            and self.charging_enabled
            and self.state_of_charge
            < self.maximum_state_of_charge
        )

    @property
    def can_discharge(self) -> bool:
        """
        Return whether the EV can currently provide V2G power.
        """

        return (
            self.is_connected
            and self.v2g_enabled
            and self.maximum_discharge_power_mw > 0.0
            and self.state_of_charge
            > self.minimum_state_of_charge
        )

    @property
    def supports_v2g(self) -> bool:
        """
        Return whether vehicle-to-grid operation is configured.
        """

        return (
            self.v2g_enabled
            and self.maximum_discharge_power_mw > 0.0
        )

    @property
    def supports_reactive_power_control(self) -> bool:
        """
        Return whether charger reactive-power control is enabled.
        """

        return (
            self.is_connected
            and self.reactive_power_control_enabled
            and self.rated_power_mva is not None
        )

    # ------------------------------------------------------------------
    # Converter Capability
    # ------------------------------------------------------------------

    @property
    def reactive_capability_mvar(
        self,
    ) -> float | None:
        """
        Return theoretical symmetric reactive-power capability.

        The simplified capability is determined from:

            |Q|max = sqrt(Srated^2 - P^2)

        Explicit reactive-power limits may impose tighter bounds.
        """

        if (
            not self.is_connected
            or self.rated_power_mva is None
        ):
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
    def charger_utilization(self) -> float | None:
        """
        Return charger apparent-power utilization.
        """

        if self.rated_power_mva is None:
            return None

        return (
            self.apparent_power_mva
            / self.rated_power_mva
        )

    # ------------------------------------------------------------------
    # Efficiency
    # ------------------------------------------------------------------

    @property
    def round_trip_efficiency(self) -> float:
        """
        Return charging/V2G round-trip efficiency.
        """

        return (
            self.charge_efficiency
            * self.discharge_efficiency
        )

    # ------------------------------------------------------------------
    # Time-Step Energy Calculation
    # ------------------------------------------------------------------

    def projected_state_of_charge(
        self,
        duration_hours: float,
    ) -> float:
        """
        Estimate SOC after maintaining the current electrical
        setpoint for a specified duration.

        Parameters
        ----------
        duration_hours
            Duration of the interval in hours.

        Returns
        -------
        float
            Projected EV battery state of charge.

        Notes
        -----
        This method does not account for driving energy consumption.

        Driving-energy transitions belong in the future EV mobility
        state model.

        This method does not mutate the EV object.
        """

        if duration_hours < 0.0:
            raise ValueError(
                "duration_hours cannot be negative."
            )

        stored_energy = self.stored_energy_mwh

        if not self.is_connected:
            return self.state_of_charge

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
            / self.battery_capacity_mwh
        )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "EV",
]