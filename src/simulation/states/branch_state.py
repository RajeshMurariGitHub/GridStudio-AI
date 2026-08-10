"""
Branch simulation state.
"""

from __future__ import annotations

from src.simulation.states.electrical_state import ElectricalState


class BranchState(ElectricalState):
    """
    Runtime branch state.
    """

    current_ampere: float = 0.0

    active_power_from_mw: float = 0.0

    reactive_power_from_mvar: float = 0.0

    active_power_to_mw: float = 0.0

    reactive_power_to_mvar: float = 0.0

    active_loss_mw: float = 0.0

    reactive_loss_mvar: float = 0.0

    loading_percent: float = 0.0
