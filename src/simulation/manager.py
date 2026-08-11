"""
Simulation orchestration for GridStudio AI.
"""

from __future__ import annotations

from src.core.enums.simulation import SimulationMode
from src.core.enums.simulation import StudyType
from src.simulation.engines.base.engine import SimulationEngine

from src.simulation.models.requests.power_flow_request import (
    PowerFlowRequest,
)

from src.simulation.models.results.power_flow_result import (
    PowerFlowResult,
)


class SimulationManager:
    """
    Orchestrate simulation execution through a simulation engine.

    The manager owns engine capability validation and delegates actual
    simulation execution to the selected engine.
    """

    def __init__(
        self,
        engine: SimulationEngine,
    ) -> None:
        self._engine = engine

    def run_power_flow(
        self,
        request: PowerFlowRequest,
    ) -> PowerFlowResult:
        """
        Run a snapshot power-flow study through the configured engine.

        Parameters
        ----------
        request:
            Solver-independent power-flow request.

        Returns
        -------
        Any
            Result returned by the configured simulation engine.

        Raises
        ------
        ValueError
            If the configured engine does not support snapshot power flow.
        """
        if not self._engine.supports(
            StudyType.POWER_FLOW,
            SimulationMode.SNAPSHOT,
        ):
            raise ValueError(
                f"Simulation engine '{self._engine.name}' does not "
                "support snapshot power flow."
            )

        return self._engine.run(request)


__all__ = [
    "SimulationManager",
]
