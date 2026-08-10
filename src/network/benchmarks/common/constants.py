"""
GridStudio AI

Module:
    constants.py

Description:
    Defines shared constants used throughout the
    GridStudio benchmark framework.

    Only framework-wide constants belong here.

    Benchmark-specific constants shall be defined
    within the corresponding benchmark package.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations


#
# ---------------------------------------------------------------------
# Default electrical base values
# ---------------------------------------------------------------------
#

DEFAULT_BASE_POWER_MVA: float = 100.0

DEFAULT_BASE_FREQUENCY_HZ: float = 50.0


#
# ---------------------------------------------------------------------
# Numerical tolerances
# ---------------------------------------------------------------------
#

DEFAULT_FLOAT_TOLERANCE: float = 1.0e-9

DEFAULT_COMPARISON_TOLERANCE: float = 1.0e-6


#
# ---------------------------------------------------------------------
# Coordinate defaults
# ---------------------------------------------------------------------
#

DEFAULT_X_COORDINATE: float = 0.0

DEFAULT_Y_COORDINATE: float = 0.0


#
# ---------------------------------------------------------------------
# Benchmark defaults
# ---------------------------------------------------------------------
#

DEFAULT_VERSION: str = "1.0"

UNKNOWN_REFERENCE: str = "Unknown"

UNKNOWN_DESCRIPTION: str = ""


#
# ---------------------------------------------------------------------
# Builder defaults
# ---------------------------------------------------------------------
#

DEFAULT_BUS_NAME_PREFIX: str = "Bus"

DEFAULT_BRANCH_NAME_PREFIX: str = "Branch"

DEFAULT_LOAD_NAME_PREFIX: str = "Load"

DEFAULT_GENERATOR_NAME_PREFIX: str = "Generator"

DEFAULT_TRANSFORMER_NAME_PREFIX: str = "Transformer"

DEFAULT_SHUNT_NAME_PREFIX: str = "Shunt"