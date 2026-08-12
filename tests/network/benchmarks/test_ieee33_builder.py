"""
GridStudio AI

Module:
    test_ieee33_builder.py

Description:
    Unit tests for the IEEE 33-bus benchmark builder.

    These tests verify that the benchmark dataset is
    correctly translated into a valid GridStudio Network.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

import pytest

from src.domain.network.network import Network

from src.core.enums.electrical import BusType

from src.network.benchmarks.ieee33.builder import (
    IEEE33Builder,
)

from src.network.benchmarks.ieee33.data import (
    IEEE33_DATASET,
)
from src.network.benchmarks.ieee33.metadata import IEEE33_METADATA


@pytest.fixture(scope="module")
def builder() -> IEEE33Builder:
    """
    Return an IEEE33 benchmark builder.
    """

    return IEEE33Builder()


@pytest.fixture(scope="module")
def network(builder) -> Network:
    """
    Build the IEEE33 benchmark network.
    """

    return builder.build()


class TestIEEE33Builder:
    """
    Tests for IEEE33Builder.
    """

    def test_base_power_propagated(
        self,
        network,
    ) -> None:
        """
        Network base power is propagated from benchmark metadata.
        """
        assert network.base_power_mva == IEEE33_METADATA.base_power_mva

    def test_build_returns_network(
        self,
        network,
    ):
        """
        Builder returns a Network instance.
        """

        assert isinstance(
            network,
            Network,
        )    


    def test_network_name(
        self,
        network,
    ):
        """
        Network metadata is assigned.
        """

        assert network.name


    def test_bus_count(
        self,
        network,
    ):
        """
        All benchmark buses are created.
        """

        assert (
            len(network.buses)
            ==
            len(IEEE33_DATASET.buses)
        )


    def test_line_count(
        self,
        network,
    ):
        """
        All benchmark branches are created.
        """

        assert (
            len(network.lines)
            ==
            len(IEEE33_DATASET.branches)
        )

    def test_load_count(
        self,
        network,
    ):
        """
        All benchmark loads are created.
        """

        assert (
            len(network.loads)
            ==
            len(IEEE33_DATASET.loads)
        )

    def test_generator_count(
        self,
        network,
    ):
        """
        All benchmark generators are created.
        """

        assert (
            len(network.generators)
            ==
            len(IEEE33_DATASET.generators)
        )

    def test_single_slack_bus(
        self,
        network,
    ):
        """
        Exactly one slack bus exists.
        """

        slack_buses = [
            bus
            for bus in network.buses
            if bus.bus_type == BusType.SLACK
        ]

        if len(slack_buses) != 1:
            raise ValueError(
                f"Expected exactly one slack bus, "
                f"found {len(slack_buses)}"
            )

    def test_network_reference_validation(
        self,
        network,
    ):
        """
        Network references are valid.
        """

        network.validate_references()

    def test_unique_element_ids(
        self,
        network,
    ):
        """
        Every network element has a unique UUID.
        """

        ids = {
            *(bus.id for bus in network.buses),
            *(line.id for line in network.lines),
            *(load.id for load in network.loads),
            *(generator.id for generator in network.generators),
        }

        expected_count = (
            len(network.buses)
            + len(network.lines)
            + len(network.loads)
            + len(network.generators)
        )

        assert len(ids) == expected_count

    def test_build_is_repeatable(
        self,
        builder,
    ):
        """
        Multiple builds produce equivalent networks.
        """

        network1 = builder.build()

        network2 = builder.build()

        assert len(network1.buses) == len(network2.buses)

        assert len(network1.lines) == len(network2.lines)

        assert len(network1.loads) == len(network2.loads)

        assert len(network1.generators) == len(network2.generators)


    def test_metadata_propagated_to_network(
        self,
        network,
    ) -> None:
        assert network.base_power_mva == IEEE33_METADATA.base_power_mva
        assert network.base_frequency_hz == (
            IEEE33_METADATA.base_frequency_hz
        )