"""
GridStudio AI

Module:
    test_der_converter.py

Description:
    Regression tests for distributed energy resource (DER)
    conversion to pandapower.

    Covered DERs

    * Solar
    * Wind
    * Battery
    * Electric Vehicle (EV)

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from .builders import (
    build_bus_1,
    build_bus_2,
    build_solar_pq,
    build_solar_voltage_controlled,
    build_wind_pq,
    build_wind_voltage_controlled,
    build_battery_charging,
    build_battery_discharging,
    build_ev_charging,
    build_ev_v2g,
)

# ============================================================================
# Helpers
# ============================================================================


def _build_der_network(network):
    """
    Construct a representative DER network.
    """

    bus1 = build_bus_1()

    bus2 = build_bus_2()

    network.add(bus1)

    network.add(bus2)

    #
    # Solar
    #

    solar_pq = build_solar_pq(bus1)

    solar_vc = build_solar_voltage_controlled(
        bus2,
    )

    network.add(solar_pq)

    network.add(solar_vc)

    #
    # Wind
    #

    wind_pq = build_wind_pq(bus1)

    wind_vc = build_wind_voltage_controlled(
        bus2,
    )

    network.add(wind_pq)

    network.add(wind_vc)

    #
    # Battery
    #

    battery_charge = build_battery_charging(
        bus1,
    )

    battery_discharge = (
        build_battery_discharging(
            bus2,
        )
    )

    network.add(
        battery_charge,
    )

    network.add(
        battery_discharge,
    )

    #
    # EV
    #

    ev_charge = build_ev_charging(
        bus1,
    )

    ev_v2g = build_ev_v2g(
        bus2,
    )

    network.add(ev_charge)

    network.add(ev_v2g)

    return (
        solar_pq,
        solar_vc,
        wind_pq,
        wind_vc,
        battery_charge,
        battery_discharge,
        ev_charge,
        ev_v2g,
    )


# ============================================================================
# Solar
# ============================================================================


def test_solar_conversion(
    converter,
    network,
):
    """
    Solar DERs shall be classified correctly.
    """

    (
        solar_pq,
        solar_vc,
        *_,
    ) = _build_der_network(network)

    conversion = converter.convert(network)

    pp_net = conversion.network

    #
    # PQ solar
    #

    assert solar_pq.name in pp_net.sgen["name"].values

    #
    # Voltage-controlled solar
    #

    assert solar_vc.name in pp_net.gen["name"].values

def test_solar_mapping(
    converter,
    network,
):
    (
        solar_pq,
        solar_vc,
        *_,
    ) = _build_der_network(network)

    conversion = converter.convert(network)

    mapping = conversion.element_mappings

    assert mapping[
        solar_pq.id
    ].table == "sgen"

    assert mapping[
        solar_vc.id
    ].table == "gen"

# ============================================================================
# Wind
# ============================================================================


def test_wind_conversion(
    converter,
    network,
):
    (
        _,
        _,
        wind_pq,
        wind_vc,
        *_,
    ) = _build_der_network(network)

    conversion = converter.convert(network)

    pp_net = conversion.network

    assert wind_pq.name in pp_net.sgen["name"].values

    assert wind_vc.name in pp_net.gen["name"].values

def test_wind_mapping(
    converter,
    network,
):
    (
        _,
        _,
        wind_pq,
        wind_vc,
        *_,
    ) = _build_der_network(network)

    conversion = converter.convert(network)

    mapping = conversion.element_mappings

    assert mapping[
        wind_pq.id
    ].table == "sgen"

    assert mapping[
        wind_vc.id
    ].table == "gen"

# ============================================================================
# Battery
# ============================================================================


def test_battery_conversion(
    converter,
    network,
):
    (
        *_,
        battery_charge,
        battery_discharge,
        __,
        ___,
    ) = _build_der_network(network)

    conversion = converter.convert(network)

    pp_net = conversion.network

    #
    # Both batteries should appear
    #

    assert (
        battery_charge.name
        in
        pp_net.storage["name"].values
    )

    assert (
        battery_discharge.name
        in
        pp_net.storage["name"].values
    )

def test_battery_mapping(
    converter,
    network,
):
    (
        *_,
        battery_charge,
        battery_discharge,
        __,
        ___,
    ) = _build_der_network(network)

    conversion = converter.convert(network)

    mapping = conversion.element_mappings

    assert (
        mapping[
            battery_charge.id
        ].table
        ==
        "storage"
    )

    assert (
        mapping[
            battery_discharge.id
        ].table
        ==
        "storage"
    )

# ============================================================================
# Electric Vehicle
# ============================================================================


def test_ev_conversion(
    converter,
    network,
):
    (
        *_,
        ev_charge,
        ev_v2g,
    ) = _build_der_network(network)

    conversion = converter.convert(network)

    pp_net = conversion.network

    assert (
        ev_charge.name
        in
        pp_net.storage["name"].values
    )

    assert (
        ev_v2g.name
        in
        pp_net.storage["name"].values
    )

def test_ev_mapping(
    converter,
    network,
):
    (
        *_,
        ev_charge,
        ev_v2g,
    ) = _build_der_network(network)

    conversion = converter.convert(network)

    mapping = conversion.element_mappings

    assert (
        mapping[
            ev_charge.id
        ].table
        ==
        "storage"
    )

    assert (
        mapping[
            ev_v2g.id
        ].table
        ==
        "storage"
    )

# ============================================================================
# DER Classification
# ============================================================================


def test_der_classification(
    converter,
    network,
):
    """
    Verify every DER is converted into the correct
    pandapower table.
    """

    ders = _build_der_network(network)

    conversion = converter.convert(network)

    mapping = conversion.element_mappings

    expected = {
        ders[0].id: "sgen",
        ders[1].id: "gen",
        ders[2].id: "sgen",
        ders[3].id: "gen",
        ders[4].id: "storage",
        ders[5].id: "storage",
        ders[6].id: "storage",
        ders[7].id: "storage",
    }

    for asset_id, table in expected.items():

        assert (
            mapping[asset_id].table
            ==
            table
        )



