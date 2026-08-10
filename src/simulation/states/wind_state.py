"""
Wind simulation state.
"""

from __future__ import annotations

from src.simulation.states.electrical_state import ElectricalState


class WindState(ElectricalState):
    """
    Runtime wind-generation state.
    """

    active_power_mw: float = 0.0
    reactive_power_mvar: float = 0.0
    online: bool = True