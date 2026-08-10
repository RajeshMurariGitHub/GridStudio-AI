"""
GridStudio AI

Module:
    wind.py

Description:
    Defines the wind generation model used throughout GridStudio AI.

    Wind represents a wind-turbine generator or aggregated wind
    generation plant connected to the electrical network.

    The model stores installed generation capacity, electrical
    capability, resource availability, curtailment capability, and
    basic turbine operating characteristics while remaining
    independent of wind-speed profiles, forecasting models,
    optimization algorithms, pandapower, and OpenDSS.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from typing import Self

from pydantic import Field
from pydantic import model_validator

from src.domain.generator import Generator


# ============================================================================
# Wind
# ============================================================================


class Wind(Generator):
    """
    Wind generation distributed energy resource.

    Wind specializes Generator by adding wind-resource and
    turbine-specific characteristics.

    Power Convention
    ----------------
    GridStudio AI uses the network-injection convention inherited
    from Generator:

    * positive active power = generation into the network,
    * positive reactive power = reactive-power injection,
    * negative reactive power = reactive-power absorption.

    The inherited ``active_power_mw`` and ``reactive_power_mvar``
    fields represent the configured/base electrical operating
    setpoint.

    Capacity Model
    --------------
    ``rated_active_power_mw`` represents the installed active-power
    rating of the wind resource.

    ``rated_power_mva`` inherited from Generator represents the
    electrical apparent-power capability of the generator/converter.

    For an aggregated wind farm, these ratings may represent the
    aggregate installed plant capacity.

    Resource Availability
    ---------------------
    ``available_active_power_mw`` may represent the active power
    presently available from the wind resource before curtailment.

    Wind speed itself is not stored as dynamic time-series data in
    this equipment model.

    Future operation should conceptually follow:

        wind-speed profile
               |
               v
        turbine power model
               |
               v
        available wind power
               |
               v
        controller / optimization
               |
               v
        Wind setpoint
               |
               v
        simulation engine

    Notes
    -----
    The optional cut-in, rated, and cut-out wind speeds describe
    basic turbine characteristics. They do not constitute a complete
    turbine power curve.

    Detailed power curves, air-density correction, wake losses,
    forecasting, and time-series resource models belong in dedicated
    service/model layers rather than this domain entity.
    """

    # ------------------------------------------------------------------
    # Installed Capacity
    # ------------------------------------------------------------------

    rated_active_power_mw: float = Field(
        ...,
        gt=0.0,
        description=(
            "Installed rated active-power capacity of the wind "
            "resource in MW."
        ),
    )

    # ------------------------------------------------------------------
    # Resource Availability
    # ------------------------------------------------------------------

    available_active_power_mw: float | None = Field(
        default=None,
        ge=0.0,
        description=(
            "Optional currently available active power from the "
            "wind resource in MW before curtailment."
        ),
    )

    # ------------------------------------------------------------------
    # Turbine Wind-Speed Characteristics
    # ------------------------------------------------------------------

    cut_in_wind_speed_mps: float | None = Field(
        default=None,
        ge=0.0,
        description=(
            "Optional turbine cut-in wind speed in meters per "
            "second."
        ),
    )

    rated_wind_speed_mps: float | None = Field(
        default=None,
        gt=0.0,
        description=(
            "Optional wind speed at which rated active power is "
            "reached, in meters per second."
        ),
    )

    cut_out_wind_speed_mps: float | None = Field(
        default=None,
        gt=0.0,
        description=(
            "Optional turbine cut-out wind speed in meters per "
            "second."
        ),
    )

    # ------------------------------------------------------------------
    # Curtailment
    # ------------------------------------------------------------------

    curtailment_enabled: bool = Field(
        default=True,
        description=(
            "Whether active-power curtailment is permitted."
        ),
    )

    # ------------------------------------------------------------------
    # Reactive-Power Capability
    # ------------------------------------------------------------------

    reactive_power_control_enabled: bool = Field(
        default=False,
        description=(
            "Whether reactive-power control is enabled for the "
            "wind generator or converter."
        ),
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def _validate_wind_configuration(
        self,
    ) -> Self:
        """
        Validate wind-generation configuration.
        """

        if (
            self.maximum_active_power_mw is not None
            and self.maximum_active_power_mw
            > self.rated_active_power_mw
        ):
            raise ValueError(
                "maximum_active_power_mw cannot exceed "
                "rated_active_power_mw."
            )

        if (
            self.available_active_power_mw is not None
            and self.available_active_power_mw
            > self.rated_active_power_mw
        ):
            raise ValueError(
                "available_active_power_mw cannot exceed "
                "rated_active_power_mw."
            )

        if (
            self.available_active_power_mw is not None
            and self.active_power_mw
            > self.available_active_power_mw
        ):
            raise ValueError(
                "active_power_mw cannot exceed "
                "available_active_power_mw."
            )

        if (
            not self.curtailment_enabled
            and self.available_active_power_mw is not None
            and self.active_power_mw
            < self.available_active_power_mw
        ):
            raise ValueError(
                "active_power_mw must equal "
                "available_active_power_mw when "
                "curtailment_enabled is False."
            )

        if (
            self.reactive_power_control_enabled
            and self.rated_power_mva is None
        ):
            raise ValueError(
                "rated_power_mva is required when "
                "reactive_power_control_enabled is True."
            )

        self._validate_wind_speed_configuration()

        return self

    def _validate_wind_speed_configuration(
        self,
    ) -> None:
        """
        Validate optional turbine wind-speed characteristics.
        """

        speeds = (
            self.cut_in_wind_speed_mps,
            self.rated_wind_speed_mps,
            self.cut_out_wind_speed_mps,
        )

        if all(value is None for value in speeds):
            return

        if self.cut_in_wind_speed_mps is None:
            raise ValueError(
                "cut_in_wind_speed_mps is required when turbine "
                "wind-speed characteristics are specified."
            )

        if self.rated_wind_speed_mps is None:
            raise ValueError(
                "rated_wind_speed_mps is required when turbine "
                "wind-speed characteristics are specified."
            )

        if self.cut_out_wind_speed_mps is None:
            raise ValueError(
                "cut_out_wind_speed_mps is required when turbine "
                "wind-speed characteristics are specified."
            )

        if not (
            self.cut_in_wind_speed_mps
            < self.rated_wind_speed_mps
            < self.cut_out_wind_speed_mps
        ):
            raise ValueError(
                "Wind-speed characteristics must satisfy "
                "cut_in_wind_speed_mps < rated_wind_speed_mps "
                "< cut_out_wind_speed_mps."
            )

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def turbine(
        cls,
        *,
        rated_active_power_mw: float,
        rated_power_mva: float,
        active_power_mw: float = 0.0,
        reactive_power_mvar: float = 0.0,
        available_active_power_mw: float | None = None,
        **kwargs,
    ) -> Self:
        """
        Create a wind-turbine generation resource.

        Parameters
        ----------
        rated_active_power_mw
            Installed active-power rating in MW.

        rated_power_mva
            Electrical apparent-power rating in MVA.

        active_power_mw
            Initial active-power operating setpoint in MW.

        reactive_power_mvar
            Initial reactive-power operating setpoint in MVAr.

        available_active_power_mw
            Optional active power currently available from the
            wind resource before curtailment.

        **kwargs
            Additional Wind/Generator fields.

        Returns
        -------
        Wind
            Configured wind generation resource.
        """

        if rated_active_power_mw <= 0.0:
            raise ValueError(
                "rated_active_power_mw must be greater than zero."
            )

        if rated_power_mva <= 0.0:
            raise ValueError(
                "rated_power_mva must be greater than zero."
            )

        if rated_power_mva < rated_active_power_mw:
            raise ValueError(
                "rated_power_mva cannot be less than "
                "rated_active_power_mw."
            )

        return cls(
            rated_active_power_mw=rated_active_power_mw,
            rated_power_mva=rated_power_mva,
            active_power_mw=active_power_mw,
            reactive_power_mvar=reactive_power_mvar,
            available_active_power_mw=(
                available_active_power_mw
            ),
            maximum_active_power_mw=(
                rated_active_power_mw
            ),
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Availability Properties
    # ------------------------------------------------------------------

    @property
    def has_available_power_limit(self) -> bool:
        """
        Return whether resource availability is specified.
        """

        return self.available_active_power_mw is not None

    @property
    def available_generation_mw(self) -> float:
        """
        Return currently available wind generation.

        When explicit resource availability is not supplied, the
        installed active-power rating is returned as the physical
        upper bound.
        """

        if self.available_active_power_mw is not None:
            return self.available_active_power_mw

        return self.rated_active_power_mw

    # ------------------------------------------------------------------
    # Curtailment Properties
    # ------------------------------------------------------------------

    @property
    def curtailed_power_mw(self) -> float:
        """
        Return active power currently curtailed.
        """

        return max(
            0.0,
            (
                self.available_generation_mw
                - self.active_generation_mw
            ),
        )

    @property
    def curtailment_fraction(self) -> float:
        """
        Return fraction of available wind generation curtailed.
        """

        available = self.available_generation_mw

        if available == 0.0:
            return 0.0

        return (
            self.curtailed_power_mw
            / available
        )

    # ------------------------------------------------------------------
    # Wind-Speed Properties
    # ------------------------------------------------------------------

    @property
    def has_wind_speed_characteristics(self) -> bool:
        """
        Return whether basic turbine wind-speed characteristics
        are defined.
        """

        return (
            self.cut_in_wind_speed_mps is not None
            and self.rated_wind_speed_mps is not None
            and self.cut_out_wind_speed_mps is not None
        )

    def is_operational_at_wind_speed(
        self,
        wind_speed_mps: float,
    ) -> bool:
        """
        Determine whether the turbine may operate at a wind speed.

        Parameters
        ----------
        wind_speed_mps
            Wind speed in meters per second.

        Returns
        -------
        bool
            True when the wind speed lies within the turbine's
            operating interval.

        Raises
        ------
        ValueError
            If turbine wind-speed characteristics are unavailable.
        """

        if wind_speed_mps < 0.0:
            raise ValueError(
                "wind_speed_mps cannot be negative."
            )

        if not self.has_wind_speed_characteristics:
            raise ValueError(
                "Wind-speed characteristics are not configured."
            )

        return (
            self.cut_in_wind_speed_mps
            <= wind_speed_mps
            < self.cut_out_wind_speed_mps
        )

    # ------------------------------------------------------------------
    # Converter / Generator Capability
    # ------------------------------------------------------------------

    @property
    def reactive_capability_mvar(
        self,
    ) -> float | None:
        """
        Return theoretical reactive-power capability at the current
        active-power setpoint.

        Returns
        -------
        float | None
            Magnitude of reactive-power capability in MVAr when an
            apparent-power rating is available.

        Notes
        -----
        This uses the simplified apparent-power capability circle.

        Detailed DFIG, synchronous-generator, full-converter, and
        grid-code capability curves belong in future dedicated
        capability models.
        """

        if self.rated_power_mva is None:
            return None

        active_power = self.active_generation_mw

        if active_power >= self.rated_power_mva:
            return 0.0

        return (
            (
                self.rated_power_mva**2
                - active_power**2
            )
            ** 0.5
        )

    # ------------------------------------------------------------------
    # Operating Properties
    # ------------------------------------------------------------------

    @property
    def is_generating(self) -> bool:
        """
        Return whether the wind resource is currently generating
        active power.
        """

        return self.active_generation_mw > 0.0

    @property
    def is_curtailed(self) -> bool:
        """
        Return whether available wind generation is curtailed.
        """

        return self.curtailed_power_mw > 0.0

    @property
    def supports_reactive_power_control(self) -> bool:
        """
        Return whether reactive-power control is enabled.
        """

        return (
            self.reactive_power_control_enabled
            and self.rated_power_mva is not None
        )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Wind",
]