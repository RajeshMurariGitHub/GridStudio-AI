from typing import Any, get_type_hints

import pytest

from src.core.enums.simulation import SimulationMode
from src.core.enums.simulation import StudyType
from src.simulation.engines.base.capabilities import EngineCapabilities
from src.simulation.engines.base.engine import SimulationEngine
from src.simulation.manager import SimulationManager

from src.simulation.models.requests.power_flow_request import (
    PowerFlowRequest,
)
from src.simulation.models.results.power_flow_result import (
    PowerFlowResult,
)

class DummyEngine(SimulationEngine):
    def __init__(
        self,
        *,
        supports_power_flow: bool = True,
    ) -> None:
        self.received_request: Any = None

        study_types = (
            frozenset({StudyType.POWER_FLOW})
            if supports_power_flow
            else frozenset()
        )

        self._capabilities = EngineCapabilities(
            study_types=study_types,
            simulation_modes=frozenset(
                {SimulationMode.SNAPSHOT},
            ),
        )

    @property
    def name(self) -> str:
        return "dummy"

    @property
    def capabilities(self) -> EngineCapabilities:
        return self._capabilities

    def run(
        self,
        request: Any,
    ) -> Any:
        self.received_request = request
        return request


def test_manager_accepts_engine() -> None:
    engine = DummyEngine()

    manager = SimulationManager(engine)

    assert manager is not None


def test_run_power_flow_delegates_request_to_engine() -> None:
    engine = DummyEngine()
    manager = SimulationManager(engine)

    request = object()

    result = manager.run_power_flow(request)

    assert engine.received_request is request
    assert result is request


def test_run_power_flow_returns_engine_result() -> None:
    class ResultEngine(DummyEngine):
        def run(
            self,
            request: Any,
        ) -> Any:
            self.received_request = request
            return "simulation-result"

    engine = ResultEngine()
    manager = SimulationManager(engine)

    result = manager.run_power_flow(object())

    assert result == "simulation-result"


def test_run_power_flow_rejects_unsupported_engine() -> None:
    engine = DummyEngine(
        supports_power_flow=False,
    )
    manager = SimulationManager(engine)

    with pytest.raises(ValueError):
        manager.run_power_flow(object())

    assert engine.received_request is None

def test_run_power_flow_has_concrete_contract() -> None:
    hints = get_type_hints(
        SimulationManager.run_power_flow,
    )

    assert (
        hints["request"]
        is PowerFlowRequest
    )

    assert (
        hints["return"]
        is PowerFlowResult
    )
