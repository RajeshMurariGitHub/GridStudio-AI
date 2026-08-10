"""
GridStudio

Module:
    power.py

Description:
    Immutable engineering value object representing complex
    electrical power.

    The Power class stores the independent active and reactive
    power components and provides derived engineering
    quantities such as apparent power, power factor, and
    complex power.

Author:
    Rajesh Murari

License:
    MIT

Python:
    >=3.12
"""

from __future__ import annotations

import math

from pydantic import ConfigDict

from src.common.models.base_model import BaseModel


class Power(BaseModel):
    """
    Complex electrical power.

    Notes
    -----
    Only active and reactive power are stored.

    Apparent power, complex power and power factor are
    calculated from these quantities.
    """

    model_config = ConfigDict(
        frozen=True,
    )

    #
    # ---------------------------------------------------------
    # Independent Variables
    # ---------------------------------------------------------
    #

    active_mw: float = 0.0

    reactive_mvar: float = 0.0

    #
    # ---------------------------------------------------------
    # Derived Quantities
    # ---------------------------------------------------------
    #

    @property
    def apparent_mva(self) -> float:
        """
        Apparent power (MVA).
        """
        return math.hypot(
            self.active_mw,
            self.reactive_mvar,
        )

    @property
    def complex_power(self) -> complex:
        """
        Complex power.

        Returns
        -------
        complex
            P + jQ
        """
        return complex(
            self.active_mw,
            self.reactive_mvar,
        )

    @property
    def power_factor(self) -> float:
        """
        Signed power factor.

        Returns
        -------
        float
            Active power divided by apparent power.

            Returns 1.0 for zero apparent power.
        """
        s = self.apparent_mva

        if s == 0.0:
            return 1.0

        return self.active_mw / s

    #
    # ---------------------------------------------------------
    # State Flags
    # ---------------------------------------------------------
    #

    @property
    def is_zero(self) -> bool:
        """
        True if both active and reactive power are zero.
        """
        return self.active_mw == 0.0 and self.reactive_mvar == 0.0

    @property
    def is_generating(self) -> bool:
        """
        True if active power is exported.
        """
        return self.active_mw > 0.0

    @property
    def is_consuming(self) -> bool:
        """
        True if active power is imported.
        """
        return self.active_mw < 0.0

    @property
    def is_inductive(self) -> bool:
        """
        True for positive reactive power.
        """
        return self.reactive_mvar > 0.0

    @property
    def is_capacitive(self) -> bool:
        """
        True for negative reactive power.
        """
        return self.reactive_mvar < 0.0
