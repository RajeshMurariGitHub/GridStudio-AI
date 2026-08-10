"""
GridStudio AI

Module:
    load.py

Description:
    Defines the electrical load model used throughout GridStudio AI.

    A Load represents electrical demand connected to a network node.

    The model supports balanced and unbalanced networks, including
    phase-specific and wye/delta-connected loads, while remaining
    independent of pandapower, OpenDSS, and other simulation engines.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from typing import Self

from pydantic import Field
from pydantic import model_validator

from src.core.enums.equipment import (
    LoadModel,
    LoadType,
)
from src.domain.electrical import (
    GROUNDED_WYE,
    ElectricalConnection,
)
from src.domain.injection import Injection


# ============================================================================
# Load
# ============================================================================


class Load(Injection):
    """
    Electrical load connected to a network node.

    Load specializes Injection with load classification and
    electrical connection information.

    Sign Convention
    ---------------
    GridStudio AI uses the network-injection convention inherited
    from Injection:

    * positive P = injection into the network,
    * negative P = absorption from the network,
    * positive Q = reactive injection,
    * negative Q = reactive absorption.

    Therefore, a conventional consuming load normally has:

        active_power_mw < 0

    and, for an inductive load:

        reactive_power_mvar < 0

    For convenience, ``Load.consumption(...)`` accepts positive
    demand values and converts them into the canonical GridStudio
    injection convention.

    Balanced Networks
    -----------------
    A conventional balanced three-phase load may use:

        phases = PHASE_ABC
        connection = GROUNDED_WYE

    Unbalanced Networks
    -------------------
    Phase-specific loads may use:

        phases = PHASE_A
        phases = PHASE_B
        phases = PHASE_C
        phases = PHASE_AB
        ...

    together with the appropriate wye or delta connection.

    Notes
    -----
    This model describes the static/base electrical demand.

    Time-dependent demand profiles should not be stored directly in
    Load. Future time-series simulation will apply profiles or
    scenario values to the base load specification.
    """

    # ------------------------------------------------------------------
    # Load Classification
    # ------------------------------------------------------------------
    
    load_type: LoadType = Field(
        default=LoadType.MIXED,
        description=(
            "Customer or usage classification of the load."
        ),
    )

    load_model: LoadModel = Field(
        default=LoadModel.CONSTANT_POWER,
        description=(
            "Electrical behavior model used to represent the load."
        ),
    )

    # ------------------------------------------------------------------
    # Electrical Connection
    # ------------------------------------------------------------------

    connection: ElectricalConnection = Field(
        default=GROUNDED_WYE,
        description=(
            "Electrical connection configuration of the load."
        ),
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def _validate_load_configuration(
        self,
    ) -> Self:
        """
        Validate load electrical configuration.
        """

        if self.active_power_mw > 0.0:
            raise ValueError(
                "Load active_power_mw must be less than or equal "
                "to zero under the GridStudio network-injection "
                "sign convention. Use Load.consumption(...) when "
                "specifying positive demand values."
            )

        return self

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def consumption(
        cls,
        *,
        active_power_mw: float,
        reactive_power_mvar: float = 0.0,
        **kwargs,
    ) -> Self:
        """
        Create a conventional consuming load.

        Parameters
        ----------
        active_power_mw
            Positive active-power demand in MW.

        reactive_power_mvar
            Reactive-power demand in MVAr.

            Positive input represents reactive-power consumption.
            Negative input represents capacitive reactive-power
            injection.

        **kwargs
            Additional Load fields such as name, node_id, phases,
            connection, load_type, scaling, tags, or metadata.

        Returns
        -------
        Load
            Load represented using GridStudio's canonical
            network-injection sign convention.
        """

        if active_power_mw < 0.0:
            raise ValueError(
                "Load.consumption() expects a non-negative "
                "active_power_mw demand."
            )

        return cls(
            active_power_mw=-active_power_mw,
            reactive_power_mvar=-reactive_power_mvar,
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Demand Properties
    # ------------------------------------------------------------------

    @property
    def active_demand_mw(self) -> float:
        """
        Return positive active-power demand.

        Returns
        -------
        float
            Scaled active-power consumption in MW.
        """

        return max(
            0.0,
            -self.effective_active_power_mw,
        )

    @property
    def reactive_demand_mvar(self) -> float:
        """
        Return signed reactive-power demand.

        Positive values represent reactive consumption.

        Negative values represent net capacitive reactive injection.
        """

        return (
            -self.effective_reactive_power_mvar
        )

    @property
    def apparent_demand_mva(self) -> float:
        """
        Return apparent-power magnitude of the load.
        """

        return abs(
            complex(
                self.active_demand_mw,
                self.reactive_demand_mvar,
            )
        )

    # ------------------------------------------------------------------
    # Power-Factor Properties
    # ------------------------------------------------------------------

    @property
    def power_factor(self) -> float | None:
        """
        Return load power-factor magnitude.

        Returns
        -------
        float | None
            Power factor in the range 0..1, or None when apparent
            demand is zero.
        """

        apparent_power = self.apparent_demand_mva

        if apparent_power == 0.0:
            return None

        return (
            self.active_demand_mw
            / apparent_power
        )

    @property
    def is_inductive(self) -> bool:
        """
        Return whether the load consumes reactive power.
        """

        return self.reactive_demand_mvar > 0.0

    @property
    def is_capacitive(self) -> bool:
        """
        Return whether the load supplies reactive power.
        """

        return self.reactive_demand_mvar < 0.0


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Load",
]