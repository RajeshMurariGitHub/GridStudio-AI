"""
Unit tests for PandapowerResultMapper.
"""

from __future__ import annotations

from uuid import UUID

import pandapower as pp
import pytest

from src.domain.network.network import Network
from src.simulation.engines.pandapower.converter import (
    PandapowerConverter,
)
from src.simulation.engines.pandapower.mapping_results import (
    PandapowerMappingResult,
)
from src.simulation.engines.pandapower.result_mapper import (
    PandapowerConversion,
    PandapowerResultMapper,
)

from .builders import (
    build_complete_network,
)

from tests.network.benchmarks.helpers import (
    build_reference_source,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mapped_network():
    """
    Build and solve a complete network.
    """

    network = build_complete_network()

    reference_source = (
        build_reference_source(
            network,
        )
    )

    conversion = (
        PandapowerConverter.convert(
            network=network,
            reference_sources=(
                reference_source,
            ),
        )
    )

    pp.runpp(
        conversion.network,
    )

    mapper = (
        PandapowerResultMapper()
    )

    result = mapper.map(
        conversion.network,
        conversion,
    )

    return (
        network,
        conversion,
        result,
    )

# =============================================================================
# Result Mapper Tests
# =============================================================================


class TestPandapowerResultMapper:
    """
    Unit tests for PandapowerResultMapper.
    """

    def test_map_bus_results(
        self,
        mapped_network: tuple[
            Network,
            PandapowerConversion,
            PandapowerMappingResult],
    ) -> None:
        """
        Bus results should be mapped into
        BusState objects.
        """

        network, conversion, result = mapped_network

        assert len(result.bus_states) == len(
            network.buses
        )

        for state in result.bus_states.values():

            assert state.voltage_magnitude_pu is not None

            assert state.voltage_angle_deg is not None

            assert state.energized is True

    def test_map_branch_results(
        self,
        mapped_network: tuple[Network, PandapowerConversion, PandapowerMappingResult],
    ) -> None:
        """
        Branch results should be mapped into
        BranchState objects.
        """

        network, conversion, result = mapped_network

        assert len(result.branch_states) == len(
            network.lines
        )

        for state in result.branch_states.values():

            assert state.loading_percent >= 0.0

            assert state.active_power_from_mw is not None

            assert state.active_power_to_mw is not None

            #assert state.online is True

    def test_map_transformer_results(
        self,
        mapped_network: tuple[Network, PandapowerConversion, PandapowerMappingResult],
    ) -> None:
        """
        Transformer results should be mapped
        into TransformerState objects.
        """

        network, conversion, result = mapped_network

        assert len(
            result.transformer_states
        ) == len(
            network.transformers
        )

        for state in result.transformer_states.values():

            assert state.loading_percent >= 0.0
            assert state.tap_position is not None

            #assert state.active_power_hv_mw is not None

            #assert state.active_power_lv_mw is not None

            #assert state.online is True


    def test_map_load_results(
        self,
        mapped_network: tuple[Network, PandapowerConversion, PandapowerMappingResult],
    ) -> None:
        """
        Load results should be mapped into
        LoadState objects.
        """

        network, conversion, result = mapped_network

        assert len(result.load_states) == len(
            network.loads
        )


        for state in result.load_states.values():

            assert state.active_power_mw >= 0.0

            assert state.reactive_power_mvar is not None

            assert state.online is True

    def test_map_generator_results(
        self,
        mapped_network: tuple[Network, PandapowerConversion, PandapowerMappingResult],
    ) -> None:
        """
        Generator results should be mapped into
        GeneratorState objects.
        """

        network, conversion, result = mapped_network

        mapped_generator_assets = (
            len(result.generator_states)
            + len(result.solar_states)
            + len(result.wind_states)
        )

        expected_generator_assets = len(
            network.generators
        )

        assert mapped_generator_assets == (
            expected_generator_assets
        )

        for state in result.generator_states.values():

            assert state.active_power_mw is not None

            assert state.reactive_power_mvar is not None

            assert state.online is True

    def test_map_storage_results(
        self,
        mapped_network: tuple[Network, PandapowerConversion, PandapowerMappingResult],
    ) -> None:
        """
        Storage assets should be mapped into
        BatteryState and EVState objects.
        """

        network, conversion, result = mapped_network

        assert len(
            result.battery_states
        ) == len(
            network.batteries
        )

        assert len(
            result.ev_states
        ) == len(
            network.evs
        )

        assert len(
            result.battery_states
        ) == len(
            network.batteries
        )

        assert len(
            result.ev_states
        ) == len(
            network.evs
        )

        for state in result.battery_states.values():

            assert state.active_power_mw is not None

            assert state.reactive_power_mvar

            #assert state.state_of_charge_percent is not None

            assert state.online is True

        for state in result.ev_states.values():

            assert state.active_power_mw is not None

            assert state.reactive_power_mvar is not None

            #assert state.state_of_charge_percent is not None

            assert state.online is True

    def test_map_shunt_results(
        self,
        mapped_network: tuple[Network, PandapowerConversion, PandapowerMappingResult],
    ) -> None:
        """
        Shunt results should be mapped into
        ShuntState objects.
        """

        network, conversion, result = mapped_network

        assert len(
            result.shunt_states
        ) == len(
            network.shunts
        )

        for state in result.shunt_states.values():

            assert state.reactive_power_mvar is not None

            assert state.online is True

    def test_statistics_are_computed(
        self,
        mapped_network: tuple[Network, PandapowerConversion, PandapowerMappingResult],
    ) -> None:
        """
        Aggregate statistics should be
        available in the mapping result.
        """

        network, conversion, result = mapped_network

        statistics = result.statistics

        expected = {

            "total_active_generation_mw",

            "total_reactive_generation_mvar",

            "total_active_load_mw",

            "total_reactive_load_mvar",

            "total_active_loss_mw",

            "total_reactive_loss_mvar",

            "minimum_bus_voltage_pu",

            "maximum_bus_voltage_pu",

            "average_bus_voltage_pu",

            "maximum_branch_loading_percent",

            "system_power_factor",

        }

        assert expected.issubset(
            statistics.keys()
        )

        ext_grid = conversion.network.res_ext_grid

        active_power = ext_grid.p_mw.sum()
        reactive_power = ext_grid.q_mvar.sum()

        apparent_power = (
            active_power ** 2
            + reactive_power ** 2
        ) ** 0.5

        expected_power_factor = (
            abs(active_power) / apparent_power
            if apparent_power > 0
            else 1.0
        )

        assert statistics[
            "system_power_factor"
        ] == pytest.approx(
            expected_power_factor,
        )


    def test_convergence_is_mapped(
        self,
        mapped_network: tuple[Network, PandapowerConversion, PandapowerMappingResult,],
    ) -> None:
        """
        Convergence information should be
        populated.
        """

        network, conversion, result = mapped_network

        convergence = result.convergence

        assert convergence is not None

        assert convergence.converged is True

        assert convergence.iterations is not None

        assert convergence.iterations >= 1

        assert convergence.tolerance is not None

        assert convergence.tolerance == pytest.approx(
            1e-8,
        )

    def test_map_returns_mapping_result(
        self,
        mapped_network: tuple[Network, PandapowerConversion, PandapowerMappingResult],
    ) -> None:
        """
        The public map() API should return a
        PandapowerMappingResult instance.
        """

        network, conversion, result = mapped_network

        assert isinstance(
            result,
            PandapowerMappingResult,
        )

        assert result.statistics

        assert result.convergence is not None

    def test_map_complete_network(
        self,
        mapped_network: tuple[Network, PandapowerConversion, PandapowerMappingResult],
    ) -> None:
        """
        Mapping a solved network should produce
        a complete and internally consistent
        mapping result.
        """

        network, conversion, result = mapped_network

        #
        # Every converted asset should have
        # a corresponding mapped state.
        #

        assert len(result.bus_states) == len(
            network.buses
        )

        assert len(result.branch_states) == len(
            network.lines
        )

        assert len(result.transformer_states) == len(
            network.transformers
        )

        assert len(result.load_states) == len(
            network.loads
        )

        mapped_generator_assets = (
            len(result.generator_states)
            + len(result.solar_states)
            + len(result.wind_states)
        )

        assert mapped_generator_assets == len(
            network.generators
)

        assert len(result.battery_states) == len(
            network.batteries
        )

        assert len(result.ev_states) == len(
            network.evs
        )

        assert len(result.shunt_states) == len(
            network.shunts
        )

        #
        # Statistics should exist.
        #

        assert result.statistics

        #
        # Solver should have converged.
        #

        assert result.convergence.converged

        #
        # Optional state collections should
        # always exist.
        #

        assert isinstance(
            result.solar_states,
            dict,
        )

        assert isinstance(
            result.wind_states,
            dict,
        )

    def test_all_state_keys_are_valid_uuids(
        self,
        mapped_network: tuple[Network, PandapowerConversion, PandapowerMappingResult],
    ) -> None:
        """
        Every mapped state dictionary should
        use GridStudio UUIDs as keys.
        """

        network, conversion, result = mapped_network

        state_collections = (

            result.bus_states,

            result.branch_states,

            result.transformer_states,

            result.load_states,

            result.generator_states,

            result.solar_states,

            result.wind_states,

            result.battery_states,

            result.ev_states,

            result.shunt_states,

        )

        for collection in state_collections:

            for key in collection.keys():

                assert isinstance(
                    key,
                    UUID,
                )

    def test_every_mapping_is_consumed(
        self,
        mapped_network: tuple[Network, PandapowerConversion, PandapowerMappingResult],
    ) -> None:
        """
        Every element registered during
        conversion should be represented
        in the mapped result.
        """

        network, conversion, result = mapped_network

        mapped_assets = (

            len(result.bus_states)

            + len(result.branch_states)

            + len(result.transformer_states)

            + len(result.load_states)

            + len(result.generator_states)

            + len(result.solar_states)

            + len(result.wind_states)

            + len(result.battery_states)

            + len(result.ev_states)

            + len(result.shunt_states)

        )

        expected_assets = (

            len(network.buses)

            + len(network.lines)

            + len(network.transformers)

            + len(network.loads)

            + len(network.generators)

            + len(network.batteries)

            + len(network.evs)

            + len(network.shunts)

        )

        assert mapped_assets == expected_assets

    def test_state_keys_match_state_asset_ids(
        self,
        mapped_network: tuple[
            Network,
            PandapowerConversion,
            PandapowerMappingResult,
        ],
    ) -> None:
        """
        Every mapped state dictionary key must match
        the asset_id stored in the corresponding state.
        """

        _, _, result = mapped_network

        state_collections = (
            result.bus_states,
            result.branch_states,
            result.transformer_states,
            result.load_states,
            result.generator_states,
            result.solar_states,
            result.wind_states,
            result.battery_states,
            result.ev_states,
            result.shunt_states,
        )

        for collection in state_collections:
            for asset_id, state in collection.items():
                assert state.asset_id == asset_id

