"""
GridStudio AI

Module:
    solar.py

Description:
    Defines the solar photovoltaic generation model used throughout
    GridStudio AI.

    Solar represents a photovoltaic DER connected to the electrical
    network through a power-electronic inverter.

    The model stores installed PV capacity, inverter capability,
    operating limits, and curtailment capability while remaining
    independent of irradiance profiles, forecasting models,
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
# Solar
# ============================================================================


class Solar(Generator):
    """
    Solar photovoltaic distributed energy resource.

    Solar specializes Generator by adding photovoltaic-array and
    inverter characteristics.

    Power Convention
    ----------------
    GridStudio AI uses the network-injection convention inherited
    from Generator:

    * positive active power = generation into the network,
    * positive reactive power = reactive-power injection,
    * negative reactive power = reactive-power absorption.

    The inherited ``active_power_mw`` and ``reactive_power_mvar``
    fields represent the configured/base operating setpoint.

    Capacity Model
    --------------
    Two ratings are distinguished:

    ``dc_capacity_mw``
        Installed photovoltaic array DC capacity.

    ``rated_power_mva``
        Inverter AC apparent-power rating inherited from Generator.

    This distinction allows GridStudio AI to represent DC/AC
    oversizing without confusing PV-array capacity with inverter
    capability.

    Time-Series Operation
    ---------------------
    Irradiance and temperature do not belong directly in this model.

    Future time-series simulation should conceptually operate as:

        weather/profile
              |
              v
        available PV power
              |
              v
        controller / optimization
              |
              v
        Solar setpoint
              |
              v
        simulation engine

    The solved electrical output belongs in simulation state/result
    models rather than this equipment definition.

    Notes
    -----
    Solar may participate in future functions including:

    * irradiance-driven generation,
    * temperature derating,
    * active-power curtailment,
    * Volt-VAR control,
    * fixed power-factor operation,
    * Volt-Watt control,
    * optimal DER dispatch,
    * hosting-capacity analysis,
    * time-series simulation,
    * forecasting,
    * multi-objective optimization.
    """

    # ------------------------------------------------------------------
    # PV Array
    # ------------------------------------------------------------------

    dc_capacity_mw: float = Field(
        ...,
        gt=0.0,
        description=(
            "Installed photovoltaic-array DC capacity in MW."
        ),
    )

    # ------------------------------------------------------------------
    # Availability
    # ------------------------------------------------------------------

    available_active_power_mw: float | None = Field(
        default=None,
        ge=0.0,
        description=(
            "Optional currently available active power from the "
            "PV resource in MW before curtailment."
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
    # Inverter Capability
    # ------------------------------------------------------------------

    reactive_power_control_enabled: bool = Field(
        default=False,
        description=(
            "Whether inverter reactive-power control is enabled."
        ),
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def _validate_solar_configuration(
        self,
    ) -> Self:
        """
        Validate photovoltaic and inverter configuration.
        """

        if (
            self.maximum_active_power_mw is not None
            and self.maximum_active_power_mw
            > self.dc_capacity_mw
        ):
            raise ValueError(
                "maximum_active_power_mw cannot exceed "
                "dc_capacity_mw."
            )

        if (
            self.available_active_power_mw is not None
            and self.available_active_power_mw
            > self.dc_capacity_mw
        ):
            raise ValueError(
                "available_active_power_mw cannot exceed "
                "dc_capacity_mw."
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
                "active_power_mw must equal available_active_power_mw "
                "when curtailment_enabled is False."
            )

        if (
            self.reactive_power_control_enabled
            and self.rated_power_mva is None
        ):
            raise ValueError(
                "rated_power_mva is required when "
                "reactive_power_control_enabled is True."
            )

        return self

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def photovoltaic(
        cls,
        *,
        dc_capacity_mw: float,
        inverter_rating_mva: float,
        active_power_mw: float = 0.0,
        reactive_power_mvar: float = 0.0,
        available_active_power_mw: float | None = None,
        **kwargs,
    ) -> Self:
        """
        Create a photovoltaic generating resource.

        Parameters
        ----------
        dc_capacity_mw
            Installed photovoltaic-array DC capacity in MW.

        inverter_rating_mva
            Inverter AC apparent-power rating in MVA.

        active_power_mw
            Initial active-power operating setpoint in MW.

        reactive_power_mvar
            Initial reactive-power operating setpoint in MVAr.

        available_active_power_mw
            Optional currently available PV active power before
            curtailment.

        **kwargs
            Additional Solar/Generator fields.

        Returns
        -------
        Solar
            Configured photovoltaic resource.
        """

        if inverter_rating_mva <= 0.0:
            raise ValueError(
                "inverter_rating_mva must be greater than zero."
            )

        return cls(
            dc_capacity_mw=dc_capacity_mw,
            rated_power_mva=inverter_rating_mva,
            active_power_mw=active_power_mw,
            reactive_power_mvar=reactive_power_mvar,
            available_active_power_mw=(
                available_active_power_mw
            ),
            maximum_active_power_mw=min(
                dc_capacity_mw,
                inverter_rating_mva,
            ),
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Capacity Properties
    # ------------------------------------------------------------------

    @property
    def inverter_rating_mva(self) -> float | None:
        """
        Return inverter AC apparent-power rating.
        """

        return self.rated_power_mva

    @property
    def dc_ac_ratio(self) -> float | None:
        """
        Return photovoltaic DC-to-AC sizing ratio.

        Returns
        -------
        float | None
            DC/AC ratio when an inverter rating is available.
        """

        if self.rated_power_mva is None:
            return None

        return (
            self.dc_capacity_mw
            / self.rated_power_mva
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
        Return currently available PV active power.

        When no explicit resource availability has been supplied,
        the installed DC capacity is returned as the upper physical
        resource bound.
        """

        if self.available_active_power_mw is not None:
            return self.available_active_power_mw

        return self.dc_capacity_mw

    # ------------------------------------------------------------------
    # Curtailment Properties
    # ------------------------------------------------------------------

    @property
    def curtailed_power_mw(self) -> float:
        """
        Return active power currently curtailed.

        Returns
        -------
        float
            Difference between available resource power and the
            configured active-power setpoint.
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
        Return fraction of available PV generation curtailed.
        """

        available = self.available_generation_mw

        if available == 0.0:
            return 0.0

        return (
            self.curtailed_power_mw
            / available
        )

    # ------------------------------------------------------------------
    # Inverter Capability
    # ------------------------------------------------------------------

    @property
    def inverter_reactive_capability_mvar(
        self,
    ) -> float | None:
        """
        Return theoretical reactive-power capability at the current
        active-power setpoint.

        Returns
        -------
        float | None
            Magnitude of available reactive capability in MVAr when
            an inverter rating is defined.

        Notes
        -----
        The calculation uses the inverter apparent-power circle:

            Qmax = sqrt(Srated^2 - P^2)

        More restrictive manufacturer or grid-code limits may later
        be represented by dedicated inverter-control/capability
        models.
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

    @property
    def inverter_utilization(self) -> float | None:
        """
        Return apparent-power utilization of the inverter.
        """

        return self.apparent_power_utilization

    # ------------------------------------------------------------------
    # Operating Properties
    # ------------------------------------------------------------------

    @property
    def is_generating(self) -> bool:
        """
        Return whether the PV system is currently generating
        active power.
        """

        return self.active_generation_mw > 0.0

    @property
    def is_curtailed(self) -> bool:
        """
        Return whether available PV power is currently curtailed.
        """

        return self.curtailed_power_mw > 0.0

    @property
    def supports_reactive_power_control(self) -> bool:
        """
        Return whether inverter reactive-power control is enabled.
        """

        return (
            self.reactive_power_control_enabled
            and self.rated_power_mva is not None
        )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Solar",
]