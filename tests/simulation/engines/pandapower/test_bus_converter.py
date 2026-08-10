"""
GridStudio AI

Module:
    test_bus_converter.py

Description:
    Regression tests for GridStudio Bus -> pandapower bus
    conversion.

    These tests verify only bus conversion behaviour and the
    associated mapping infrastructure.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from .builders import (
    build_bus_hv,
    build_bus_1,
    build_bus_2,
)


# ============================================================================
# Helpers
# ============================================================================


def _build_three_bus_network(network):
    """
    Populate a network with the canonical three-bus topology.

    Returns
    -------
    tuple
        (hv_bus, bus1, bus2)
    """

    hv_bus = build_bus_hv()
    bus1 = build_bus_1()
    bus2 = build_bus_2()

    network.add(hv_bus)
    network.add(bus1)
    network.add(bus2)

    return (
        hv_bus,
        bus1,
        bus2,
    )


# ============================================================================
# Bus Conversion
# ============================================================================


def test_bus_conversion(
    converter,
    network,
):
    """
    GridStudio buses shall be converted to pandapower buses.
    """

    _build_three_bus_network(network)

    conversion = converter.convert(network)

    pp_net = conversion.network

    assert len(pp_net.bus) == 3

    expected = [
        ("Bus HV", 33.0),
        ("Bus 1", 11.0),
        ("Bus 2", 11.0),
    ]

    for index, (name, voltage) in enumerate(expected):

        row = pp_net.bus.loc[index]

        assert row["name"] == name
        assert row["vn_kv"] == voltage
        assert bool(row["in_service"])


# ============================================================================
# Bus UUID Mapping
# ============================================================================


def test_bus_uuid_mapping(
    converter,
    network,
):
    """
    Every GridStudio bus shall be assigned a pandapower
    bus index.
    """

    buses = _build_three_bus_network(network)

    conversion = converter.convert(network)

    for expected_index, bus in enumerate(buses):

        assert (
            conversion.bus_indices[bus.id]
            == expected_index
        )


# ============================================================================
# Element Mapping
# ============================================================================


def test_bus_element_mapping(
    converter,
    network,
):
    """
    Bus element mappings shall remain internally
    consistent.
    """

    buses = _build_three_bus_network(network)

    conversion = converter.convert(network)

    for bus in buses:

        mapping = conversion.element_mappings[
            bus.id
        ]

        assert mapping.table == "bus"

        assert (
            mapping.index
            ==
            conversion.bus_indices[bus.id]
        )

        assert (
            mapping.index
            ==
            conversion.element_indices[bus.id]
        )


# ============================================================================
# Disabled Bus
# ============================================================================


def test_disabled_bus_conversion(
    converter,
    network,
):
    """
    Disabled buses shall be converted as
    out-of-service pandapower buses.
    """

    bus = build_bus_1(
        enabled=False,
    )

    network.add(bus)

    conversion = converter.convert(network)

    pp_net = conversion.network

    assert len(pp_net.bus) == 1

    row = pp_net.bus.loc[0]

    assert row["name"] == "Bus 1"

    assert not bool(row["in_service"])


# ============================================================================
# Empty Network
# ============================================================================


def test_empty_network_conversion(
    converter,
    network,
):
    """
    Converting an empty network shall produce an empty
    pandapower network.
    """

    conversion = converter.convert(network)

    pp_net = conversion.network

    assert pp_net.bus.empty

    assert len(pp_net.bus) == 0