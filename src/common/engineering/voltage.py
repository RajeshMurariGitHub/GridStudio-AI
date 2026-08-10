"""
GridStudio

Module:
    voltage.py

Description:
    Immutable engineering value object representing a complex
    voltage phasor in per-unit.

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


class Voltage(BaseModel):
    """
    Complex voltage phasor.

    Notes
    -----
    The voltage is stored internally as a complex number in
    per-unit. Magnitude and angle are computed on demand.
    """

    model_config = ConfigDict(
        frozen=True,
    )

    #
    # ---------------------------------------------------------
    # Independent Variable
    # ---------------------------------------------------------
    #

    phasor_pu: complex = complex(1.0, 0.0)

    #
    # ---------------------------------------------------------
    # Derived Quantities
    # ---------------------------------------------------------
    #

    @property
    def magnitude_pu(self) -> float:
        """Voltage magnitude in per-unit."""
        return abs(self.phasor_pu)

    @property
    def angle_rad(self) -> float:
        """Voltage angle in radians."""
        return cmath.phase(self.phasor_pu)

    @property
    def angle_deg(self) -> float:
        """Voltage angle in degrees."""
        return math.degrees(self.angle_rad)

    @property
    def real(self) -> float:
        """Real component."""
        return self.phasor_pu.real

    @property
    def imaginary(self) -> float:
        """Imaginary component."""
        return self.phasor_pu.imag

    #
    # ---------------------------------------------------------
    # State Flags
    # ---------------------------------------------------------
    #

    @property
    def is_zero(self) -> bool:
        """True if the voltage phasor is zero."""
        return self.phasor_pu == 0j
