from src.core.enums.simulation import SimulationMode
from src.core.enums.simulation import StudyType
from src.simulation.engines.base.capabilities import EngineCapabilities


def test_empty_capabilities_support_nothing() -> None:
    capabilities = EngineCapabilities()

    assert capabilities.study_types == frozenset()
    assert capabilities.simulation_modes == frozenset()

    assert not capabilities.supports_study(
        StudyType.POWER_FLOW,
    )
    assert not capabilities.supports_mode(
        SimulationMode.SNAPSHOT,
    )


def test_supports_declared_study() -> None:
    capabilities = EngineCapabilities(
        study_types=frozenset(
            {
                StudyType.POWER_FLOW,
            }
        ),
    )

    assert capabilities.supports_study(
        StudyType.POWER_FLOW,
    )

    assert not capabilities.supports_study(
        StudyType.SHORT_CIRCUIT,
    )


def test_supports_declared_mode() -> None:
    capabilities = EngineCapabilities(
        simulation_modes=frozenset(
            {
                SimulationMode.SNAPSHOT,
            }
        ),
    )

    assert capabilities.supports_mode(
        SimulationMode.SNAPSHOT,
    )

    assert not capabilities.supports_mode(
        SimulationMode.TIME_SERIES,
    )


def test_supports_requires_both_study_and_mode() -> None:
    capabilities = EngineCapabilities(
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

    assert capabilities.supports(
        StudyType.POWER_FLOW,
        SimulationMode.SNAPSHOT,
    )

    assert not capabilities.supports(
        StudyType.SHORT_CIRCUIT,
        SimulationMode.SNAPSHOT,
    )

    assert not capabilities.supports(
        StudyType.POWER_FLOW,
        SimulationMode.TIME_SERIES,
    )


def test_capability_sets_are_frozen() -> None:
    capabilities = EngineCapabilities(
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

    assert isinstance(
        capabilities.study_types,
        frozenset,
    )

    assert isinstance(
        capabilities.simulation_modes,
        frozenset,
    )