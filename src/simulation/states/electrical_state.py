"""
GridStudio

Module:
    electrical_state.py

Description:
    Base class for all electrical simulation state objects.

    This class extends BaseState by adding operational
    properties common to every electrical asset.

Author:
    Rajesh Murari

License:
    MIT

Python:
    >=3.12
"""

from __future__ import annotations

from pydantic import ConfigDict

from src.simulation.states.base_state import BaseState
from src.core.enums.validation import ValidationStatus


class ElectricalState(BaseState):
    """
    Base class for electrical simulation state objects.

    Notes
    -----
    This class stores only the operational status common
    to all electrical assets. Numerical quantities such as
    voltage, current, power, loading, and losses belong to
    specialized derived classes.
    """

    model_config = ConfigDict(
        frozen=True,
    )

    energized: bool = True

    converged: bool = True

    @property
    def is_valid(self) -> bool:
        """
        Returns True when the state passed validation.
        """
        return self.validation_status == ValidationStatus.VALID
