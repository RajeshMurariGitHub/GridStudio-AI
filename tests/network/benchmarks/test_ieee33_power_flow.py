"""
GridStudio AI

Module:
    test_ieee33_power_flow.py

Description:
    Integration tests for the IEEE 33-Bus benchmark.

    These tests verify the complete GridStudio AI
    power-flow pipeline from benchmark network
    construction through solver execution.

    Numerical IEEE benchmark comparison is performed
    separately after the simulation pipeline has been
    validated.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

import pytest

from src.network.benchmarks.ieee33 import (
    IEEE33Builder,
)

from src.simulation.engines.pandapower.engine import (
    PandapowerEngine,
)

from tests.network.benchmarks.helpers import (
    build_power_flow_request,
)

from src.network.benchmarks.ieee33.expected_results import (
    IEEE33ExpectedResults,
)

from src.network.benchmarks.ieee33 import IEEE33_DATASET

ABS_TOL = 1e-5

BENCHMARK_ANGLE_TOL = 1e-4
BENCHMARK_BRANCH_POWER_TOL = 1e-4
BENCHMARK_BRANCH_LOSS_TOL = 1e-4

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(scope="module")
def engine():
    """
    Create the pandapower engine.
    """

    return PandapowerEngine()

@pytest.fixture(scope="module")
def power_flow_request(
    benchmark_network,
):
    """
    Create the IEEE 33-bus power-flow request.
    """

    return build_power_flow_request(
        benchmark_network,
    )

@pytest.fixture(scope="module")
def power_flow_result(
    engine,
    power_flow_request,
):
    """
    Execute the power-flow simulation.
    """

    return engine.run(
        power_flow_request,
    )


@pytest.fixture(scope="module")
def benchmark_context():
    """
    Build the IEEE 33 benchmark once.

    Returns
    -------
    tuple
        (builder, network)
    """

    builder = IEEE33Builder()

    network = builder.build()

    return (
        builder,
        network,
    )

@pytest.fixture(scope="module")
def benchmark_builder(
    benchmark_context,
):
    return benchmark_context[0]


@pytest.fixture(scope="module")
def benchmark_network(
    benchmark_context,
):
    return benchmark_context[1]


@pytest.fixture(scope="module")
def network(
    benchmark_network,
):
    return benchmark_network

# ============================================================================
# Integration Tests
# ============================================================================


class TestIEEE33PowerFlow:
    """
    Integration tests for the IEEE 33-bus power-flow benchmark.
    """

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    def _branch_state(
        self,
        benchmark_builder,
        power_flow_result,
        branch_number: int,
    ):
        """
        Return the BranchState corresponding to the benchmark branch number.
        """

        branch_id = (
            benchmark_builder.branch_lookup[
                branch_number
            ]
        )

        return (
            power_flow_result.branch_states[
                branch_id
            ]
        )

    # -------------------------------------------------------------------------
    # Tests
    # -------------------------------------------------------------------------

    def test_engine_returns_result(
        self,
        power_flow_result,
    ):
        """
        Engine returns a PowerFlowResult.
        """

        assert power_flow_result is not None

    def test_solution_converged(
        self,
        power_flow_result,
    ):
        """
        Power-flow converged successfully.
        """

        assert power_flow_result.converged

    def test_bus_result_count(
        self,
        network,
        power_flow_result,
    ):
        """
        Every network bus has a simulation result.
        """

        assert (
            power_flow_result.bus_count
            ==
            len(network.buses)
        )

    def test_branch_result_count(
        self,
        network,
        power_flow_result,
    ):
        """
        Every network branch has a simulation result.
        """

        assert (
            power_flow_result.branch_count
            ==
            len(network.lines)
        )

    def test_generator_result_count(
        self,
        network,
        power_flow_result,
    ):
        """
        Every generator has a simulation result.
        """

        assert (
            power_flow_result.generator_count
            ==
            len(network.generators)
        )

    def test_solver_execution_time(
        self,
        power_flow_result,
    ):
        """
        Solver reports a non-negative execution time.
        """

        assert (
            power_flow_result.execution_time_seconds
            >=
            0.0
        )

    def test_network_name_preserved(
        self,
        network,
        power_flow_result,
    ):
        """
        Result refers to the solved network.
        """

        assert (
            power_flow_result.network_name
            ==
            network.name
        )

    def test_no_solver_errors(
        self,
        power_flow_result,
    ):
        """
        Successful simulations report no errors.
        """

        assert not power_flow_result.errors


    def test_minimum_bus_voltage(
        self,
        power_flow_result,
    ):
        """
        Minimum bus voltage matches the Baran & Wu benchmark.
        """

        assert abs(
            power_flow_result.minimum_bus_voltage_pu
            - IEEE33ExpectedResults.MINIMUM_BUS_VOLTAGE_PU
        ) < ABS_TOL


    def test_total_active_loss(
        self,
        power_flow_result,
    ):
        """
        Total active loss matches the benchmark.
        """

        assert abs(
            power_flow_result.total_active_loss_mw
            - IEEE33ExpectedResults.TOTAL_ACTIVE_LOSS_MW
        ) < ABS_TOL


    def test_total_generation(
        self,
        power_flow_result,
    ):
        """
        Total generated power matches the benchmark.
        """

        assert abs(
            power_flow_result.total_active_generation_mw
            - IEEE33ExpectedResults.TOTAL_ACTIVE_GENERATION_MW
        ) < ABS_TOL


    def test_bus_voltage_profile(
        self,
        benchmark_builder,
        power_flow_result,
    ):
        """
        Bus voltage magnitudes match
        the published IEEE 33 benchmark.
        """

        for (
            bus_number,
            expected_voltage,
        ) in (
            IEEE33ExpectedResults.VOLTAGE_MAGNITUDES.items()
        ):

            bus_id = benchmark_builder.bus_lookup[
                bus_number
            ]

            state = power_flow_result.bus_states[
                bus_id
            ]

            assert abs(
                state.voltage_magnitude_pu
                -
                expected_voltage
            ) < ABS_TOL


    def test_maximum_bus_voltage(
        self,
        power_flow_result,
    ):
        """
        Maximum bus voltage matches the benchmark.
        """

        assert abs(
            power_flow_result.maximum_bus_voltage_pu
            -
            IEEE33ExpectedResults.MAXIMUM_BUS_VOLTAGE_PU
        ) < ABS_TOL


    def test_average_bus_voltage(
        self,
        power_flow_result,
    ):
        """
        Average bus voltage matches the benchmark.
        """

        assert abs(
            power_flow_result.average_bus_voltage_pu
            -
            IEEE33ExpectedResults.AVERAGE_BUS_VOLTAGE_PU
        ) < ABS_TOL


    def test_total_reactive_generation(
        self,
        power_flow_result,
    ):
        """
        Total reactive generation matches the benchmark.
        """

        assert abs(
            power_flow_result.total_reactive_generation_mvar
            -
            IEEE33ExpectedResults.TOTAL_REACTIVE_GENERATION_MVAR
        ) < ABS_TOL


    def test_total_active_load(
        self,
        power_flow_result,
    ):
        """
        Total active load matches the benchmark.
        """

        assert abs(
            power_flow_result.total_active_load_mw
            -
            IEEE33ExpectedResults.TOTAL_ACTIVE_LOAD_MW
        ) < ABS_TOL

    def test_total_reactive_load(
        self,
        power_flow_result,
    ):
        """
        Total reactive load matches the benchmark.
        """

        assert abs(
            power_flow_result.total_reactive_load_mvar
            -
            IEEE33ExpectedResults.TOTAL_REACTIVE_LOAD_MVAR
        ) < ABS_TOL


    def test_total_reactive_loss(
        self,
        power_flow_result,
    ):
        """
        Total reactive loss matches the benchmark.
        """

        assert abs(
            power_flow_result.total_reactive_loss_mvar
            -
            IEEE33ExpectedResults.TOTAL_REACTIVE_LOSS_MVAR
        ) < ABS_TOL


    def test_system_power_factor(
        self,
        power_flow_result,
    ):
        """
        System power factor matches the benchmark.
        """

        assert abs(
            power_flow_result.system_power_factor
            -
            IEEE33ExpectedResults.SYSTEM_POWER_FACTOR
        ) < ABS_TOL


    def test_bus_voltage_angles(
        self,
        benchmark_builder,
        power_flow_result,
    ):
        """
        Bus voltage angles match the
        published benchmark.
        """

        for (
            bus_number,
            expected_angle,
        ) in (
            IEEE33ExpectedResults.VOLTAGE_ANGLES.items()
        ):

            bus_id = benchmark_builder.bus_lookup[
                bus_number
            ]

            state = power_flow_result.bus_states[
                bus_id
            ]

            assert abs(
                state.voltage_angle_deg
                -
                expected_angle
            ) < BENCHMARK_ANGLE_TOL


    def test_branch_power_flows(
        self,
        benchmark_builder,
        power_flow_result,
    ):
        """
        Branch active and reactive power flows match
        the published IEEE 33 benchmark.
        """

        for branch in IEEE33_DATASET.branches:

            expected = (
                IEEE33ExpectedResults.BRANCH_POWER_FLOWS[
                    (
                        branch.from_bus_number,
                        branch.to_bus_number,
                    )
                ]
            )

            state = self._branch_state(
                benchmark_builder,
                power_flow_result,
                branch.branch_number,
            )

            assert abs(
                state.active_power_from_mw
                -
                expected["p_from_mw"]
            ) < BENCHMARK_BRANCH_POWER_TOL

            assert abs(
                state.reactive_power_from_mvar
                -
                expected["q_from_mvar"]
            ) < BENCHMARK_BRANCH_POWER_TOL

            assert abs(
                state.active_power_to_mw
                -
                expected["p_to_mw"]
            ) < BENCHMARK_BRANCH_POWER_TOL

            assert abs(
                state.reactive_power_to_mvar
                -
                expected["q_to_mvar"]
            ) < BENCHMARK_BRANCH_POWER_TOL


    def test_branch_losses(
        self,
        benchmark_builder,
        power_flow_result,
    ):
        """
        Branch losses are consistent with
        the published benchmark.
        """

        for branch in IEEE33_DATASET.branches:

            expected = (
                IEEE33ExpectedResults.BRANCH_POWER_FLOWS[
                    (
                        branch.from_bus_number,
                        branch.to_bus_number,
                    )
                ]
            )

            state = self._branch_state(
                benchmark_builder,
                power_flow_result,
                branch.branch_number,
            )

            expected_active_loss = (
                expected["p_from_mw"]
                +
                expected["p_to_mw"]
            )

            expected_reactive_loss = (
                expected["q_from_mvar"]
                +
                expected["q_to_mvar"]
            )

            assert abs(
                state.active_loss_mw
                -
                expected_active_loss
            ) < BENCHMARK_BRANCH_LOSS_TOL

            assert abs(
                state.reactive_loss_mvar
                -
                expected_reactive_loss
            ) < BENCHMARK_BRANCH_LOSS_TOL