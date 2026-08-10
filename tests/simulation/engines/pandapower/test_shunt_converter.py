"""
GridStudio AI

Module:
    test_shunt_converter.py

Description:
    Regression tests for GridStudio Shunt ->
    pandapower Shunt conversion.

Covered assets

    * Capacitor Bank
    * Shunt Reactor

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from .builders import (
    build_bus_1,
    build_bus_2,
    build_capacitor_bank,
    build_shunt_reactor,
)


# ============================================================================
# Helpers
# ============================================================================


def _build_shunt_network(network):
    """
    Build a representative shunt network.
    """

    bus1 = build_bus_1()

    bus2 = build_bus_2()

    network.add(bus1)

    network.add(bus2)

    capacitor = build_capacitor_bank(bus2)

    reactor = build_shunt_reactor(bus1)

    network.add(capacitor)

    network.add(reactor)

    return (
        capacitor,
        reactor,
    )


# ============================================================================
# Shunt Conversion
# ============================================================================


def test_shunt_conversion(
    converter,
    network,
):
    """
    Capacitor banks and shunt reactors shall be converted
    to pandapower shunts.
    """

    capacitor, reactor = _build_shunt_network(
        network,
    )

    conversion = converter.convert(network)

    pp_net = conversion.network

    assert len(pp_net.shunt) == 2

    assert (
        capacitor.name
        in
        pp_net.shunt["name"].values
    )

    assert (
        reactor.name
        in
        pp_net.shunt["name"].values
    )


# ============================================================================
# Capacitor Sign Convention
# ============================================================================


def test_capacitor_sign_convention(
    converter,
    network,
):
    """
    Capacitor banks shall inject negative reactive power
    into pandapower.
    """

    capacitor, _ = _build_shunt_network(
        network,
    )

    conversion = converter.convert(network)

    row = conversion.network.shunt.loc[
        conversion.element_indices[
            capacitor.id
        ]
    ]

    #
    # Capacitor → negative Q
    #

    assert row["q_mvar"] < 0.0

    assert row["step"] == capacitor.active_steps


# ============================================================================
# Reactor Sign Convention
# ============================================================================


def test_reactor_sign_convention(
    converter,
    network,
):
    """
    Reactors shall consume reactive power and therefore
    appear as positive Q in pandapower.
    """

    _, reactor = _build_shunt_network(
        network,
    )

    conversion = converter.convert(network)

    row = conversion.network.shunt.loc[
        conversion.element_indices[
            reactor.id
        ]
    ]

    assert row["q_mvar"] > 0.0

    assert row["step"] == reactor.active_steps


# ============================================================================
# Step Conversion
# ============================================================================


def test_shunt_step_conversion(
    converter,
    network,
):
    """
    Active step count shall be preserved.
    """

    capacitor, reactor = _build_shunt_network(
        network,
    )

    conversion = converter.convert(network)

    pp_net = conversion.network

    cap = pp_net.shunt.loc[
        conversion.element_indices[
            capacitor.id
        ]
    ]

    reac = pp_net.shunt.loc[
        conversion.element_indices[
            reactor.id
        ]
    ]

    assert (
        cap["step"]
        ==
        capacitor.active_steps
    )

    assert (
        reac["step"]
        ==
        reactor.active_steps
    )

    assert (
        cap["max_step"]
        ==
        capacitor.step_count
    )

    assert (
        reac["max_step"]
        ==
        reactor.step_count
    )


# ============================================================================
# UUID Mapping
# ============================================================================


def test_shunt_mapping(
    converter,
    network,
):
    """
    Shunts shall participate in converter element mapping.
    """

    capacitor, reactor = _build_shunt_network(
        network,
    )

    conversion = converter.convert(network)

    mapping = conversion.element_mappings

    assert (
        mapping[
            capacitor.id
        ].table
        ==
        "shunt"
    )

    assert (
        mapping[
            reactor.id
        ].table
        ==
        "shunt"
    )

    assert (
        mapping[
            capacitor.id
        ].index
        >=
        0
    )

    assert (
        mapping[
            reactor.id
        ].index
        >=
        0
    )


# ============================================================================
# Disabled Shunt
# ============================================================================


def test_disabled_shunt_conversion(
    converter,
    network,
):
    """
    Disabled shunts shall become out-of-service
    pandapower shunts.
    """

    bus = build_bus_2()

    network.add(bus)

    capacitor = build_capacitor_bank(
        bus,
        enabled=False,
    )

    network.add(capacitor)

    conversion = converter.convert(network)

    row = conversion.network.shunt.loc[0]

    assert not bool(
        row["in_service"]
    )