"""
GridStudio

Module:
    impedance.py

Description:
    Immutable engineering value object representing complex
    electrical impedance.

    The impedance is stored internally as a complex quantity
    in ohms. Resistance, reactance, magnitude, and phase
    angle are derived from the stored impedance.

Author:
    Rajesh Murari

License:
    MIT

Python:
    >=3.12
"""

from __future__ import annotations

import cmath
import math

from pydantic import ConfigDict

from src.common.models.base_model import BaseModel


class Impedance(BaseModel):
    """
    Complex electrical impedance.

    Notes
    -----
    Stores impedance in rectangular form and derives all
    other engineering quantities.
    """

    model_config = ConfigDict(
        frozen=True,
    )

    #
    # ---------------------------------------------------------
    # Independent Variable
    # ---------------------------------------------------------
    #

    impedance_ohm: complex = complex(0.0, 0.0)

    #
    # ---------------------------------------------------------
    # Derived Quantities
    # ---------------------------------------------------------
    #

    @property
    def magnitude_ohm(self) -> float:
        """
        Magnitude of the impedance.
        """
        return abs(self.impedance_ohm)

    @property
    def angle_rad(self) -> float:
        """
        Impedance phase angle in radians.
        """
        return cmath.phase(self.impedance_ohm)

    @property
    def angle_deg(self) -> float:
        """
        Impedance phase angle in degrees.
        """
        return math.degrees(self.angle_rad)

    @property
    def real(self) -> float:
        """
        Real component of the impedance.
        """
        return self.impedance_ohm.real

    @property
    def imaginary(self) -> float:
        """
        Imaginary component of the impedance.
        """
        return self.impedance_ohm.imag

    @property
    def resistance_ohm(self) -> float:
        """
        Resistance component.
        """
        return self.impedance_ohm.real

    @property
    def reactance_ohm(self) -> float:
        """
        Reactance component.
        """
        return self.impedance_ohm.imag

    #
    # ---------------------------------------------------------
    # State Flags
    # ---------------------------------------------------------
    #

    @property
    def is_zero(self) -> bool:
        """
        True if the impedance is zero.
        """
        return self.impedance_ohm == 0j

    @property
    def is_purely_resistive(self) -> bool:
        """
        True if the reactance is zero.
        """
        return self.reactance_ohm == 0.0

    @property
    def is_purely_reactive(self) -> bool:
        """
        True if the resistance is zero.
        """
        return self.resistance_ohm == 0.0

    @property
    def is_inductive(self) -> bool:
        """
        True for positive reactance.
        """
        return self.reactance_ohm > 0.0

    @property
    def is_capacitive(self) -> bool:
        """
        True for negative reactance.
        """
        return self.reactance_ohm < 0.0
