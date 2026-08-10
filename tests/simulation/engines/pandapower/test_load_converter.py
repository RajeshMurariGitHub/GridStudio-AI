"""
GridStudio AI

Module:
    test_load_converter.py

Description:
    Regression tests for GridStudio Load ->
    pandapower Load conversion.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from .builders import (
    build_bus_2,
    build_load,
)


# ============================================================================
# Helpers
# ============================================================================


def _build_load_network(network):
    """
    Construct the minimal network required for load conversion.
    """

    bus = build_bus_2()

    network.add(bus)

    load = build_load(bus)

    network.add(load)

    return (
        bus,
        load,
    )


# ============================================================================
# Load Conversion
# ============================================================================


def test_load_conversion(
    converter,
    network,
):
    """
    GridStudio Load shall be converted into one
    pandapower load.
    """

    bus, load = _build_load_network(network)

    conversion = converter.convert(network)

    pp_net = conversion.network

    assert len(pp_net.load) == 1

    row = pp_net.load.loc[0]

    assert row["name"] == load.name

    assert (
        row["bus"]
        ==
        conversion.bus_indices[bus.id]
    )

    #
    # GridStudio uses negative injections.
    # pandapower expects positive demand.
    #

    assert row["p_mw"] == abs(load.active_power_mw)

    assert row["q_mvar"] == abs(load.reactive_power_mvar)

    assert row["scaling"] == load.scaling

    assert bool(row["in_service"])


# ============================================================================
# Sign Convention
# ============================================================================


def test_load_sign_convention(
    converter,
    network,
):
    """
    Verify GridStudio load sign convention is translated
    correctly to pandapower.
    """

    _, load = _build_load_network(network)

    conversion = converter.convert(network)

    row = conversion.network.load.loc[0]

    #
    # Load should appear as positive demand.
    #

    assert row["p_mw"] > 0.0

    assert row["q_mvar"] > 0.0

    assert row["p_mw"] == -load.active_power_mw

    assert row["q_mvar"] == -load.reactive_power_mvar


# ============================================================================
# Scaling
# ============================================================================


def test_load_scaling(
    converter,
    network,
):
    """
    Scaling factor shall be preserved.
    """

    _, load = _build_load_network(network)

    conversion = converter.convert(network)

    row = conversion.network.load.loc[0]

    assert row["scaling"] == load.scaling


# ============================================================================
# UUID Mapping
# ============================================================================


def test_load_mapping(
    converter,
    network,
):
    """
    Load UUID shall map to the pandapower load table.
    """

    _, load = _build_load_network(network)

    conversion = converter.convert(network)

    mapping = conversion.element_mappings[
        load.id
    ]

    assert mapping.table == "load"

    assert mapping.index == 0

    assert (
        conversion.element_indices[load.id]
        == 0
    )


# ============================================================================
# Disabled Load
# ============================================================================


def test_disabled_load_conversion(
    converter,
    network,
):
    """
    Disabled loads shall become out-of-service
    pandapower loads.
    """

    bus = build_bus_2()

    network.add(bus)

    load = build_load(
        bus,
        enabled=False,
    )

    network.add(load)

    conversion = converter.convert(network)

    row = conversion.network.load.loc[0]

    assert not bool(row["in_service"])


# ============================================================================
# Empty Network
# ============================================================================


def test_no_loads(
    converter,
    network,
):
    """
    Network without loads shall produce an empty
    pandapower load table.
    """

    conversion = converter.convert(network)

    assert conversion.network.load.empty