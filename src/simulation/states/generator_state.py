"""
Generator simulation state.
"""

from __future__ import annotations

from src.simulation.states.electrical_state import ElectricalState


class GeneratorState(ElectricalState):
    """
    Runtime generator state.
    """

    active_power_mw: float = 0.0

    reactive_power_mvar: float = 0.0

    voltage_setpoint_pu: float = 1.0

    online: bool = True
