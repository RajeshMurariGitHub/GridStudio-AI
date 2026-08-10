"""
GridStudio AI

Module:
    builders.py

Description:
    Reusable builder functions for pandapower converter tests.

    These builders construct GridStudio domain models only.

    No pandapower objects are created here.
    No converter logic belongs here.
    No assertions belong here.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from src.domain.bus import Bus
from src.domain.network import Network
from src.domain.line import Line
from src.domain.load import Load
from src.domain.generator import Generator
from src.domain.solar import Solar
from src.domain.wind import Wind
from src.domain.battery import Battery
from src.domain.ev import EV
from src.domain.shunt import Shunt
from src.domain.switch import Switch
from src.domain.transformer import Transformer
from src.domain.electrical.line_parameters import LineParameters
from src.core.enums.electrical import BusType

from src.simulation.models.requests import ReferenceSource

from src.simulation.models.requests.power_flow_request import (
    PowerFlowRequest,
)

# ============================================================================
# Buses
# ============================================================================


def build_bus_hv(
        *,
        enabled: bool = True,
        name: str = "Bus HV",
) -> Bus:
    return Bus(
        name=name,
        nominal_voltage_kv=33.0,
        bus_type=BusType.SLACK,
        voltage_setpoint_pu=1.0,
        angle_setpoint_deg=0.0,
        enabled=enabled,
    )


def build_bus_1(
        *,
        enabled: bool = True,
        name: str = "Bus 1",
) -> Bus:
    return Bus(
        name=name,
        nominal_voltage_kv=11.0,
        bus_type=BusType.PQ,
        enabled=enabled,
    )


def build_bus_2(
        *,
        enabled: bool = True,
        name: str ="Bus 2",
) -> Bus:
    return Bus(
        name=name,
        nominal_voltage_kv=11.0,
        enabled=enabled,
    )


# ============================================================================
# Reference Source
# ============================================================================


def build_reference_source(
    bus: Bus,
) -> ReferenceSource:
    return ReferenceSource(
        bus_id=bus.id,
        voltage_magnitude_pu=1.01,
        voltage_angle_deg=5.0,
    )

# ============================================================================
# Power Flow Request
# ============================================================================


def build_power_flow_request(
    network: Network,
) -> PowerFlowRequest:
    """
    Build a PowerFlowRequest for a test network.
    """

    slack_bus = next(
        bus
        for bus in network.buses
        if bus.bus_type == BusType.SLACK
    )


    return PowerFlowRequest(
        network=network,
        reference_sources=(
            build_reference_source(
                slack_bus,
            ),
        ),
    )


# ============================================================================
# Line
# ============================================================================


def build_line(
    from_bus: Bus,
    to_bus: Bus,
    *,
    enabled: bool = True,
    length_km: float = 5.0,
) -> Line:

    parameters = LineParameters(
        r1_ohm_per_km=0.10,
        x1_ohm_per_km=0.20,
        c1_nf_per_km=10.0,
    )

    return Line(
        name="Line 1-2",
        from_node_id=from_bus.id,
        to_node_id=to_bus.id,
        length_km=length_km,
        parameters=parameters,
        maximum_current_ka=0.40,
        enabled=enabled,
    )


# ============================================================================
# Load
# ============================================================================


def build_load(
    bus: Bus,
    *,
    enabled: bool = True,
    scaling: float = 0.8,
    active_power_mw: float = 2.5,
    reactive_power_mvar: float = 0.75,
) -> Load:

    return Load.consumption(
        name="Load 2",
        node_id=bus.id,
        active_power_mw=active_power_mw,
        reactive_power_mvar=reactive_power_mvar,
        scaling=scaling,
        enabled=enabled,
    )


# ============================================================================
# Generator
# ============================================================================


def build_generator(
    bus: Bus,
    *,
    enabled = True,
    scaling = 0.75,
) -> Generator:

    return Generator.generation(
        name="Generator 1",
        node_id=bus.id,
        active_power_mw=1.8,
        reactive_power_mvar=0.30,
        scaling=scaling,
        minimum_active_power_mw=0.0,
        maximum_active_power_mw=2.5,
        minimum_reactive_power_mvar=-0.5,
        maximum_reactive_power_mvar=0.6,
        rated_power_mva=3.0,
        enabled=enabled,
    )


def build_voltage_generator_without_control(
    bus: Bus,
) -> Generator:

    return Generator(
        name="Voltage Generator 1",
        node_id=bus.id,
        active_power_mw=0.8,
        reactive_power_mvar=0.15,
        scaling=1.0,
        voltage_setpoint_pu=1.01,
        rated_power_mva=1.5,
        minimum_active_power_mw=0.0,
        maximum_active_power_mw=1.2,
        minimum_reactive_power_mvar=-0.3,
        maximum_reactive_power_mvar=0.4,
    )


def build_voltage_generator(
    bus: Bus,
) -> Generator:

    return Generator(
        name="Voltage Generator 2",
        node_id=bus.id,
        active_power_mw=1.2,
        reactive_power_mvar=0.0,
        scaling=1.0,
        voltage_control_enabled=True,
        voltage_setpoint_pu=1.02,
        rated_power_mva=2.0,
        minimum_active_power_mw=0.0,
        maximum_active_power_mw=1.8,
        minimum_reactive_power_mvar=-0.4,
        maximum_reactive_power_mvar=0.6,
    )


# ============================================================================
# Solar
# ============================================================================


def build_solar_pq(
    bus: Bus,
) -> Solar:

    return Solar.photovoltaic(
        name="Solar PQ 1",
        node_id=bus.id,
        dc_capacity_mw=2.4,
        inverter_rating_mva=2.0,
        active_power_mw=1.5,
        reactive_power_mvar=0.20,
        available_active_power_mw=1.8,
        scaling=0.90,
        minimum_reactive_power_mvar=-0.6,
        maximum_reactive_power_mvar=0.6,
        curtailment_enabled=True,
        reactive_power_control_enabled=True,
    )


def build_solar_voltage_controlled(
    bus: Bus,
) -> Solar:

    return Solar.photovoltaic(
        name="Solar Voltage Controlled 1",
        node_id=bus.id,
        dc_capacity_mw=3.0,
        inverter_rating_mva=2.5,
        active_power_mw=1.8,
        reactive_power_mvar=0.0,
        available_active_power_mw=2.2,
        voltage_control_enabled=True,
        voltage_setpoint_pu=1.015,
        minimum_reactive_power_mvar=-0.8,
        maximum_reactive_power_mvar=0.8,
    )


# ============================================================================
# Wind
# ============================================================================


def build_wind_pq(
    bus: Bus,
) -> Wind:

    return Wind.turbine(
        name="Wind PQ 1",
        node_id=bus.id,
        rated_active_power_mw=3.0,
        rated_power_mva=3.2,
        active_power_mw=2.1,
        reactive_power_mvar=0.25,
        available_active_power_mw=2.5,
        scaling=0.80,
        minimum_active_power_mw=0.0,
        minimum_reactive_power_mvar=-0.8,
        maximum_reactive_power_mvar=0.8,
    )


def build_wind_voltage_controlled(
    bus: Bus,
) -> Wind:

    return Wind.turbine(
        name="Wind Voltage Controlled 1",
        node_id=bus.id,
        rated_active_power_mw=4.0,
        rated_power_mva=4.5,
        active_power_mw=3.0,
        voltage_control_enabled=True,
        voltage_setpoint_pu=1.01,
        minimum_reactive_power_mvar=-1.0,
        maximum_reactive_power_mvar=1.0,
    )


# ============================================================================
# Battery
# ============================================================================


def build_battery_discharging(bus: Bus) -> Battery:
    return Battery(
        name="Battery Discharging",
        node_id=bus.id,
        active_power_mw=2.0,
        reactive_power_mvar=0.40,
        scaling=0.75,
        energy_capacity_mwh=8.0,
        state_of_charge=0.60,
        maximum_charge_power_mw=2.5,
        maximum_discharge_power_mw=3.0,
        rated_power_mva=3.5,
    )


def build_battery_charging(bus: Bus) -> Battery:
    return Battery(
        name="Battery Charging",
        node_id=bus.id,
        active_power_mw=-1.5,
        reactive_power_mvar=-0.30,
        scaling=0.80,
        energy_capacity_mwh=6.0,
        state_of_charge=0.35,
        maximum_charge_power_mw=2.0,
        maximum_discharge_power_mw=2.5,
        rated_power_mva=3.0,
    )


# ============================================================================
# EV
# ============================================================================


def build_ev_charging(bus: Bus) -> EV:
    return EV.charger(
        name="EV Charging",
        node_id=bus.id,
        battery_capacity_mwh=0.080,
        maximum_charge_power_mw=0.022,
        state_of_charge=0.40,
        active_power_mw=-0.018,
        reactive_power_mvar=-0.004,
        rated_power_mva=0.025,
    )


def build_ev_v2g(bus: Bus) -> EV:
    return EV.bidirectional(
        name="EV V2G",
        node_id=bus.id,
        battery_capacity_mwh=0.100,
        maximum_charge_power_mw=0.030,
        maximum_discharge_power_mw=0.025,
        state_of_charge=0.70,
        active_power_mw=0.020,
        reactive_power_mvar=0.005,
        rated_power_mva=0.035,
    )


# ============================================================================
# Shunts
# ============================================================================


def build_capacitor_bank(
    bus: Bus,
    *,
    enabled: bool = True,
    active_steps: int = 3,
) -> Shunt:
    return Shunt.capacitor_bank(
        name="Capacitor Bank 2",
        node_id=bus.id,
        reactive_power_mvar=1.20,
        scaling=0.50,
        nominal_voltage_kv=11.0,
        step_count=4,
        active_steps=active_steps,
        enabled=enabled,
    )


def build_shunt_reactor(
    bus: Bus,
    *,
    enabled: bool = True,
    active_steps: int = 1,
) -> Shunt:
    return Shunt.reactor(
        name="Shunt Reactor 1",
        node_id=bus.id,
        reactive_power_mvar=0.80,
        scaling=0.75,
        nominal_voltage_kv=11.0,
        step_count=2,
        active_steps=1,
        enabled=enabled,
    )


# ============================================================================
# Transformer
# ============================================================================

def build_fixed_transformer(
    hv_bus: Bus,
    lv_bus: Bus,
    *,
    enabled: bool = True,
) -> Transformer:

    return Transformer(
        name="Transformer Fixed 33/11 kV",
        from_node_id=hv_bus.id,
        to_node_id=lv_bus.id,
        rated_power_mva=10.0,
        high_voltage_kv=33.0,
        low_voltage_kv=11.0,
        impedance_percent=6.0,
        resistance_percent=0.8,
        enabled=enabled,
    )


# ============================================================================
# Switch
# ============================================================================
def build_open_switch(
    bus1: Bus,
    bus2: Bus,
) -> Switch:
    return Switch(
        name="Switch Open",
        from_node_id=bus1.id,
        to_node_id=bus2.id,
        is_closed=False,
        rated_voltage_kv=11.0,
        rated_current_ka=0.4,
    )

def build_closed_switch(
    bus1: Bus,
    bus2: Bus,
) -> Switch:

    return Switch(
        name="Switch Closed",
        from_node_id=bus1.id,
        to_node_id=bus2.id,
        is_closed=True,
        rated_voltage_kv=11.0,
        rated_current_ka=0.5,
    )

def build_disabled_switch(
    bus1: Bus,
    bus2: Bus,
) -> Switch:
    return Switch(
        name="Switch Disabled Closed",
        from_node_id=bus1.id,
        to_node_id=bus2.id,
        is_closed=True,
        enabled=False,
        rated_voltage_kv=11.0,
        rated_current_ka=0.3,
    )
# ============================================================================
# Network
# ============================================================================

def build_network() -> Network:
    """
    Construct the minimal valid network used by
    PandapowerEngine unit tests.

    The network contains one slack bus, one PQ bus,
    one branch, and one load so that a valid
    PowerFlowRequest can be constructed.
    """
    return Network(
        name="Test Network",
    )

    """
    network = Network(
        name="Test Network",
    )
    
    slack_bus = build_bus_hv()

    pq_bus = build_bus_1()

    network.add_many(
        (
            slack_bus,
            pq_bus,
            build_fixed_transformer(
                hv_bus=slack_bus,
                lv_bus=pq_bus,
            ),
            build_load(
                bus=pq_bus,
                active_power_mw=1.0,
                reactive_power_mvar=0.3,
            ),
        )
    )

    return network
    """

# ============================================================================
# Complete Network
# ============================================================================


def build_complete_network() -> Network:
    """
    Build a representative GridStudio network containing one
    instance of every converter-supported asset.

    This network is intentionally aligned with the canonical
    smoke_pandapower_converter.py example and is reused by the
    converter regression test suite.
    """

    network = Network(
        name="Complete Test Network",
    )

    #
    # ------------------------------------------------------------------
    # Buses
    # ------------------------------------------------------------------
    #

    bus_hv = build_bus_hv()

    bus_1 = build_bus_1()

    bus_2 = build_bus_2()

    network.add_many(
        (
            bus_hv,
            bus_1,
            bus_2,

            build_line(
                from_bus=bus_1,
                to_bus=bus_2,
            ),

            build_load(
                bus=bus_2,
            ),

            build_generator(
                bus=bus_1,
            ),

            build_voltage_generator_without_control(
                bus=bus_2,
            ),

            build_voltage_generator(
                bus=bus_2,
            ),

            build_solar_pq(
                bus=bus_1,
            ),

            #build_solar_voltage_controlled(
            #    bus=bus_2,
            #),

            build_wind_pq(
                bus=bus_1,
            ),

            #build_wind_voltage_controlled(
            #    bus=bus_2,
            #),

            build_battery_charging(
                bus=bus_1,
            ),

            build_battery_discharging(
                bus=bus_2,
            ),

            build_ev_charging(
                bus=bus_1,
            ),

            build_ev_v2g(
                bus=bus_2,
            ),

            build_capacitor_bank(
                bus=bus_2,
            ),

            build_shunt_reactor(
                bus=bus_1,
            ),

            build_fixed_transformer(
                hv_bus=bus_hv,
                lv_bus=bus_1,
            ),

            build_open_switch(
                bus1=bus_1,
                bus2=bus_2,
            ),

            build_closed_switch(
                bus1=bus_1,
                bus2=bus_2,
            ),

            build_disabled_switch(
                bus1=bus_1,
                bus2=bus_2,
            ),
        )
    )
    return network

# ------------------------------------------------------------------
# Engine 
# ------------------------------------------------------------------

def build_engine_network() -> Network:
    """
    Construct the minimal valid network used
    by PandapowerEngine tests.
    """

    network = Network(
        name="Engine Test Network",
    )

    slack_bus = build_bus_hv()

    pq_bus = build_bus_1()

    network.add_many(
        (
            slack_bus,
            pq_bus,
            build_fixed_transformer(
                hv_bus=slack_bus,
                lv_bus=pq_bus,
            ),
            build_load(
                bus=pq_bus,
                active_power_mw=1.0,
                reactive_power_mvar=0.3,
            ),
        )
    )

    return network


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

__all__ = [
    "build_bus_hv",
    "build_bus_1",
    "build_bus_2",
    "build_reference_source",
    "build_power_flow_request",
    "build_line",
    "build_load",
    "build_generator",
    "build_voltage_generator_without_control",
    "build_voltage_generator",
    "build_solar_pq",
    "build_solar_voltage_controlled",
    "build_wind_pq",
    "build_wind_voltage_controlled",
    "build_battery_discharging",
    "build_battery_charging",
    "build_ev_charging",
    "build_ev_v2g",
    "build_capacitor_bank",
    "build_shunt_reactor",
    "build_fixed_transformer",
    "build_open_switch",
    "build_closed_switch",
    "build_disabled_switch",
    "build_network",
    "build_complete_network",
    "build_engine_network",
]