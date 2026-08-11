"""
Integration tests for the complete pandapower
power-flow execution pipeline.
"""

from __future__ import annotations

import pytest

from src.simulation.engines.pandapower.engine import (
    PandapowerEngine,
)

from src.simulation.models.results.power_flow_result import (
    PowerFlowResult,
)

from .builders import (
    build_engine_network,
    build_power_flow_request,
)

@pytest.fixture
def engine():
    """
    Create a Pandapower engine.
    """

    return PandapowerEngine()

class TestPandapowerPowerFlowPipeline:
    """
    Integration tests for the complete
    pandapower execution pipeline.
    """


    def test_complete_power_flow(
        self,
        engine,
    ):
        """
        Execute an end-to-end power-flow study.
        """

        network=build_engine_network()
    
        request = build_power_flow_request(
            network,
        )

        result = engine.run(
            request,
        )

        assert isinstance(
            result,
            PowerFlowResult,
        )

        assert result.successful

        assert result.convergence.converged

    def test_result_metadata(
        self,
        engine,
    ) -> None:
        """
        Execution metadata should be
        populated.
        """
        network=build_engine_network()
        request = build_power_flow_request(
            network,
        )

        result = engine.run(
            request,
        )

        assert result.simulation_id is not None

        assert result.started_at is not None

        assert result.completed_at is not None

        assert (
            result.execution_time_seconds
            >= 0.0
        )

        assert result.solver_name == "pandapower"

        assert result.solver_version

        assert (
            result.base_frequency_hz
            == pytest.approx(
                network.base_frequency_hz,
            )
        )

    def test_repeatability(
        self,
        engine,
    ) -> None:
        """
        Running the same study twice should
        produce consistent results.
        """

        network=build_engine_network()
        request = build_power_flow_request(
            network,
        )   

        first = engine.run(
            request,
        )

        second = engine.run(
            request,
        )

        assert first.successful

        assert second.successful

        assert (
            first.total_active_generation_mw
            == pytest.approx(
                second.total_active_generation_mw,
            )
        )

        assert (
            first.total_active_load_mw
            == pytest.approx(
                second.total_active_load_mw,
            )
        )

        assert (
            first.total_active_loss_mw
            == pytest.approx(
                second.total_active_loss_mw,
            )
        )

        assert (
            first.minimum_bus_voltage_pu
            == pytest.approx(
                second.minimum_bus_voltage_pu,
            )
        )

