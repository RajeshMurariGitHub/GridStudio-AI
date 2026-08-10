"""
GridStudio AI

Module:
    test_converter_mapping.py

Description:
    Regression tests for converter bookkeeping.

    These tests verify that every GridStudio asset
    receives a valid pandapower mapping.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from .builders import (
    build_complete_network,
)


# ============================================================================
# Complete Mapping
# ============================================================================


def test_complete_converter_mapping(
    converter,
):
    """
    Every GridStudio asset shall receive a valid
    converter mapping.
    """

    network = build_complete_network()

    conversion = converter.convert(network)

    #
    # ------------------------------------------------------------------
    # Buses
    # ------------------------------------------------------------------
    #

    for bus in network.buses:

        assert bus.id in conversion.bus_indices

        index = conversion.bus_indices[bus.id]

        assert index >= 0

        assert index < len(
            conversion.network.bus
        )

    #
    # ------------------------------------------------------------------
    # Every mapped asset
    # ------------------------------------------------------------------
    #

    assets = (
        list(network.lines)
        + list(network.loads)
        + list(network.generators)
        + list(network.shunts)
        + list(network.transformers)
        + list(network.switches)
        + list(network.solar)
        + list(network.wind)
        + list(network.batteries)
        + list(network.evs)
    )

    for asset in assets:

        assert (
            asset.id
            in
            conversion.element_indices
        )

        assert (
            asset.id
            in
            conversion.element_mappings
        )

        mapping = (
            conversion.element_mappings[
                asset.id
            ]
        )

        assert mapping.index >= 0

        assert isinstance(
            mapping.table,
            str,
        )

# ============================================================================
# Bus Indices
# ============================================================================


def test_bus_indices_unique(
    converter,
):
    """
    Every bus shall receive a unique
    pandapower index.
    """

    network = build_complete_network()

    conversion = converter.convert(network)

    indices = list(
        conversion.bus_indices.values()
    )

    assert len(indices) == len(set(indices))


# ============================================================================
# Element Indices
# ============================================================================


def test_element_indices_unique(
    converter,
):
    """
    Every GridStudio element shall receive
    exactly one converter index.
    """

    network = build_complete_network()

    conversion = converter.convert(network)

    assert len(
        conversion.element_indices
    ) == len(
        conversion.element_mappings
    )


# ============================================================================
# Mapping Tables
# ============================================================================


def test_mapping_tables(
    converter,
):
    """
    Mapping table names shall be valid.
    """

    network = build_complete_network()

    conversion = converter.convert(network)

    valid_tables = {

        "line",

        "bus",

        "load",

        "sgen",

        "gen",

        "storage",

        "switch",

        "trafo",

        "shunt",

        "ext_grid",
    }

    for mapping in (
        conversion.element_mappings.values()
    ):

        assert (
            mapping.table
            in
            valid_tables
        )


# ============================================================================
# Mapping Consistency
# ============================================================================


def test_mapping_consistency(
    converter,
):
    """
    Converter bookkeeping shall remain
    internally consistent.
    """

    network = build_complete_network()

    conversion = converter.convert(network)

    assert len(
        conversion.element_indices
    ) == len(
        set(
            conversion.element_indices.keys()
        )
    )

    assert len(
        conversion.element_mappings
    ) == len(
        set(
            conversion.element_mappings.keys()
        )
    )


# ============================================================================
# Empty Network
# ============================================================================


def test_empty_network_mapping(
    converter,
    network,
):
    """
    Empty networks shall produce
    empty mappings.
    """

    conversion = converter.convert(network)

    assert not conversion.bus_indices

    assert not conversion.element_indices

    assert not conversion.element_mappings


