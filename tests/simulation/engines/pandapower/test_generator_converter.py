"""
GridStudio AI

Module:
    test_generator_converter.py

Description:
    Regression tests for GridStudio Generator ->
    pandapower Generator conversion.

These tests verify:

    * Static Generator -> sgen
    * Voltage-Controlled Generator -> gen
    * Classification
    * Power limits
    * Scaling
    * UUID mapping

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from .builders import (
    build_bus_1,
    build_bus_2,
    build_generator,
    build_voltage_generator_without_control,
    build_voltage_generator,
)


# ============================================================================
# Helpers
# ============================================================================


def _build_generator_network(network):

    bus1 = build_bus_1()
    bus2 = build_bus_2()

    network.add(bus1)
    network.add(bus2)

    generator = build_generator(bus1)

    voltage_generator_pq = (
        build_voltage_generator_without_control(
            bus2,
        )
    )

    voltage_generator = (
        build_voltage_generator(
            bus2,
        )
    )

    network.add(generator)

    network.add(
        voltage_generator_pq,
    )

    network.add(
        voltage_generator,
    )

    return (
        generator,
        voltage_generator_pq,
        voltage_generator,
    )


# ============================================================================
# Static Generator
# ============================================================================


def test_static_generator_conversion(
    converter,
    network,
):

    (
        generator,
        _,
        _,
    ) = _build_generator_network(network)

    conversion = converter.convert(network)

    pp_net = conversion.network

    assert len(pp_net.sgen) == 2

    row = pp_net.sgen.loc[0]

    assert row["name"] == generator.name

    assert row["p_mw"] == generator.active_power_mw

    assert row["q_mvar"] == generator.reactive_power_mvar

    assert row["scaling"] == generator.scaling

    assert bool(row["in_service"])


# ============================================================================
# Voltage Generator without Voltage Control
# ============================================================================


def test_voltage_generator_without_control(
    converter,
    network,
):

    (
        _,
        voltage_generator,
        _,
    ) = _build_generator_network(network)

    conversion = converter.convert(network)

    row = conversion.network.sgen.loc[1]

    assert row["name"] == voltage_generator.name

    assert row["p_mw"] == voltage_generator.active_power_mw

    assert row["q_mvar"] == voltage_generator.reactive_power_mvar


# ============================================================================
# Voltage-Controlled Generator
# ============================================================================


def test_voltage_controlled_generator_conversion(
    converter,
    network,
):

    (
        _,
        _,
        generator,
    ) = _build_generator_network(network)

    conversion = converter.convert(network)

    pp_net = conversion.network

    assert len(pp_net.gen) == 1

    row = pp_net.gen.loc[0]

    assert row["name"] == generator.name

    assert row["p_mw"] == generator.active_power_mw

    assert (
        row["vm_pu"]
        ==
        generator.voltage_setpoint_pu
    )

    assert (
        row["min_q_mvar"]
        ==
        generator.minimum_reactive_power_mvar
    )

    assert (
        row["max_q_mvar"]
        ==
        generator.maximum_reactive_power_mvar
    )


# ============================================================================
# Classification
# ============================================================================


def test_generator_classification(
    converter,
    network,
):

    (
        generator,
        voltage_generator_pq,
        voltage_generator,
    ) = _build_generator_network(network)

    conversion = converter.convert(network)

    mapping = conversion.element_mappings

    assert (
        mapping[generator.id].table
        == "sgen"
    )

    assert (
        mapping[
            voltage_generator_pq.id
        ].table
        == "sgen"
    )

    assert (
        mapping[
            voltage_generator.id
        ].table
        == "gen"
    )


# ============================================================================
# UUID Mapping
# ============================================================================


def test_generator_mapping(
    converter,
    network,
):

    (
        generator,
        voltage_generator_pq,
        voltage_generator,
    ) = _build_generator_network(network)

    conversion = converter.convert(network)

    mapping = conversion.element_mappings

    assert mapping[
        generator.id
    ].index == 0

    assert mapping[
        voltage_generator_pq.id
    ].index == 1

    assert mapping[
        voltage_generator.id
    ].index == 0


# ============================================================================
# Disabled Generator
# ============================================================================


def test_disabled_generator(
    converter,
    network,
):

    bus = build_bus_1()

    network.add(bus)

    generator = build_generator(
        bus,
        enabled=False,
    )

    network.add(
        generator,
    )

    conversion = converter.convert(network)

    row = conversion.network.sgen.loc[0]

    assert not bool(
        row["in_service"]
    )