"""
GridStudio AI

Module:
    test_transformer_converter.py

Description:
    Regression tests for GridStudio Transformer ->
    pandapower Transformer conversion.

Covered assets

    * Fixed Two-Winding Transformer

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from .builders import (
    build_bus_hv,
    build_bus_1,
    build_fixed_transformer,
)


# ============================================================================
# Helpers
# ============================================================================


def _build_transformer_network(network):
    """
    Construct the minimal transformer network.
    """

    hv_bus = build_bus_hv()

    lv_bus = build_bus_1()

    network.add(hv_bus)

    network.add(lv_bus)

    transformer = build_fixed_transformer(
        hv_bus=hv_bus,
        lv_bus=lv_bus,
    )

    network.add(transformer)

    return (
        hv_bus,
        lv_bus,
        transformer,
    )


# ============================================================================
# Transformer Conversion
# ============================================================================


def test_transformer_conversion(
    converter,
    network,
):
    """
    A GridStudio transformer shall become one
    pandapower transformer.
    """

    _, _, transformer = _build_transformer_network(
        network,
    )

    conversion = converter.convert(network)

    pp_net = conversion.network

    assert len(pp_net.trafo) == 1

    row = pp_net.trafo.loc[0]

    assert row["name"] == transformer.name

    assert bool(row["in_service"])


# ============================================================================
# Transformer Ratings
# ============================================================================


def test_transformer_ratings(
    converter,
    network,
):
    """
    Transformer electrical ratings shall be preserved.
    """

    _, _, transformer = _build_transformer_network(
        network,
    )

    conversion = converter.convert(network)

    row = conversion.network.trafo.loc[0]

    assert (
        row["sn_mva"]
        ==
        transformer.rated_power_mva
    )

    assert (
        row["vn_hv_kv"]
        ==
        transformer.high_voltage_kv
    )

    assert (
        row["vn_lv_kv"]
        ==
        transformer.low_voltage_kv
    )


# ============================================================================
# Impedance Model
# ============================================================================


def test_transformer_impedance(
    converter,
    network,
):
    """
    Transformer impedance model shall be preserved.
    """

    _, _, transformer = _build_transformer_network(
        network,
    )

    conversion = converter.convert(network)

    row = conversion.network.trafo.loc[0]

    assert (
        row["vk_percent"]
        ==
        transformer.impedance_percent
    )

    assert (
        row["vkr_percent"]
        ==
        transformer.resistance_percent
    )


# ============================================================================
# Bus Mapping
# ============================================================================


def test_transformer_bus_mapping(
    converter,
    network,
):
    """
    Transformer terminal buses shall map to the
    correct pandapower buses.
    """

    hv_bus, lv_bus, _ = _build_transformer_network(
        network,
    )

    conversion = converter.convert(network)

    row = conversion.network.trafo.loc[0]

    assert (
        row["hv_bus"]
        ==
        conversion.bus_indices[
            hv_bus.id
        ]
    )

    assert (
        row["lv_bus"]
        ==
        conversion.bus_indices[
            lv_bus.id
        ]
    )


# ============================================================================
# UUID Mapping
# ============================================================================


def test_transformer_mapping(
    converter,
    network,
):
    """
    Transformer shall participate in converter
    element mapping.
    """

    _, _, transformer = _build_transformer_network(
        network,
    )

    conversion = converter.convert(network)

    mapping = conversion.element_mappings[
        transformer.id
    ]

    assert mapping.table == "trafo"

    assert mapping.index == 0

    assert (
        conversion.element_indices[
            transformer.id
        ]
        == 0
    )


# ============================================================================
# Disabled Transformer
# ============================================================================


def test_disabled_transformer_conversion(
    converter,
    network,
):
    """
    Disabled transformers shall become
    out-of-service pandapower transformers.
    """

    hv_bus = build_bus_hv()

    lv_bus = build_bus_1()

    network.add(hv_bus)

    network.add(lv_bus)

    transformer = build_fixed_transformer(
        hv_bus=hv_bus,
        lv_bus=lv_bus,
        enabled=False,
    )

    network.add(transformer)

    conversion = converter.convert(network)

    row = conversion.network.trafo.loc[0]

    assert not bool(
        row["in_service"]
    )


# ============================================================================
# Empty Network
# ============================================================================


def test_no_transformers(
    converter,
    network,
):
    """
    A network without transformers shall produce
    an empty pandapower transformer table.
    """

    conversion = converter.convert(network)

    assert conversion.network.trafo.empty