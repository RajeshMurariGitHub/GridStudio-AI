"""
GridStudio AI

Module:
    test_line_converter.py

Description:
    Regression tests for GridStudio Line -> pandapower Line
    conversion.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from .builders import (
    build_bus_1,
    build_bus_2,
    build_line,
)


# ============================================================================
# Helpers
# ============================================================================


def _build_line_network(network):
    """
    Build the minimal network required for line conversion.
    """

    bus1 = build_bus_1()
    bus2 = build_bus_2()

    network.add(bus1)
    network.add(bus2)

    line = build_line(
        from_bus=bus1,
        to_bus=bus2,
    )

    network.add(line)

    return (
        bus1,
        bus2,
        line,
    )


# ============================================================================
# Line Conversion
# ============================================================================


def test_line_conversion(
    converter,
    network,
):
    """
    GridStudio Line shall be converted to a pandapower line.
    """

    bus1, bus2, line = _build_line_network(network)

    conversion = converter.convert(network)

    pp_net = conversion.network

    assert len(pp_net.line) == 1

    row = pp_net.line.loc[0]

    assert row["name"] == line.name

    assert (
        row["from_bus"]
        ==
        conversion.bus_indices[bus1.id]
    )

    assert (
        row["to_bus"]
        ==
        conversion.bus_indices[bus2.id]
    )

    assert row["length_km"] == line.length_km

    assert bool(row["in_service"])


# ============================================================================
# Electrical Parameters
# ============================================================================


def test_line_impedance_conversion(
    converter,
    network,
):
    """
    Line electrical parameters shall be preserved.
    """

    _, _, line = _build_line_network(network)

    conversion = converter.convert(network)

    row = conversion.network.line.loc[0]

    assert (
        row["r_ohm_per_km"]
        == line.parameters.r1_ohm_per_km
    )

    assert (
        row["x_ohm_per_km"]
        == line.parameters.x1_ohm_per_km
    )

    assert (
        row["c_nf_per_km"]
        == line.parameters.c1_nf_per_km
    )

    assert (
        row["max_i_ka"]
        == line.maximum_current_ka
    )


# ============================================================================
# UUID Mapping
# ============================================================================


def test_line_mapping(
    converter,
    network,
):
    """
    Line UUID shall map to the pandapower line table.
    """

    _, _, line = _build_line_network(network)

    conversion = converter.convert(network)

    mapping = conversion.element_mappings[
        line.id
    ]

    assert mapping.table == "line"

    assert mapping.index == 0

    assert (
        conversion.element_indices[line.id]
        == 0
    )


# ============================================================================
# Disabled Line
# ============================================================================


def test_disabled_line_conversion(
    converter,
    network,
):
    """
    Disabled lines shall become out-of-service
    pandapower lines.
    """

    bus1 = build_bus_1()
    bus2 = build_bus_2()

    network.add(bus1)
    network.add(bus2)

    line = build_line(
        from_bus=bus1,
        to_bus=bus2,
        enabled=False,
    )

    network.add(line)

    conversion = converter.convert(network)

    row = conversion.network.line.loc[0]

    assert not bool(row["in_service"])


# ============================================================================
# Empty Network
# ============================================================================


def test_no_lines(
    converter,
    network,
):
    """
    A network without lines shall produce an empty
    pandapower line table.
    """

    conversion = converter.convert(network)

    assert conversion.network.line.empty