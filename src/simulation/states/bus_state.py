"""
GridStudio

Module:
    bus_state.py

Description:
    Simulation state of an electrical bus after a completed
    power flow solution.

    This class stores only the numerical operating condition
    of the bus. Static asset information such as nominal
    voltage, voltage limits, location, and connectivity
    remain in the domain Bus model.

Author:
    Rajesh Murari

License:
    MIT

Python:
    >=3.12
"""

from __future__ import annotations

from pydantic import ConfigDict

from src.simulation.states.electrical_state import ElectricalState


class BusState(ElectricalState):
    """
    Numerical operating state of a bus.

    Notes
    -----
    This class represents the solved electrical state of a
    bus after a simulation. It contains only calculated
    quantities and never duplicates the static properties
    defined in the domain Bus model.
    """

    model_config = ConfigDict(
        frozen=True,
    )

    #
    # ---------------------------------------------------------
    # Voltage State
    # ---------------------------------------------------------
    #

    voltage_magnitude_pu: float

    voltage_angle_deg: float

    voltage_complex: complex

    #
    # ---------------------------------------------------------
    # Net Power Injection
    # ---------------------------------------------------------
    #

    net_active_power_mw: float

    net_reactive_power_mvar: float

    #
    # ---------------------------------------------------------
    # Generation
    # ---------------------------------------------------------
    #

    #generated_active_power_mw: float = 0.0

    #generated_reactive_power_mvar: float = 0.0

    #
    # ---------------------------------------------------------
    # Load
    # ---------------------------------------------------------
    #

    #load_active_power_mw: float = 0.0

    #load_reactive_power_mvar: float = 0.0

    #
    # ---------------------------------------------------------
    # Quality Indicators
    # ---------------------------------------------------------
    #

    voltage_violation: bool = False

    #
    # ---------------------------------------------------------
    # Computed Properties
    # ---------------------------------------------------------
    #

    @property
    def voltage_deviation_pu(self) -> float:
        """
        Voltage deviation from the nominal 1.0 per-unit.
        """
        return self.voltage_magnitude_pu - 1.0

    @property
    def within_voltage_limits(self) -> bool:
        """
        True when the bus voltage is within acceptable limits.
        """
        return not self.voltage_violation
