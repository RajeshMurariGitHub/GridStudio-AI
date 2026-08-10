"""
GridStudio

Module:
    types.py

Description:
    Common type aliases used throughout the GridStudio platform.

Author:
    Rajesh Murari

License:
    MIT

Python:
    >=3.12
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, TypeAlias

import numpy as np
import pandas as pd

PathLike: TypeAlias = str | Path

JSONDict: TypeAlias = dict[str, Any]

JSONList: TypeAlias = list[Any]

Numeric: TypeAlias = int | float

NumberArray: TypeAlias = np.ndarray

DataFrame: TypeAlias = pd.DataFrame

Series: TypeAlias = pd.Series

BusIndex: TypeAlias = int

LineIndex: TypeAlias = int

TransformerIndex: TypeAlias = int

GeneratorIndex: TypeAlias = int

LoadIndex: TypeAlias = int

SwitchIndex: TypeAlias = int

NetworkID: TypeAlias = str

SimulationID: TypeAlias = str

ExperimentID: TypeAlias = str

Timestamp: TypeAlias = pd.Timestamp

TimeSeries: TypeAlias = pd.Series

__all__ = [
    "PathLike",
    "JSONDict",
    "JSONList",
    "Numeric",
    "NumberArray",
    "DataFrame",
    "Series",
    "BusIndex",
    "LineIndex",
    "TransformerIndex",
    "GeneratorIndex",
    "LoadIndex",
    "SwitchIndex",
    "NetworkID",
    "SimulationID",
    "ExperimentID",
    "Timestamp",
    "TimeSeries",
]
