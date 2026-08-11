"""
GridStudio AI

Module:
    mapping_result.py

Description:
    Internal result produced by PandapowerResultMapper.

    This model contains mapped simulation states and derived
    statistics, but intentionally excludes execution metadata.

    The PandapowerEngine converts this object into the public
    PowerFlowResult.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from typing import Mapping
from uuid import UUID

from pydantic import ConfigDict

from src.core.models import BaseModel

from src.simulation.models.convergence import ConvergenceInfo

from src.simulation.states.bus_state import BusState
from src.simulation.states.branch_state import BranchState
from src.simulation.states.transformer_state import TransformerState
from src.simulation.states.load_state import LoadState
from src.simulation.states.generator_state import GeneratorState
from src.simulation.states.battery_state import BatteryState
from src.simulation.states.ev_state import EVState
from src.simulation.states.shunt_state import ShuntState
from src.simulation.states.solar_state import SolarState
from src.simulation.states.wind_state import WindState


class PandapowerMappingResult(BaseModel):
    """
    Internal mapped representation of a solved pandapower network.

    This model is an implementation detail of the pandapower
    engine and is not part of the public simulation API.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    convergence: ConvergenceInfo

    statistics: Mapping[
        str,
        float,
    ]

    bus_states: dict[
        UUID,
        BusState,
    ]

    branch_states: dict[
        UUID,
        BranchState,
    ]

    transformer_states: dict[
        UUID,
        TransformerState,
    ]

    load_states: dict[
        UUID,
        LoadState,
    ]

    generator_states: dict[
        UUID,
        GeneratorState,
    ]

    battery_states: dict[
        UUID,
        BatteryState,
    ]

    ev_states: dict[
        UUID,
        EVState,
    ]

    shunt_states: dict[
        UUID,
        ShuntState,
    ]

    solar_states: dict[UUID, SolarState]

    wind_states: dict[UUID, WindState]


__all__ = [
    "PandapowerMappingResult",
]