"""
GridStudio

Module:
    current.py

Description:
    Immutable engineering value object representing an AC
    current phasor.

    The current is stored internally as a complex phasor in
    amperes. Magnitude and angle are computed on demand.

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


class Current(BaseModel):
    """
    Complex AC current phasor.

    Notes
    -----
    The current is stored as a complex phasor in amperes.
    Magnitude and phase angle are derived properties.
    """

    model_config = ConfigDict(
        frozen=True,
    )

    #
    # ---------------------------------------------------------
    # Independent Variable
    # ---------------------------------------------------------
    #

    phasor_amp: complex = complex(0.0, 0.0)

    #
    # ---------------------------------------------------------
    # Derived Quantities
    # ---------------------------------------------------------
    #

    @property
    def magnitude_amp(self) -> float:
        """
        Current magnitude in amperes.
        """
        return abs(self.phasor_amp)

    @property
    def angle_rad(self) -> float:
        """
        Current phase angle in radians.
        """
        return cmath.phase(self.phasor_amp)

    @property
    def angle_deg(self) -> float:
        """
        Current phase angle in degrees.
        """
        return math.degrees(self.angle_rad)

    @property
    def real(self) -> float:
        """
        Real component of the current phasor.
        """
        return self.phasor_amp.real

    @property
    def imaginary(self) -> float:
        """
        Imaginary component of the current phasor.
        """
        return self.phasor_amp.imag

    #
    # ---------------------------------------------------------
    # State Flags
    # ---------------------------------------------------------
    #

    @property
    def is_zero(self) -> bool:
        """
        Returns True when the current phasor is zero.
        """
        return self.phasor_amp == 0j
