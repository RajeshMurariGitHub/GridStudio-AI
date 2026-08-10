"""
GridStudio AI

Module:
    power_flow_result.py

Description:
    Immutable result of a completed power flow simulation.

    This model contains:

    * Convergence information
    * Iteration history
    * Simulation state collections
    * Network metadata
    * Derived system statistics

    All values are computed before construction,
    making the model completely immutable.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from uuid import UUID

from pydantic import ConfigDict
from pydantic import Field

from src.simulation.models.convergence import (
    ConvergenceInfo,
)
from src.simulation.models.results.base_result import (
    BaseSimulationResult,
)

from src.simulation.models.iteration import (
    IterationRecord,
)

from src.simulation.states.battery_state import (
    BatteryState,
)
from src.simulation.states.branch_state import (
    BranchState,
)
from src.simulation.states.bus_state import (
    BusState,
)
from src.simulation.states.ev_state import (
    EVState,
)
from src.simulation.states.generator_state import (
    GeneratorState,
)
from src.simulation.states.load_state import (
    LoadState,
)
from src.simulation.states.shunt_state import (
    ShuntState,
)
from src.simulation.states.solar_state import (
    SolarState,
)
from src.simulation.states.transformer_state import (
    TransformerState,
)
from src.simulation.states.wind_state import (
    WindState,
)


class PowerFlowResult(BaseSimulationResult):
    """
    Immutable result of a completed power flow simulation.

    Notes
    -----
    This class is a read-only snapshot of the solved
    electrical network.

    Every value is supplied during construction.
    No fields are modified after initialization.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    #
    # ------------------------------------------------------------------
    # Convergence
    # ------------------------------------------------------------------
    #

    convergence: ConvergenceInfo

    iterations: list[IterationRecord] = Field(
        default_factory=list,
    )

    #
    # ------------------------------------------------------------------
    # Simulation States
    # ------------------------------------------------------------------
    #

    bus_states: dict[UUID, BusState] = Field(
        default_factory=dict,
    )

    branch_states: dict[UUID, BranchState] = Field(
        default_factory=dict,
    )

    generator_states: dict[UUID, GeneratorState] = Field(
        default_factory=dict,
    )

    transformer_states: dict[
        UUID,
        TransformerState,
    ] = Field(
        default_factory=dict,
    )

    load_states: dict[UUID, LoadState] = Field(
        default_factory=dict,
    )

    battery_states: dict[
        UUID,
        BatteryState,
    ] = Field(
        default_factory=dict,
    )

    solar_states: dict[UUID, SolarState] = Field(
        default_factory=dict,
    )

    wind_states: dict[UUID, WindState] = Field(
        default_factory=dict,
    )

    ev_states: dict[UUID, EVState] = Field(
        default_factory=dict,
    )

    shunt_states: dict[
        UUID,
        ShuntState,
    ] = Field(
        default_factory=dict,
    )

    #
    # ------------------------------------------------------------------
    # Network Metadata
    # ------------------------------------------------------------------
    #

    network_name: str

    base_power_mva: float | None

    base_frequency_hz: float

    #
    # ------------------------------------------------------------------
    # Derived Statistics
    # ------------------------------------------------------------------
    #

    total_active_generation_mw: float

    total_reactive_generation_mvar: float

    total_active_load_mw: float

    total_reactive_load_mvar: float

    total_active_loss_mw: float

    total_reactive_loss_mvar: float

    system_power_factor: float

    minimum_bus_voltage_pu: float

    maximum_bus_voltage_pu: float

    average_bus_voltage_pu: float

    maximum_branch_loading_percent: float

    slack_bus_id: UUID | None = None

    #
    # ------------------------------------------------------------------
    # Convenience Properties
    # ------------------------------------------------------------------
    #

    @property
    def converged(self) -> bool:
        """
        True if the solver converged successfully.
        """
        return self.convergence.converged

    @property
    def bus_count(self) -> int:
        """
        Number of solved buses.
        """
        return len(self.bus_states)

    @property
    def branch_count(self) -> int:
        """
        Number of solved branches.
        """
        return len(self.branch_states)

    @property
    def generator_count(self) -> int:
        """
        Number of solved generators.
        """
        return len(self.generator_states)

    @property
    def transformer_count(self) -> int:
        """
        Number of solved transformers.
        """
        return len(self.transformer_states)

__all__ = [
    "PowerFlowResult",
]