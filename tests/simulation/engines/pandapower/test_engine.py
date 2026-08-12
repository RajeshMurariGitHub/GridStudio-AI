"""
Unit tests for PandapowerEngine.
"""

from __future__ import annotations

from uuid import UUID

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest


from src.simulation.engines.pandapower.engine import (
    PandapowerEngine,
)

from src.simulation.engines.pandapower.mapping_results import (
    PandapowerMappingResult,
)

from src.simulation.models.results.power_flow_result import (
    PowerFlowResult,
)

from .builders import (
    build_power_flow_request,
    build_engine_network,
)

from src.core.enums.simulation import SimulationMode
from src.core.enums.simulation import StudyType

from src.simulation.models.convergence import (
    ConvergenceInfo,
)

@pytest.fixture
def engine():
    """
    Create a Pandapower engine.
    """

    return PandapowerEngine()

class TestPandapowerEngine:
    """
    Unit tests for PandapowerEngine.
    """
    # ENGINE IDENTITY
    def test_name(
        self,
        engine,
    ) -> None:
        assert engine.name == "pandapower"

    # SUPPORTED CAPABILITIES
    def test_capabilities(
        self,
        engine,
    ) -> None:
        assert engine.supports_study(
            StudyType.POWER_FLOW,
        )

        assert engine.supports_mode(
            SimulationMode.SNAPSHOT,
        )

        assert engine.supports(
            StudyType.POWER_FLOW,
            SimulationMode.SNAPSHOT,
        )

    # UNSUPPORTED CAPABILITIES
    def test_unsupported_capabilities(
        self,
        engine,
    ) -> None:
        assert not engine.supports_study(
            StudyType.SHORT_CIRCUIT,
        )

        assert not engine.supports_mode(
            SimulationMode.TIME_SERIES,
        )

        assert not engine.supports(
            StudyType.POWER_FLOW,
            SimulationMode.TIME_SERIES,
        )


    def test_invalid_request(
        self,
        engine,
    ):
        """
        Invalid request type should raise TypeError.
        """

        with pytest.raises(
            TypeError,
        ):

            engine.run(
                None,
            )

    def test_run_invokes_converter(
        self,
        engine,
    ):
        """
        Engine should invoke the converter.
        """
        network=build_engine_network()
        request = build_power_flow_request(
            network,
        )  

        fake_conversion = MagicMock()

        fake_conversion.network = MagicMock()

        with patch.object(
            engine._converter,
            "convert",
            return_value=fake_conversion,
        ) as convert:

            with patch.object(
                engine,
                "_execute_power_flow",
            ):

                with patch.object(
                    engine._mapper,
                    "map",
                    return_value=MagicMock(),
                ):

                    with patch.object(
                        engine,
                        "_build_result",
                        return_value=MagicMock(),
                    ):

                        engine.run(
                            request,
                        )

        convert.assert_called_once()

    def test_run_executes_solver(
        self,
        engine,
    ):
        """
        Engine should execute the power-flow solver.
        """

        network=build_engine_network()
        request = build_power_flow_request(
            network,
        ) 

        fake_conversion = MagicMock()

        fake_conversion.network = MagicMock()

        with patch.object(
            engine._converter,
            "convert",
            return_value=fake_conversion,
        ):

            with patch.object(
                engine,
                "_execute_power_flow",
            ) as solver:

                with patch.object(
                    engine._mapper,
                    "map",
                    return_value=MagicMock(),
                ):

                    with patch.object(
                        engine,
                        "_build_result",
                        return_value=MagicMock(),
                    ):

                        engine.run(
                            request,
                        )

        solver.assert_called_once_with(
            fake_conversion.network,
        )


    def test_run_invokes_mapper(
        self,
        engine,
    ):
        """
        Engine should invoke the result mapper.
        """

        network=build_engine_network()
        request = build_power_flow_request(
            network,
        ) 

        fake_conversion = MagicMock()

        fake_conversion.network = MagicMock()

        with patch.object(
            engine._converter,
            "convert",
            return_value=fake_conversion,
        ):

            with patch.object(
                engine,
                "_execute_power_flow",
            ):

                with patch.object(
                    engine._mapper,
                    "map",
                    return_value=MagicMock(),
                ) as mapper:

                    with patch.object(
                        engine,
                        "_build_result",
                        return_value=MagicMock(),
                    ):

                        engine.run(
                            request,
                        )

        mapper.assert_called_once_with(
            fake_conversion.network,
            fake_conversion,
        )

    def test_run_returns_power_flow_result(
        self,
        engine,
    ) -> None:
        """
        Engine should return a PowerFlowResult.
        """
        network=build_engine_network()
        request = build_power_flow_request(
            network,
        ) 

        fake_conversion = MagicMock()

        fake_conversion.network = MagicMock()

        fake_mapping = MagicMock(
            spec=PandapowerMappingResult,
        )

        fake_mapping.convergence = ConvergenceInfo(
            converged=True,
            iterations=0,
        )

        fake_mapping.statistics = {

            "total_active_generation_mw": 0.0,
            "total_reactive_generation_mvar": 0.0,
            "total_active_load_mw": 0.0,
            "total_reactive_load_mvar": 0.0,
            "total_active_loss_mw": 0.0,
            "total_reactive_loss_mvar": 0.0,
            "minimum_bus_voltage_pu": 1.0,
            "maximum_bus_voltage_pu": 1.0,
            "average_bus_voltage_pu": 1.0,
            "maximum_branch_loading_percent": 0.0,
            "system_power_factor": 1.0,
        }

        fake_mapping.bus_states = {}
        fake_mapping.branch_states = {}
        fake_mapping.transformer_states = {}
        fake_mapping.load_states = {}
        fake_mapping.generator_states = {}
        fake_mapping.battery_states = {}
        fake_mapping.ev_states = {}
        fake_mapping.shunt_states = {}
        fake_mapping.solar_states = {}
        fake_mapping.wind_states = {}

        with patch.object(
            engine._converter,
            "convert",
            return_value=fake_conversion,
        ):

            with patch.object(
                engine,
                "_execute_power_flow",
            ):

                with patch.object(
                    engine._mapper,
                    "map",
                    return_value=fake_mapping,
                ):

                    result = engine.run(
                        request,
                    )

        assert isinstance(
            result,
            PowerFlowResult,
        )

    def test_build_result(
        self,
        engine,
    ) -> None:
        """
        _build_result() should correctly
        assemble a PowerFlowResult.
        """

        network=build_engine_network()
        request = build_power_flow_request(
            network,
        ) 

        mapping_result = MagicMock(
            spec=PandapowerMappingResult,
        )

        mapping_result.convergence = ConvergenceInfo(
            converged=True,
            iterations=0,
        )

        mapping_result.statistics = {

            "total_active_generation_mw": 10.0,
            "total_reactive_generation_mvar": 2.0,
            "total_active_load_mw": 9.5,
            "total_reactive_load_mvar": 1.8,
            "total_active_loss_mw": 0.5,
            "total_reactive_loss_mvar": 0.2,
            "minimum_bus_voltage_pu": 0.98,
            "maximum_bus_voltage_pu": 1.02,
            "average_bus_voltage_pu": 1.00,
            "maximum_branch_loading_percent": 35.0,
            "system_power_factor": 0.98,
        }

        mapping_result.bus_states = {}
        mapping_result.branch_states = {}
        mapping_result.transformer_states = {}
        mapping_result.load_states = {}
        mapping_result.generator_states = {}
        mapping_result.battery_states = {}
        mapping_result.ev_states = {}
        mapping_result.shunt_states = {}
        mapping_result.solar_states = {}
        mapping_result.wind_states = {}

        result = engine._build_result(

            simulation_id=UUID(int=1),

            request=request,

            mapping_result=mapping_result,

            started_at=engine._current_timestamp(),

            completed_at=engine._current_timestamp(),

            execution_time_seconds=0.01,
        )

        assert isinstance(
            result,
            PowerFlowResult,
        )

        assert result.successful

        assert result.slack_bus_id == (
            request.reference_sources[0].bus_id
        )

        assert result.total_active_generation_mw == 10.0

        assert result.total_active_loss_mw == 0.5

        assert result.base_power_mva == network.base_power_mva

    def test_solver_failure_propagates(
        self,
        engine,
    ) -> None:
        """
        Solver exceptions should propagate.
        """

        network=build_engine_network()
        request = build_power_flow_request(
            network,
        ) 

        fake_conversion = MagicMock()

        fake_conversion.network = MagicMock()

        with patch.object(
            engine._converter,
            "convert",
            return_value=fake_conversion,
        ):

            with patch.object(
                engine,
                "_execute_power_flow",
                side_effect=RuntimeError(
                    "solver failed",
                ),
            ):

                with pytest.raises(
                    RuntimeError,
                ):

                    engine.run(
                        request,
                    )


