"""
GridStudio AI

Module:
    bus.py

Description:
    Defines the electrical bus model used throughout GridStudio AI.

    A Bus represents a power-system connection point with a nominal
    voltage level, bus classification, operating voltage limits,
    and optional power-flow reference setpoints.

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

from src.core.enums import BusType
from src.domain.node import Node


# ============================================================================
# Bus
# ============================================================================


class Bus(Node):
    """
    Electrical power-system bus.

    A Bus specializes Node by adding the electrical properties
    required to represent a power-system connection point.

    Examples
    --------
    A bus may represent:

    * a slack/reference bus,
    * a PV generator bus,
    * a PQ load bus,
    * a distribution feeder node,
    * a DER interconnection point,
    * an unbalanced multi-phase distribution bus.

    Parameters
    ----------
    nominal_voltage_kv
        Nominal line-to-line voltage level of the bus in kV.

    bus_type
        Power-flow classification of the bus.

    minimum_voltage_pu
        Lower acceptable voltage-magnitude limit.

    maximum_voltage_pu
        Upper acceptable voltage-magnitude limit.

    voltage_setpoint_pu
        Optional voltage-magnitude setpoint.

    angle_setpoint_deg
        Optional voltage-angle reference in electrical degrees.

    Notes
    -----
    Bus describes network configuration rather than solved state.

    Solved quantities such as actual voltage magnitude, voltage
    angle, complex voltage, power injection, and phase-specific
    results belong in simulation state/result models.

    For unbalanced networks, ``phases`` inherited from Node defines
    which physical phases exist at the bus.

    ``nominal_voltage_kv`` represents the nominal system voltage
    level and does not imply that all solved phase voltages are
    identical.
    """

    # ------------------------------------------------------------------
    # Voltage Level
    # ------------------------------------------------------------------

    nominal_voltage_kv: float = Field(
        ...,
        gt=0.0,
        description=(
            "Nominal line-to-line voltage level of the bus in kV."
        ),
    )

    # ------------------------------------------------------------------
    # Power-Flow Classification
    # ------------------------------------------------------------------

    bus_type: BusType = Field(
        default=BusType.PQ,
        description=(
            "Power-flow classification of the bus."
        ),
    )

    # ------------------------------------------------------------------
    # Voltage Limits
    # ------------------------------------------------------------------

    minimum_voltage_pu: float = Field(
        default=0.90,
        gt=0.0,
        description=(
            "Minimum acceptable bus voltage magnitude in per unit."
        ),
    )

    maximum_voltage_pu: float = Field(
        default=1.10,
        gt=0.0,
        description=(
            "Maximum acceptable bus voltage magnitude in per unit."
        ),
    )

    # ------------------------------------------------------------------
    # Power-Flow Setpoints
    # ------------------------------------------------------------------

    voltage_setpoint_pu: float | None = Field(
        default=None,
        gt=0.0,
        description=(
            "Optional voltage-magnitude setpoint in per unit."
        ),
    )

    angle_setpoint_deg: float | None = Field(
        default=None,
        ge=-180.0,
        le=180.0,
        description=(
            "Optional voltage-angle reference in electrical "
            "degrees."
        ),
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def _validate_voltage_configuration(
        self,
    ) -> Self:
        """
        Validate bus voltage limits and setpoints.
        """

        if (
            self.minimum_voltage_pu
            >= self.maximum_voltage_pu
        ):
            raise ValueError(
                "minimum_voltage_pu must be less than "
                "maximum_voltage_pu."
            )

        if self.voltage_setpoint_pu is not None:
            if not (
                self.minimum_voltage_pu
                <= self.voltage_setpoint_pu
                <= self.maximum_voltage_pu
            ):
                raise ValueError(
                    "voltage_setpoint_pu must lie within the "
                    "configured bus voltage limits."
                )

        return self

    # ------------------------------------------------------------------
    # Bus-Type Properties
    # ------------------------------------------------------------------

    @property
    def is_slack(self) -> bool:
        """
        Return whether this is the slack/reference bus.
        """

        return self.bus_type == BusType.SLACK

    @property
    def is_reference(self) -> bool:
        """
        Alias indicating whether this is the reference bus.
        """

        return self.is_slack

    @property
    def is_pv(self) -> bool:
        """
        Return whether this is a PV bus.
        """

        return self.bus_type == BusType.PV

    @property
    def is_pq(self) -> bool:
        """
        Return whether this is a PQ bus.
        """

        return self.bus_type == BusType.PQ

    # ------------------------------------------------------------------
    # Voltage Properties
    # ------------------------------------------------------------------

    @property
    def voltage_range_pu(
        self,
    ) -> tuple[float, float]:
        """
        Return configured voltage limits.

        Returns
        -------
        tuple[float, float]
            Minimum and maximum voltage magnitude in per unit.
        """

        return (
            self.minimum_voltage_pu,
            self.maximum_voltage_pu,
        )

    @property
    def has_voltage_setpoint(self) -> bool:
        """
        Return whether a voltage-magnitude setpoint is defined.
        """

        return self.voltage_setpoint_pu is not None

    @property
    def has_angle_setpoint(self) -> bool:
        """
        Return whether a voltage-angle setpoint is defined.
        """

        return self.angle_setpoint_deg is not None


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Bus",
]