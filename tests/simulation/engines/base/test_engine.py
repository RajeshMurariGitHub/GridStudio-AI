from typing import Any

import pytest

from src.core.enums.simulation import SimulationMode
from src.core.enums.simulation import StudyType
from src.simulation.engines.base.capabilities import EngineCapabilities
from src.simulation.engines.base.engine import SimulationEngine


class DummyEngine(SimulationEngine):
    @property
    def name(self) -> str:
        return "dummy"

    @property
    def capabilities(self) -> EngineCapabilities:
        return EngineCapabilities(
            study_types=frozenset(
                {
                    StudyType.POWER_FLOW,
                }
            ),
            simulation_modes=frozenset(
                {
                    SimulationMode.SNAPSHOT,
                }
            ),
        )

    def run(
        self,
        request: Any,
    ) -> Any:
        return request


def test_engine_identity() -> None:
    engine = DummyEngine()

    assert engine.name == "dummy"


def test_engine_capabilities() -> None:
    engine = DummyEngine()

    assert engine.capabilities.supports_study(
        StudyType.POWER_FLOW,
    )

    assert engine.capabilities.supports_mode(
        SimulationMode.SNAPSHOT,
    )


def test_engine_delegates_capability_checks() -> None:
    engine = DummyEngine()

    assert engine.supports_study(
        StudyType.POWER_FLOW,
    )

    assert not engine.supports_study(
        StudyType.SHORT_CIRCUIT,
    )

    assert engine.supports_mode(
        SimulationMode.SNAPSHOT,
    )

    assert not engine.supports_mode(
        SimulationMode.TIME_SERIES,
    )


def test_engine_supports_combined_capability() -> None:
    engine = DummyEngine()

    assert engine.supports(
        StudyType.POWER_FLOW,
        SimulationMode.SNAPSHOT,
    )

    assert not engine.supports(
        StudyType.POWER_FLOW,
        SimulationMode.TIME_SERIES,
    )


def test_engine_run_contract() -> None:
    engine = DummyEngine()

    request = object()

    assert engine.run(request) is request


def test_simulation_engine_is_abstract() -> None:
    with pytest.raises(TypeError):
        SimulationEngine()