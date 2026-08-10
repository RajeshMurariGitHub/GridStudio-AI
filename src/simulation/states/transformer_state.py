from __future__ import annotations

from src.simulation.states.electrical_state import ElectricalState


class TransformerState(ElectricalState):
    """
    Runtime transformer state.
    """

    loading_percent: float = 0.0

    tap_position: int = 0
