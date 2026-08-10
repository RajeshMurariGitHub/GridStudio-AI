"""
GridStudio AI

Module:
    test_switch_converter.py

Description:
    Regression tests for GridStudio Switch ->
    pandapower Switch conversion.

Covered assets

    * Closed Switch
    * Open Switch
    * Disabled Switch

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from .builders import (
    build_bus_1,
    build_bus_2,
    build_closed_switch,
    build_open_switch,
    build_disabled_switch,
)


# ============================================================================
# Helpers
# ============================================================================


def _build_switch_network(network):
    """
    Construct the canonical switch network.
    """

    bus1 = build_bus_1()

    bus2 = build_bus_2()

    network.add(bus1)

    network.add(bus2)

    closed_switch = build_closed_switch(
        bus1,
        bus2,
    )

    open_switch = build_open_switch(
        bus1,
        bus2,
    )

    disabled_switch = build_disabled_switch(
        bus1,
        bus2,
    )

    network.add(closed_switch)

    network.add(open_switch)

    network.add(disabled_switch)

    return (
        closed_switch,
        open_switch,
        disabled_switch,
    )


# ============================================================================
# Switch Conversion
# ============================================================================


def test_switch_conversion(
    converter,
    network,
):
    """
    GridStudio switches shall become pandapower switches.
    """

    (
        closed_switch,
        open_switch,
        disabled_switch,
    ) = _build_switch_network(network)

    conversion = converter.convert(network)

    pp_net = conversion.network

    assert len(pp_net.switch) == 3

    names = set(pp_net.switch["name"])

    assert closed_switch.name in names
    assert open_switch.name in names
    assert disabled_switch.name in names


# ============================================================================
# Closed Switch
# ============================================================================


def test_closed_switch(
    converter,
    network,
):
    """
    Closed switches shall remain closed.
    """

    (
        closed_switch,
        _,
        _,
    ) = _build_switch_network(network)

    conversion = converter.convert(network)

    row = conversion.network.switch.loc[
        conversion.element_indices[
            closed_switch.id
        ]
    ]

    assert bool(row["closed"])

    assert row["in_ka"] == closed_switch.rated_current_ka


# ============================================================================
# Open Switch
# ============================================================================


def test_open_switch(
    converter,
    network,
):
    """
    Open switches shall remain open.
    """

    (
        _,
        open_switch,
        _,
    ) = _build_switch_network(network)

    conversion = converter.convert(network)

    row = conversion.network.switch.loc[
        conversion.element_indices[
            open_switch.id
        ]
    ]

    assert not bool(row["closed"])

    assert row["in_ka"] == open_switch.rated_current_ka


# ============================================================================
# Disabled Switch
# ============================================================================


def test_disabled_switch(
    converter,
    network,
):
    """
    Disabled switches shall become open switches.
    """

    (
        _,
        _,
        disabled_switch,
    ) = _build_switch_network(network)

    conversion = converter.convert(network)

    row = conversion.network.switch.loc[
        conversion.element_indices[
            disabled_switch.id
        ]
    ]

    assert not bool(row["closed"])


# ============================================================================
# UUID Mapping
# ============================================================================


def test_switch_mapping(
    converter,
    network,
):
    """
    Switches shall participate in converter mapping.
    """

    (
        closed_switch,
        open_switch,
        disabled_switch,
    ) = _build_switch_network(network)

    conversion = converter.convert(network)

    mapping = conversion.element_mappings

    assert mapping[
        closed_switch.id
    ].table == "switch"

    assert mapping[
        open_switch.id
    ].table == "switch"

    assert mapping[
        disabled_switch.id
    ].table == "switch"

    assert mapping[
        closed_switch.id
    ].index >= 0

    assert mapping[
        open_switch.id
    ].index >= 0

    assert mapping[
        disabled_switch.id
    ].index >= 0


# ============================================================================
# Empty Network
# ============================================================================


def test_no_switches(
    converter,
    network,
):
    """
    A network without switches shall produce an empty
    pandapower switch table.
    """

    conversion = converter.convert(network)

    assert conversion.network.switch.empty