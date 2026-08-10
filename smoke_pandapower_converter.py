"""
GridStudio AI

Smoke Test:
    Pandapower Converter - Bus + Line + Load + Generator + Solar + Wind ... 
    + Battery + Shunt + Transformer + Switch

Description:
    End-to-end smoke test for the GridStudio-to-pandapower
    conversion boundary.

    This test verifies:

    * GridStudio Bus conversion,
    * GridStudio Line conversion,
    * GridStudio Load conversion,
    * GridStudio non-voltage-controlled Generator conversion,
    * Generator -> pandapower sgen mapping,
    * voltage setpoint alone does not enable voltage control,
    * voltage-controlled Generator -> pandapower gen mapping,
    * GridStudio Wind conversion,
    * Wind PQ -> pandapower sgen mapping,
    * voltage-controlled Wind -> pandapower gen mapping,
    * wind availability and curtailment semantics,
    * wind turbine operating-speed characteristics,
    * GridStudio Shunt conversion,
    * capacitor-bank -> pandapower shunt mapping,
    * shunt-reactor -> pandapower shunt mapping,
    * GridStudio/pandapower shunt reactive-power sign translation,
    * shunt step-count and active-step propagation,
    * shunt scaling applied at the conversion boundary,
    * UUID-to-pandapower index mappings,
    * line connectivity and electrical parameters,
    * GridStudio load sign convention,
    * pandapower load sign convention,
    * GridStudio generator sign convention,
    * pandapower sgen sign convention,
    * load and generator scaling,
    * generator operating limits and rating,
    * voltage-control setpoint propagation,
    * operational state propagation,
    * GridStudio ideal Switch conversion,
    * bus-bus switch connectivity,
    * switch open/closed state propagation,
    * non-operational closed switch isolation,
    * switch current-rating propagation.
    * GridStudio Battery conversion,
    * Battery -> pandapower storage mapping,
    * battery charge/discharge/idle operating modes,
    * GridStudio/pandapower storage active-power sign translation,
    * GridStudio/pandapower storage reactive-power sign translation,
    * battery active/reactive operating-limit translation,
    * battery SOC fraction -> pandapower SOC percent conversion,
    * battery energy-capacity and rating propagation,
    * battery scaling propagation,

Run from the project root with:

    python smoke_pandapower_converter.py
"""

from numbers import Integral

import pytest

from src.domain.bus import Bus
from src.domain.electrical.line_parameters import LineParameters
from src.domain.generator import Generator
from src.domain.line import Line
from src.domain.load import Load
from src.domain.network import Network
from src.domain.shunt import Shunt
from src.domain.solar import Solar
from src.domain.switch import Switch
from src.domain.transformer import Transformer
from src.domain.wind import Wind
from src.domain.battery import Battery
from src.domain.ev import EV
from src.simulation.models.requests import ReferenceSource
from src.simulation.engines.pandapower.converter import (
    PandapowerConverter,
)


# ============================================================================
# GridStudio Domain Network
# ============================================================================


network = Network(
    name=(
        "Pandapower Bus-Line-Load-Generator-Solar-Wind-Shunt-Transformer-Switch "
        "Smoke Test"
    ),
)


# ============================================================================
# Buses
# ============================================================================


bus_hv = Bus(
    name="Bus HV",
    nominal_voltage_kv=33.0,
)

bus_1 = Bus(
    name="Bus 1",
    nominal_voltage_kv=11.0,
)

bus_2 = Bus(
    name="Bus 2",
    nominal_voltage_kv=11.0,
)

# ============================================================================
# Reference / External Grid Source
# ============================================================================

# ReferenceSource is simulation configuration rather than physical
# GridStudio network equipment.
#
# It therefore does NOT belong in Network.elements and must not be
# added using network.add().
#
# At the pandapower conversion boundary it becomes an ext_grid:
#
#     GridStudio bus_id
#         -> pandapower bus
#
#     voltage_magnitude_pu
#         -> vm_pu
#
#     voltage_angle_deg
#         -> va_degree

reference_source = ReferenceSource(
    bus_id=bus_hv.id,
    voltage_magnitude_pu=1.01,
    voltage_angle_deg=5.0,
)

# ============================================================================
# Line Parameters
# ============================================================================


parameters = LineParameters(
    r1_ohm_per_km=0.10,
    x1_ohm_per_km=0.20,
    c1_nf_per_km=10.0,
)


# ============================================================================
# Line
# ============================================================================


line = Line(
    name="Line 1-2",
    from_node_id=bus_1.id,
    to_node_id=bus_2.id,
    length_km=5.0,
    parameters=parameters,
    maximum_current_ka=0.40,
)


# ============================================================================
# Load
# ============================================================================

# Load.consumption() accepts conventional positive demand values.
#
# GridStudio internally uses the network-injection convention:
#
#     positive P/Q = injection into network
#     negative P/Q = absorption from network
#
# Therefore this conventional consuming load is stored internally as:
#
#     active_power_mw     = -2.5
#     reactive_power_mvar = -0.75
#
# scaling remains 0.8.


load = Load.consumption(
    name="Load 2",
    node_id=bus_2.id,
    active_power_mw=2.5,
    reactive_power_mvar=0.75,
    scaling=0.8,
)


# ============================================================================
# Static Generator
# ============================================================================

# Generator.generation() uses the GridStudio network-injection
# convention directly:
#
#     positive P = active-power injection into the network
#     positive Q = reactive-power injection into the network
#     negative Q = reactive-power absorption
#
# This generator does NOT regulate voltage. The pandapower converter
# should therefore represent it using the pandapower sgen table.
#
# Base operating point:
#
#     P = +1.8 MW
#     Q = +0.30 MVAr
#
# With scaling = 0.75:
#
#     effective P = 1.35 MW
#     effective Q = 0.225 MVAr


generator = Generator.generation(
    name="Generator 1",
    node_id=bus_1.id,
    active_power_mw=1.8,
    reactive_power_mvar=0.30,
    scaling=0.75,
    minimum_active_power_mw=0.0,
    maximum_active_power_mw=2.5,
    minimum_reactive_power_mvar=-0.5,
    maximum_reactive_power_mvar=0.6,
    rated_power_mva=3.0,
)


# ============================================================================
# Voltage Generator 1 - Setpoint Present, Control Disabled
# ============================================================================

# This generator deliberately has a voltage setpoint but does NOT
# explicitly enable voltage control.
#
# Generator.is_voltage_controlled requires BOTH:
#
#     voltage_control_enabled is True
#     voltage_setpoint_pu is not None
#
# Therefore this generator must remain a pandapower sgen.
#
# This case protects the semantic boundary against accidentally
# interpreting the presence of a voltage setpoint alone as voltage
# regulation.


voltage_generator_1 = Generator(
    name="Voltage Generator 1",
    node_id=bus_2.id,
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


# ============================================================================
# Voltage Generator 2 - Voltage-Controlled Generator
# ============================================================================

# This generator explicitly enables voltage control AND provides
# a voltage setpoint.
#
# Therefore:
#
#     is_voltage_controlled is True
#
# and the converter must represent it using pandapower gen.
#
# For a voltage-controlled generator, the conversion boundary is:
#
#     GridStudio specified P
#         -> pandapower p_mw
#
#     GridStudio voltage setpoint
#         -> pandapower vm_pu
#
# Reactive power is solved by the power-flow engine and constrained
# by the configured minimum and maximum reactive-power limits.


voltage_generator_2 = Generator(
    name="Voltage Generator 2",
    node_id=bus_2.id,
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
# Solar PV
# ============================================================================

solar_pq = Solar.photovoltaic(
    name="Solar PQ 1",
    node_id=bus_1.id,
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

solar_voltage_controlled = Solar.photovoltaic(
    name="Solar Voltage Controlled 1",
    node_id=bus_2.id,
    dc_capacity_mw=3.0,
    inverter_rating_mva=2.5,
    active_power_mw=1.8,
    reactive_power_mvar=0.0,
    available_active_power_mw=2.2,
    scaling=1.0,
    minimum_reactive_power_mvar=-0.8,
    maximum_reactive_power_mvar=0.8,
    voltage_control_enabled=True,
    voltage_setpoint_pu=1.015,
    curtailment_enabled=True,
    reactive_power_control_enabled=True,
)



# ============================================================================
# Wind
# ============================================================================

# Wind follows the same GridStudio network-injection convention as Generator:
#
#     positive P = active-power injection
#     positive Q = reactive-power injection
#
# Two cases exercise the same converter classification boundary used by
# Generator and Solar:
#
#     Wind PQ 1
#         -> voltage control disabled
#         -> pandapower sgen
#
#     Wind Voltage Controlled 1
#         -> voltage control enabled + voltage setpoint present
#         -> pandapower gen
#
# Wind.turbine() also establishes maximum_active_power_mw from the installed
# rated active-power capacity.

wind_pq = Wind.turbine(
    name="Wind PQ 1",
    node_id=bus_1.id,
    rated_active_power_mw=3.0,
    rated_power_mva=3.2,
    active_power_mw=2.1,
    reactive_power_mvar=0.25,
    available_active_power_mw=2.5,
    scaling=0.80,
    minimum_active_power_mw=0.0,
    minimum_reactive_power_mvar=-0.8,
    maximum_reactive_power_mvar=0.8,
    cut_in_wind_speed_mps=3.0,
    rated_wind_speed_mps=12.0,
    cut_out_wind_speed_mps=25.0,
    curtailment_enabled=True,
    reactive_power_control_enabled=True,
)

wind_voltage_controlled = Wind.turbine(
    name="Wind Voltage Controlled 1",
    node_id=bus_2.id,
    rated_active_power_mw=4.0,
    rated_power_mva=4.5,
    active_power_mw=3.0,
    reactive_power_mvar=0.0,
    available_active_power_mw=3.5,
    scaling=1.0,
    minimum_active_power_mw=0.0,
    minimum_reactive_power_mvar=-1.0,
    maximum_reactive_power_mvar=1.0,
    voltage_control_enabled=True,
    voltage_setpoint_pu=1.01,
    cut_in_wind_speed_mps=3.5,
    rated_wind_speed_mps=11.5,
    cut_out_wind_speed_mps=25.0,
    curtailment_enabled=True,
    reactive_power_control_enabled=True,
)


# ============================================================================
# Batteries
# ============================================================================

# GridStudio Battery uses the network-injection convention:
#
#     positive P = discharge into the network
#     negative P = charging from the network
#
#     positive Q = reactive-power injection
#     negative Q = reactive-power absorption
#
# pandapower storage uses the consumer-reference convention:
#
#     positive p_mw = charging
#     negative p_mw = discharging
#
#     positive q_mvar = reactive-power absorption
#     negative q_mvar = reactive-power injection
#
# Therefore both P and Q reverse sign at the conversion boundary.
#
# The three cases below exercise:
#
#     Battery Discharging
#         -> positive GridStudio P
#         -> negative pandapower p_mw
#
#     Battery Charging
#         -> negative GridStudio P
#         -> positive pandapower p_mw
#
#     Battery Idle VAR
#         -> zero active power
#         -> non-zero reactive-power support


battery_discharging = Battery(
    name="Battery Discharging",
    node_id=bus_1.id,
    active_power_mw=2.0,
    reactive_power_mvar=0.40,
    scaling=0.75,
    energy_capacity_mwh=8.0,
    state_of_charge=0.60,
    minimum_state_of_charge=0.10,
    maximum_state_of_charge=0.90,
    maximum_charge_power_mw=2.5,
    maximum_discharge_power_mw=3.0,
    rated_power_mva=3.5,
    minimum_reactive_power_mvar=-0.8,
    maximum_reactive_power_mvar=1.0,
    charge_efficiency=0.95,
    discharge_efficiency=0.94,
)

battery_charging = Battery(
    name="Battery Charging",
    node_id=bus_2.id,
    active_power_mw=-1.5,
    reactive_power_mvar=-0.30,
    scaling=0.80,
    energy_capacity_mwh=6.0,
    state_of_charge=0.35,
    minimum_state_of_charge=0.15,
    maximum_state_of_charge=0.95,
    maximum_charge_power_mw=2.0,
    maximum_discharge_power_mw=2.5,
    rated_power_mva=3.0,
    minimum_reactive_power_mvar=-0.7,
    maximum_reactive_power_mvar=0.9,
    charge_efficiency=0.96,
    discharge_efficiency=0.95,
)

battery_idle_var = Battery(
    name="Battery Idle VAR",
    node_id=bus_2.id,
    active_power_mw=0.0,
    reactive_power_mvar=0.25,
    scaling=1.0,
    energy_capacity_mwh=4.0,
    state_of_charge=0.50,
    minimum_state_of_charge=0.20,
    maximum_state_of_charge=0.80,
    maximum_charge_power_mw=1.5,
    maximum_discharge_power_mw=1.5,
    rated_power_mva=2.0,
    minimum_reactive_power_mvar=-0.5,
    maximum_reactive_power_mvar=0.6,
    charge_efficiency=0.95,
    discharge_efficiency=0.95,
)


# ============================================================================
# Electric Vehicles
# ============================================================================

# GridStudio EV uses the canonical network-injection convention:
#
#     negative P = grid-to-vehicle charging
#     positive P = vehicle-to-grid discharge
#
#     positive Q = reactive-power injection
#     negative Q = reactive-power absorption
#
# pandapower storage uses the consumer-reference convention:
#
#     positive p_mw = charging
#     negative p_mw = discharging
#
# Therefore EV P and Q reverse sign at the conversion boundary.
#
# Three cases are exercised:
#
#     EV Charging
#         -> connected unidirectional charger
#         -> negative GridStudio P
#         -> positive pandapower storage P
#
#     EV V2G
#         -> connected bidirectional charger
#         -> positive GridStudio P
#         -> negative pandapower storage P
#
#     EV Disconnected
#         -> physically disconnected from charging equipment
#         -> zero GridStudio P/Q
#         -> pandapower storage out of service


ev_charging = EV.charger(
    name="EV Charging",
    node_id=bus_2.id,
    battery_capacity_mwh=0.080,
    maximum_charge_power_mw=0.022,
    state_of_charge=0.40,
    active_power_mw=-0.018,
    reactive_power_mvar=-0.004,
    rated_power_mva=0.025,
    minimum_state_of_charge=0.10,
    maximum_state_of_charge=0.90,
    scaling=0.80,
    charge_efficiency=0.95,
    discharge_efficiency=0.95,
    is_connected=True,
    charging_enabled=True,
    reactive_power_control_enabled=True,
    minimum_reactive_power_mvar=-0.010,
    maximum_reactive_power_mvar=0.010,
)

ev_v2g = EV.bidirectional(
    name="EV V2G",
    node_id=bus_1.id,
    battery_capacity_mwh=0.100,
    maximum_charge_power_mw=0.030,
    maximum_discharge_power_mw=0.025,
    state_of_charge=0.70,
    active_power_mw=0.020,
    reactive_power_mvar=0.005,
    rated_power_mva=0.035,
    minimum_state_of_charge=0.20,
    maximum_state_of_charge=0.95,
    scaling=0.75,
    charge_efficiency=0.96,
    discharge_efficiency=0.94,
    is_connected=True,
    charging_enabled=True,
    reactive_power_control_enabled=True,
    minimum_reactive_power_mvar=-0.012,
    maximum_reactive_power_mvar=0.015,
)

ev_disconnected = EV.charger(
    name="EV Disconnected",
    node_id=bus_2.id,
    battery_capacity_mwh=0.060,
    maximum_charge_power_mw=0.011,
    state_of_charge=0.55,
    active_power_mw=0.0,
    reactive_power_mvar=0.0,
    rated_power_mva=0.015,
    minimum_state_of_charge=0.10,
    maximum_state_of_charge=0.90,
    scaling=1.0,
    charge_efficiency=0.95,
    discharge_efficiency=0.95,
    is_connected=False,
    charging_enabled=True,
)



# ============================================================================
# Capacitor Bank
# ============================================================================

# GridStudio uses the network-injection convention for Shunt:
#
#     positive Q = reactive-power injection
#     negative Q = reactive-power absorption
#
# Therefore a capacitor bank has positive reactive_power_mvar.
#
# This bank has:
#
#     total rated Q = +1.20 MVAr
#     step_count    = 4
#     active_steps  = 3
#     scaling       = 0.50
#
# Therefore:
#
#     Q per step
#         = +1.20 / 4
#         = +0.30 MVAr
#
#     configured GridStudio Q
#         = +0.30 * 3 * 0.50
#         = +0.45 MVAr
#
# pandapower shunt uses the load-reference sign convention:
#
#     positive q_mvar = inductive absorption
#     negative q_mvar = capacitive injection
#
# Therefore the converter must invert the GridStudio Q sign.
#
# GridStudio scaling is already incorporated into the converted
# per-step reactive-power value. It must NOT be represented again
# using a separate pandapower scaling factor.


capacitor_bank = Shunt.capacitor_bank(
    name="Capacitor Bank 2",
    node_id=bus_2.id,
    reactive_power_mvar=1.20,
    scaling=0.50,
    nominal_voltage_kv=11.0,
    step_count=4,
    active_steps=3,
)


# ============================================================================
# Shunt Reactor
# ============================================================================

# Shunt.reactor() accepts a positive absorption magnitude and stores
# it using GridStudio's network-injection convention as negative Q.
#
# This reactor has:
#
#     total rated Q = -0.80 MVAr
#     step_count    = 2
#     active_steps  = 1
#     scaling       = 0.75
#
# Therefore:
#
#     Q per step
#         = -0.80 / 2
#         = -0.40 MVAr
#
#     configured GridStudio Q
#         = -0.40 * 1 * 0.75
#         = -0.30 MVAr
#
# After conversion to pandapower's load-reference convention,
# the per-step q_mvar must be positive.


shunt_reactor = Shunt.reactor(
    name="Shunt Reactor 1",
    node_id=bus_1.id,
    reactive_power_mvar=0.80,
    scaling=0.75,
    nominal_voltage_kv=11.0,
    step_count=2,
    active_steps=1,
)


# ============================================================================
# Transformers
# ============================================================================

# Transformer terminal convention:
#     from_node_id -> high-voltage winding
#     to_node_id   -> low-voltage winding

fixed_transformer = Transformer(
    name="Transformer Fixed 33/11 kV",
    from_node_id=bus_hv.id,
    to_node_id=bus_1.id,
    rated_power_mva=10.0,
    high_voltage_kv=33.0,
    low_voltage_kv=11.0,
    impedance_percent=6.0,
    resistance_percent=0.8,
    no_load_loss_kw=12.0,
    exciting_current_percent=0.25,
    phase_shift_deg=0.0,
)

tapped_transformer = Transformer(
    name="Transformer Tapped 33/11 kV",
    from_node_id=bus_hv.id,
    to_node_id=bus_2.id,
    rated_power_mva=16.0,
    high_voltage_kv=33.0,
    low_voltage_kv=11.0,
    impedance_percent=8.0,
    resistance_percent=1.0,
    no_load_loss_kw=18.0,
    exciting_current_percent=0.30,
    phase_shift_deg=30.0,
    tap_position=2,
    minimum_tap_position=-5,
    maximum_tap_position=5,
    tap_step_percent=1.25,
    tap_on_high_voltage_side=True,
)


# ============================================================================
# Switches
# ============================================================================

# Three ideal bus-bus switches exercise the topology/state boundary:
#
# 1. closed + operational     -> pandapower closed=True
# 2. open + operational       -> pandapower closed=False
# 3. closed + non-operational -> pandapower closed=False
#
# All three are ideal switches (R = X = 0), so they can be represented
# directly using pandapower's bus-bus switch model.

closed_switch = Switch(
    name="Switch Closed",
    from_node_id=bus_1.id,
    to_node_id=bus_2.id,
    is_closed=True,
    normally_closed=True,
    rated_voltage_kv=11.0,
    rated_current_ka=0.50,
)

open_switch = Switch(
    name="Switch Open",
    from_node_id=bus_1.id,
    to_node_id=bus_2.id,
    is_closed=False,
    normally_closed=True,
    rated_voltage_kv=11.0,
    rated_current_ka=0.40,
)

disabled_closed_switch = Switch(
    name="Switch Disabled Closed",
    from_node_id=bus_1.id,
    to_node_id=bus_2.id,
    enabled=False,
    is_closed=True,
    normally_closed=True,
    rated_voltage_kv=11.0,
    rated_current_ka=0.30,
)


# ============================================================================
# Verify GridStudio Semantics Before Conversion
# ============================================================================


# ---------------------------------------------------------------------------
# Load Semantics
# ---------------------------------------------------------------------------


assert load.active_power_mw == pytest.approx(-2.5)
assert load.reactive_power_mvar == pytest.approx(-0.75)
assert load.scaling == pytest.approx(0.8)

assert load.active_demand_mw == pytest.approx(2.0)
assert load.reactive_demand_mvar == pytest.approx(0.6)


# ---------------------------------------------------------------------------
# Static Generator Semantics
# ---------------------------------------------------------------------------


assert generator.active_power_mw == pytest.approx(1.8)
assert generator.reactive_power_mvar == pytest.approx(0.30)
assert generator.scaling == pytest.approx(0.75)

assert generator.is_voltage_controlled is False

assert generator.active_generation_mw == pytest.approx(1.35)
assert generator.reactive_generation_mvar == pytest.approx(0.225)

assert generator.minimum_active_power_mw == pytest.approx(0.0)
assert generator.maximum_active_power_mw == pytest.approx(2.5)

assert generator.minimum_reactive_power_mvar == pytest.approx(-0.5)
assert generator.maximum_reactive_power_mvar == pytest.approx(0.6)

assert generator.rated_power_mva == pytest.approx(3.0)


# ---------------------------------------------------------------------------
# Voltage Generator 1 Semantics
# ---------------------------------------------------------------------------

# A voltage setpoint by itself does not make the Generator
# voltage-controlled.


assert voltage_generator_1.voltage_setpoint_pu == pytest.approx(
    1.01
)

assert voltage_generator_1.voltage_control_enabled is False
assert voltage_generator_1.is_voltage_controlled is False

assert voltage_generator_1.active_power_mw == pytest.approx(0.8)
assert voltage_generator_1.reactive_power_mvar == pytest.approx(
    0.15
)

assert (
    voltage_generator_1.minimum_active_power_mw
    == pytest.approx(0.0)
)

assert (
    voltage_generator_1.maximum_active_power_mw
    == pytest.approx(1.2)
)

assert (
    voltage_generator_1.minimum_reactive_power_mvar
    == pytest.approx(-0.3)
)

assert (
    voltage_generator_1.maximum_reactive_power_mvar
    == pytest.approx(0.4)
)

assert voltage_generator_1.rated_power_mva == pytest.approx(1.5)


# ---------------------------------------------------------------------------
# Voltage Generator 2 Semantics
# ---------------------------------------------------------------------------


assert voltage_generator_2.voltage_control_enabled is True

assert voltage_generator_2.voltage_setpoint_pu == pytest.approx(
    1.02
)

assert voltage_generator_2.is_voltage_controlled is True

assert voltage_generator_2.active_power_mw == pytest.approx(1.2)

assert voltage_generator_2.reactive_power_mvar == pytest.approx(
    0.0
)

assert voltage_generator_2.scaling == pytest.approx(1.0)

assert (
    voltage_generator_2.minimum_active_power_mw
    == pytest.approx(0.0)
)

assert (
    voltage_generator_2.maximum_active_power_mw
    == pytest.approx(1.8)
)

assert (
    voltage_generator_2.minimum_reactive_power_mvar
    == pytest.approx(-0.4)
)

assert (
    voltage_generator_2.maximum_reactive_power_mvar
    == pytest.approx(0.6)
)

assert voltage_generator_2.rated_power_mva == pytest.approx(2.0)


# ---------------------------------------------------------------------------
# Solar Semantics
# ---------------------------------------------------------------------------

assert solar_pq.dc_capacity_mw == pytest.approx(2.4)
assert solar_pq.inverter_rating_mva == pytest.approx(2.0)
assert solar_pq.dc_ac_ratio == pytest.approx(1.2)
assert solar_pq.active_power_mw == pytest.approx(1.5)
assert solar_pq.reactive_power_mvar == pytest.approx(0.20)
assert solar_pq.scaling == pytest.approx(0.90)
assert solar_pq.active_generation_mw == pytest.approx(1.35)
assert solar_pq.reactive_generation_mvar == pytest.approx(0.18)
assert solar_pq.maximum_active_power_mw == pytest.approx(2.0)
assert solar_pq.available_active_power_mw == pytest.approx(1.8)
assert solar_pq.available_generation_mw == pytest.approx(1.8)
assert solar_pq.curtailed_power_mw == pytest.approx(0.45)
assert solar_pq.curtailment_fraction == pytest.approx(0.25)
assert solar_pq.is_generating is True
assert solar_pq.is_curtailed is True
assert solar_pq.supports_reactive_power_control is True
assert solar_pq.is_voltage_controlled is False

assert solar_voltage_controlled.dc_capacity_mw == pytest.approx(3.0)
assert solar_voltage_controlled.inverter_rating_mva == pytest.approx(2.5)
assert solar_voltage_controlled.dc_ac_ratio == pytest.approx(1.2)
assert solar_voltage_controlled.active_power_mw == pytest.approx(1.8)
assert solar_voltage_controlled.maximum_active_power_mw == pytest.approx(2.5)
assert solar_voltage_controlled.available_active_power_mw == pytest.approx(2.2)
assert solar_voltage_controlled.voltage_control_enabled is True
assert solar_voltage_controlled.voltage_setpoint_pu == pytest.approx(1.015)
assert solar_voltage_controlled.is_voltage_controlled is True
assert solar_voltage_controlled.supports_reactive_power_control is True



# ---------------------------------------------------------------------------
# Wind Semantics
# ---------------------------------------------------------------------------

assert wind_pq.rated_active_power_mw == pytest.approx(3.0)
assert wind_pq.rated_power_mva == pytest.approx(3.2)
assert wind_pq.active_power_mw == pytest.approx(2.1)
assert wind_pq.reactive_power_mvar == pytest.approx(0.25)
assert wind_pq.available_active_power_mw == pytest.approx(2.5)
assert wind_pq.maximum_active_power_mw == pytest.approx(3.0)
assert wind_pq.scaling == pytest.approx(0.80)
assert wind_pq.active_generation_mw == pytest.approx(1.68)
assert wind_pq.reactive_generation_mvar == pytest.approx(0.20)
assert wind_pq.available_generation_mw == pytest.approx(2.5)
assert wind_pq.curtailed_power_mw == pytest.approx(0.82)
assert wind_pq.curtailment_fraction == pytest.approx(0.328)
assert wind_pq.is_generating is True
assert wind_pq.is_curtailed is True
assert wind_pq.supports_reactive_power_control is True
assert wind_pq.is_voltage_controlled is False
assert wind_pq.has_wind_speed_characteristics is True
assert wind_pq.is_operational_at_wind_speed(10.0) is True
assert wind_pq.is_operational_at_wind_speed(2.0) is False
assert wind_pq.is_operational_at_wind_speed(25.0) is False

assert wind_voltage_controlled.rated_active_power_mw == pytest.approx(4.0)
assert wind_voltage_controlled.rated_power_mva == pytest.approx(4.5)
assert wind_voltage_controlled.active_power_mw == pytest.approx(3.0)
assert wind_voltage_controlled.available_active_power_mw == pytest.approx(3.5)
assert wind_voltage_controlled.maximum_active_power_mw == pytest.approx(4.0)
assert wind_voltage_controlled.voltage_control_enabled is True
assert wind_voltage_controlled.voltage_setpoint_pu == pytest.approx(1.01)
assert wind_voltage_controlled.is_voltage_controlled is True
assert wind_voltage_controlled.supports_reactive_power_control is True
assert wind_voltage_controlled.has_wind_speed_characteristics is True


# ---------------------------------------------------------------------------
# Battery Semantics
# ---------------------------------------------------------------------------

# Discharging battery
assert battery_discharging.active_power_mw == pytest.approx(2.0)
assert battery_discharging.reactive_power_mvar == pytest.approx(0.40)
assert battery_discharging.scaling == pytest.approx(0.75)
assert battery_discharging.energy_capacity_mwh == pytest.approx(8.0)
assert battery_discharging.state_of_charge == pytest.approx(0.60)
assert battery_discharging.maximum_charge_power_mw == pytest.approx(2.5)
assert battery_discharging.maximum_discharge_power_mw == pytest.approx(3.0)
assert battery_discharging.rated_power_mva == pytest.approx(3.5)
assert battery_discharging.is_discharging is True
assert battery_discharging.is_charging is False
assert battery_discharging.is_idle is False

# Charging battery
assert battery_charging.active_power_mw == pytest.approx(-1.5)
assert battery_charging.reactive_power_mvar == pytest.approx(-0.30)
assert battery_charging.scaling == pytest.approx(0.80)
assert battery_charging.energy_capacity_mwh == pytest.approx(6.0)
assert battery_charging.state_of_charge == pytest.approx(0.35)
assert battery_charging.is_charging is True
assert battery_charging.is_discharging is False
assert battery_charging.is_idle is False

# Idle battery providing reactive support
assert battery_idle_var.active_power_mw == pytest.approx(0.0)
assert battery_idle_var.reactive_power_mvar == pytest.approx(0.25)
assert battery_idle_var.state_of_charge == pytest.approx(0.50)
assert battery_idle_var.is_idle is True
assert battery_idle_var.is_charging is False
assert battery_idle_var.is_discharging is False


# ---------------------------------------------------------------------------
# EV Semantics
# ---------------------------------------------------------------------------

# Charging EV

assert ev_charging.is_connected is True
assert ev_charging.v2g_enabled is False
assert ev_charging.supports_v2g is False

assert ev_charging.active_power_mw == pytest.approx(-0.018)
assert ev_charging.reactive_power_mvar == pytest.approx(-0.004)
assert ev_charging.scaling == pytest.approx(0.80)

assert ev_charging.is_charging is True
assert ev_charging.is_discharging is False
assert ev_charging.is_idle is False

assert ev_charging.charging_power_mw == pytest.approx(
    0.018 * 0.80
)
assert ev_charging.discharging_power_mw == pytest.approx(0.0)

assert ev_charging.battery_capacity_mwh == pytest.approx(0.080)
assert ev_charging.state_of_charge == pytest.approx(0.40)
assert ev_charging.stored_energy_mwh == pytest.approx(0.032)

assert ev_charging.maximum_charge_power_mw == pytest.approx(0.022)
assert ev_charging.maximum_discharge_power_mw == pytest.approx(0.0)

assert ev_charging.can_charge is True
assert ev_charging.can_discharge is False


# V2G EV

assert ev_v2g.is_connected is True
assert ev_v2g.v2g_enabled is True
assert ev_v2g.supports_v2g is True

assert ev_v2g.active_power_mw == pytest.approx(0.020)
assert ev_v2g.reactive_power_mvar == pytest.approx(0.005)
assert ev_v2g.scaling == pytest.approx(0.75)

assert ev_v2g.is_charging is False
assert ev_v2g.is_discharging is True
assert ev_v2g.is_idle is False

assert ev_v2g.charging_power_mw == pytest.approx(0.0)
assert ev_v2g.discharging_power_mw == pytest.approx(
    0.020 * 0.75
)

assert ev_v2g.battery_capacity_mwh == pytest.approx(0.100)
assert ev_v2g.state_of_charge == pytest.approx(0.70)
assert ev_v2g.stored_energy_mwh == pytest.approx(0.070)

assert ev_v2g.maximum_charge_power_mw == pytest.approx(0.030)
assert ev_v2g.maximum_discharge_power_mw == pytest.approx(0.025)

assert ev_v2g.can_charge is True
assert ev_v2g.can_discharge is True


# Disconnected EV

assert ev_disconnected.is_connected is False

assert ev_disconnected.active_power_mw == pytest.approx(0.0)
assert ev_disconnected.reactive_power_mvar == pytest.approx(0.0)

assert ev_disconnected.is_charging is False
assert ev_disconnected.is_discharging is False
assert ev_disconnected.is_idle is True

assert ev_disconnected.charging_power_mw == pytest.approx(0.0)
assert ev_disconnected.discharging_power_mw == pytest.approx(0.0)
assert ev_disconnected.apparent_power_mva == pytest.approx(0.0)

assert ev_disconnected.can_charge is False
assert ev_disconnected.can_discharge is False

# ---------------------------------------------------------------------------
# Capacitor-Bank Semantics
# ---------------------------------------------------------------------------


assert capacitor_bank.active_power_mw == pytest.approx(0.0)
assert capacitor_bank.reactive_power_mvar == pytest.approx(1.20)
assert capacitor_bank.scaling == pytest.approx(0.50)

assert capacitor_bank.nominal_voltage_kv == pytest.approx(11.0)

assert capacitor_bank.step_count == 4
assert capacitor_bank.active_steps == 3

assert capacitor_bank.energized_fraction == pytest.approx(0.75)

assert capacitor_bank.reactive_power_per_step_mvar == pytest.approx(
    0.30
)

assert capacitor_bank.configured_reactive_power_mvar == pytest.approx(
    0.45
)

assert capacitor_bank.is_capacitive is True
assert capacitor_bank.is_inductive is False
assert capacitor_bank.is_energized is True
assert capacitor_bank.is_fully_energized is False
assert capacitor_bank.is_switched_bank is True


# ---------------------------------------------------------------------------
# Shunt-Reactor Semantics
# ---------------------------------------------------------------------------


assert shunt_reactor.active_power_mw == pytest.approx(0.0)
assert shunt_reactor.reactive_power_mvar == pytest.approx(-0.80)
assert shunt_reactor.scaling == pytest.approx(0.75)

assert shunt_reactor.nominal_voltage_kv == pytest.approx(11.0)

assert shunt_reactor.step_count == 2
assert shunt_reactor.active_steps == 1

assert shunt_reactor.energized_fraction == pytest.approx(0.50)

assert shunt_reactor.reactive_power_per_step_mvar == pytest.approx(
    -0.40
)

assert shunt_reactor.configured_reactive_power_mvar == pytest.approx(
    -0.30
)

assert shunt_reactor.is_capacitive is False
assert shunt_reactor.is_inductive is True
assert shunt_reactor.is_energized is True
assert shunt_reactor.is_fully_energized is False
assert shunt_reactor.is_switched_bank is True


# ---------------------------------------------------------------------------
# Transformer Semantics
# ---------------------------------------------------------------------------

assert fixed_transformer.high_voltage_node_id == bus_hv.id
assert fixed_transformer.low_voltage_node_id == bus_1.id
assert fixed_transformer.nominal_voltage_ratio == pytest.approx(3.0)
assert fixed_transformer.impedance_pu == pytest.approx(0.06)
assert fixed_transformer.resistance_pu == pytest.approx(0.008)
assert fixed_transformer.has_tap_changer is False
assert fixed_transformer.tap_ratio_multiplier == pytest.approx(1.0)
assert fixed_transformer.effective_voltage_ratio == pytest.approx(3.0)
assert fixed_transformer.has_phase_shift is False

assert tapped_transformer.high_voltage_node_id == bus_hv.id
assert tapped_transformer.low_voltage_node_id == bus_2.id
assert tapped_transformer.has_tap_changer is True
assert tapped_transformer.has_phase_shift is True
assert tapped_transformer.tap_position == 2
assert tapped_transformer.minimum_tap_position == -5
assert tapped_transformer.maximum_tap_position == 5
assert tapped_transformer.tap_step_percent == pytest.approx(1.25)
assert tapped_transformer.tap_on_high_voltage_side is True
assert tapped_transformer.tap_ratio_multiplier == pytest.approx(1.025)
assert tapped_transformer.nominal_voltage_ratio == pytest.approx(3.0)
assert tapped_transformer.effective_voltage_ratio == pytest.approx(3.075)


# ---------------------------------------------------------------------------
# Switch Semantics
# ---------------------------------------------------------------------------

assert closed_switch.from_node_id == bus_1.id
assert closed_switch.to_node_id == bus_2.id
assert closed_switch.is_closed is True
assert closed_switch.is_operational is True
assert closed_switch.is_ideal is True
assert closed_switch.rated_voltage_kv == pytest.approx(11.0)
assert closed_switch.rated_current_ka == pytest.approx(0.50)

assert open_switch.from_node_id == bus_1.id
assert open_switch.to_node_id == bus_2.id
assert open_switch.is_closed is False
assert open_switch.is_operational is True
assert open_switch.is_ideal is True
assert open_switch.rated_voltage_kv == pytest.approx(11.0)
assert open_switch.rated_current_ka == pytest.approx(0.40)

assert disabled_closed_switch.from_node_id == bus_1.id
assert disabled_closed_switch.to_node_id == bus_2.id
assert disabled_closed_switch.is_closed is True
assert disabled_closed_switch.is_operational is False
assert disabled_closed_switch.is_ideal is True
assert disabled_closed_switch.rated_voltage_kv == pytest.approx(11.0)
assert disabled_closed_switch.rated_current_ka == pytest.approx(0.30)


# ---------------------------------------------------------------------------
# Reference Source Semantics
# ---------------------------------------------------------------------------

assert reference_source.bus_id == bus_hv.id

assert reference_source.voltage_magnitude_pu == pytest.approx(
    1.01
)

assert reference_source.voltage_angle_deg == pytest.approx(
    5.0
)

# ============================================================================
# Add Elements to Network
# ============================================================================


network.add(bus_hv)
network.add(bus_1)
network.add(bus_2)

network.add(line)

network.add(load)

network.add(generator)
network.add(voltage_generator_1)
network.add(voltage_generator_2)

network.add(solar_pq)
network.add(solar_voltage_controlled)

network.add(wind_pq)
network.add(wind_voltage_controlled)

network.add(capacitor_bank)

network.add(shunt_reactor)

network.add(fixed_transformer)
network.add(tapped_transformer)

network.add(closed_switch)
network.add(open_switch)
network.add(disabled_closed_switch)

network.add(battery_discharging)
network.add(battery_charging)
network.add(battery_idle_var)

network.add(ev_charging)
network.add(ev_v2g)
network.add(ev_disconnected)

# ============================================================================
# Convert to Pandapower
# ============================================================================


converter = PandapowerConverter()

conversion = converter.convert(
    network,
    reference_sources=(
        reference_source,
    ),
)

pp_net = conversion.network


# ============================================================================
# Inspect Pandapower Network
# ============================================================================


print("\n=== Pandapower Network ===")
print(pp_net)

print("\n=== Bus Table ===")
print(pp_net.bus)

print("\n=== External Grid Table ===")
print(pp_net.ext_grid)

print("\n=== Line Table ===")
print(pp_net.line)

print("\n=== Load Table ===")
print(pp_net.load)

print("\n=== Static Generator Table ===")
print(pp_net.sgen)

print("\n=== Voltage-Controlled Generator Table ===")
print(pp_net.gen)

print("\n=== Battery / EV Storage Table ===")
print(pp_net.storage)

print("\n=== Shunt Table ===")
print(pp_net.shunt)

print("\n=== Transformer Table ===")
print(pp_net.trafo)

print("\n=== Switch Table ===")
print(pp_net.switch)

print("\n=== Bus Mapping ===")
print(conversion.bus_indices)

print("\n=== Element Mapping ===")
print(conversion.element_indices)

print("\n=== Element Table Mapping ===")
for element_id, mapping in conversion.element_mappings.items():
    print(
        f"{element_id} -> "
        f"{mapping.table}[{mapping.index}]"
    )

# ============================================================================
# Structural Assertions
# ============================================================================


assert len(pp_net.bus) == 3
assert len(pp_net.ext_grid) == 1

assert len(pp_net.line) == 1
assert len(pp_net.load) == 1

# Generator 1, Voltage Generator 1, Solar PQ 1, and Wind PQ 1 are not
# voltage-controlled. All four belong in pandapower sgen.

assert len(pp_net.sgen) == 4

# Voltage Generator 2, Solar Voltage Controlled 1, and
# Wind Voltage Controlled 1 explicitly enable voltage control and
# therefore belong in pandapower gen.

assert len(pp_net.gen) == 3

# All three Battery objects and all three EV objects must be
# represented using the pandapower storage table.

assert len(pp_net.storage) == 6

# Both GridStudio Shunt objects must be represented using the
# pandapower shunt table.

assert len(pp_net.shunt) == 2
assert len(pp_net.trafo) == 2
assert len(pp_net.switch) == 3


# ============================================================================
# Bus Mapping
# ============================================================================


assert bus_hv.id in conversion.bus_indices
assert bus_1.id in conversion.bus_indices
assert bus_2.id in conversion.bus_indices

bus_hv_index = conversion.bus_indices[bus_hv.id]
bus_1_index = conversion.bus_indices[bus_1.id]
bus_2_index = conversion.bus_indices[bus_2.id]

assert bus_hv_index in pp_net.bus.index
assert bus_1_index in pp_net.bus.index
assert bus_2_index in pp_net.bus.index


# ---------------------------------------------------------------------------
# Bus Element Mapping
# ---------------------------------------------------------------------------


assert bus_hv.id in conversion.element_indices
assert bus_1.id in conversion.element_indices
assert bus_2.id in conversion.element_indices

assert int(conversion.element_indices[bus_hv.id]) == int(bus_hv_index)

assert (
    int(conversion.element_indices[bus_1.id])
    == int(bus_1_index)
)

assert (
    int(conversion.element_indices[bus_2.id])
    == int(bus_2_index)
)


# ============================================================================
# Bus Properties
# ============================================================================


assert pp_net.bus.loc[bus_hv_index, "name"] == "Bus HV"
assert pp_net.bus.loc[bus_1_index, "name"] == "Bus 1"
assert pp_net.bus.loc[bus_2_index, "name"] == "Bus 2"

assert pp_net.bus.loc[
    bus_hv_index,
    "vn_kv",
] == pytest.approx(33.0)

assert pp_net.bus.loc[
    bus_1_index,
    "vn_kv",
] == pytest.approx(11.0)

assert pp_net.bus.loc[
    bus_2_index,
    "vn_kv",
] == pytest.approx(11.0)

assert bool(
    pp_net.bus.loc[bus_1_index, "in_service"]
) is True

assert bool(
    pp_net.bus.loc[bus_2_index, "in_service"]
) is True


# ============================================================================
# Reference Source / External Grid Conversion
# ============================================================================

# ReferenceSource is simulation configuration and therefore has no
# GridStudio physical-element UUID mapping in element_indices.
#
# Its bus reference is resolved through the existing bus_indices
# mapping and converted to a pandapower ext_grid.

assert len(pp_net.ext_grid) == 1

ext_grid_index = int(pp_net.ext_grid.index[0])

pp_reference_source = pp_net.ext_grid.loc[
    ext_grid_index
]


# ---------------------------------------------------------------------------
# Reference Source Connectivity
# ---------------------------------------------------------------------------

assert (
    int(pp_reference_source["bus"])
    == int(bus_hv_index)
)


# ---------------------------------------------------------------------------
# Reference Voltage Magnitude
# ---------------------------------------------------------------------------

assert pp_reference_source["vm_pu"] == pytest.approx(
    reference_source.voltage_magnitude_pu
)


# ---------------------------------------------------------------------------
# Reference Voltage Angle
# ---------------------------------------------------------------------------

assert pp_reference_source["va_degree"] == pytest.approx(
    reference_source.voltage_angle_deg
)


# ---------------------------------------------------------------------------
# Reference Source Classification
# ---------------------------------------------------------------------------

# The reference source is not physical Network equipment and must
# therefore not appear in GridStudio's element-index mapping.
#
# bus_hv itself remains mapped normally.

assert reference_source.bus_id in conversion.bus_indices

assert (
    int(conversion.bus_indices[reference_source.bus_id])
    == int(bus_hv_index)
)

# ============================================================================
# Line Mapping
# ============================================================================


assert line.id in conversion.element_indices

line_mapping = conversion.element_indices[line.id]

print("\n=== Line Mapping ===")
print(line_mapping)


# ---------------------------------------------------------------------------
# Resolve Pandapower Line Index
# ---------------------------------------------------------------------------

# pandapower/pandas may return numpy integer types.
#
# Integral is therefore used instead of plain int.


if isinstance(line_mapping, Integral):
    line_index = int(line_mapping)

elif (
    isinstance(line_mapping, tuple)
    and len(line_mapping) == 2
):
    # Retain compatibility in case the mapping contract later evolves
    # to an (element_type, index) representation.

    element_type, line_index = line_mapping

    assert element_type == "line"

    line_index = int(line_index)

else:
    raise AssertionError(
        f"Unexpected line mapping: {line_mapping!r}"
    )


assert line_index in pp_net.line.index

pp_line = pp_net.line.loc[line_index]


# ============================================================================
# Line Connectivity
# ============================================================================


assert int(pp_line["from_bus"]) == int(bus_1_index)
assert int(pp_line["to_bus"]) == int(bus_2_index)


# ============================================================================
# Line Electrical Parameters
# ============================================================================


assert pp_line["name"] == "Line 1-2"

assert pp_line["length_km"] == pytest.approx(5.0)
assert pp_line["r_ohm_per_km"] == pytest.approx(0.10)
assert pp_line["x_ohm_per_km"] == pytest.approx(0.20)

# pandapower create_line_from_parameters() uses capacitance
# directly in nF/km.

assert pp_line["c_nf_per_km"] == pytest.approx(10.0)
assert pp_line["max_i_ka"] == pytest.approx(0.40)

assert int(pp_line["parallel"]) == 1


# ============================================================================
# Line Operational State
# ============================================================================


assert bool(pp_line["in_service"]) is True


# ============================================================================
# Load Mapping
# ============================================================================


assert load.id in conversion.element_indices

load_mapping = conversion.element_indices[load.id]

print("\n=== Load Mapping ===")
print(load_mapping)

assert isinstance(load_mapping, Integral)

load_index = int(load_mapping)

assert load_index in pp_net.load.index

pp_load = pp_net.load.loc[load_index]


# ============================================================================
# Load Connectivity
# ============================================================================


assert int(pp_load["bus"]) == int(bus_2_index)

assert pp_load["name"] == "Load 2"


# ============================================================================
# Load Power Sign Convention
# ============================================================================

# GridStudio stores this conventional load as:
#
#     P = -2.5 MW
#     Q = -0.75 MVAr
#
# pandapower's load table uses positive P/Q for consumption.
#
# Therefore the converter boundary translates:
#
#     GridStudio P = -2.5
#         -> pandapower p_mw = +2.5
#
#     GridStudio Q = -0.75
#         -> pandapower q_mvar = +0.75
#
# The base powers must NOT be pre-scaled because pandapower
# receives the GridStudio scaling factor separately.


assert pp_load["p_mw"] == pytest.approx(2.5)
assert pp_load["q_mvar"] == pytest.approx(0.75)


# ============================================================================
# Load Scaling
# ============================================================================


assert pp_load["scaling"] == pytest.approx(0.8)


# ---------------------------------------------------------------------------
# Effective Load
# ---------------------------------------------------------------------------


effective_pp_load_p_mw = (
    float(pp_load["p_mw"])
    * float(pp_load["scaling"])
)

effective_pp_load_q_mvar = (
    float(pp_load["q_mvar"])
    * float(pp_load["scaling"])
)


assert effective_pp_load_p_mw == pytest.approx(
    load.active_demand_mw
)

assert effective_pp_load_q_mvar == pytest.approx(
    load.reactive_demand_mvar
)


# ============================================================================
# Load Operational State
# ============================================================================


assert bool(pp_load["in_service"]) is True


# ============================================================================
# Static Generator Mapping
# ============================================================================


assert generator.id in conversion.element_indices

generator_mapping = conversion.element_indices[generator.id]

print("\n=== Generator Mapping ===")
print(generator_mapping)

assert isinstance(generator_mapping, Integral)

generator_index = int(generator_mapping)

assert generator_index in pp_net.sgen.index

pp_generator = pp_net.sgen.loc[generator_index]


# ============================================================================
# Static Generator Connectivity
# ============================================================================


assert int(pp_generator["bus"]) == int(bus_1_index)

assert pp_generator["name"] == "Generator 1"


# ============================================================================
# Static Generator Power Sign Convention
# ============================================================================

# GridStudio Generator:
#
#     positive P = active-power injection
#     positive Q = reactive-power injection
#
# pandapower sgen uses the generator-oriented sign convention for
# p_mw and q_mvar.
#
# Therefore there is NO sign inversion at this conversion boundary:
#
#     GridStudio P = +1.8
#         -> pandapower p_mw = +1.8
#
#     GridStudio Q = +0.30
#         -> pandapower q_mvar = +0.30
#
# As with Load, base powers remain unscaled and the scaling factor
# is transferred separately.


assert pp_generator["p_mw"] == pytest.approx(1.8)
assert pp_generator["q_mvar"] == pytest.approx(0.30)


# ============================================================================
# Static Generator Scaling
# ============================================================================


assert pp_generator["scaling"] == pytest.approx(0.75)


# ---------------------------------------------------------------------------
# Effective Static Generator Output
# ---------------------------------------------------------------------------


effective_pp_generator_p_mw = (
    float(pp_generator["p_mw"])
    * float(pp_generator["scaling"])
)

effective_pp_generator_q_mvar = (
    float(pp_generator["q_mvar"])
    * float(pp_generator["scaling"])
)


assert effective_pp_generator_p_mw == pytest.approx(
    generator.active_generation_mw
)

assert effective_pp_generator_q_mvar == pytest.approx(
    generator.reactive_generation_mvar
)


# ============================================================================
# Static Generator Rating and Limits
# ============================================================================


assert pp_generator["sn_mva"] == pytest.approx(3.0)

assert pp_generator["min_p_mw"] == pytest.approx(0.0)
assert pp_generator["max_p_mw"] == pytest.approx(2.5)

assert pp_generator["min_q_mvar"] == pytest.approx(-0.5)
assert pp_generator["max_q_mvar"] == pytest.approx(0.6)


# ============================================================================
# Static Generator Operational State
# ============================================================================


assert bool(pp_generator["in_service"]) is True


# ============================================================================
# Voltage Generator 1 Mapping
# ============================================================================

# Voltage Generator 1 has a voltage setpoint but voltage control
# is disabled.
#
# It must therefore be represented as an sgen.


assert voltage_generator_1.id in conversion.element_indices

voltage_generator_1_mapping = (
    conversion.element_indices[voltage_generator_1.id]
)

print("\n=== Voltage Generator 1 Mapping ===")
print(voltage_generator_1_mapping)

assert isinstance(
    voltage_generator_1_mapping,
    Integral,
)

voltage_generator_1_index = int(
    voltage_generator_1_mapping
)

assert voltage_generator_1_index in pp_net.sgen.index

pp_voltage_generator_1 = pp_net.sgen.loc[
    voltage_generator_1_index
]


# ============================================================================
# Voltage Generator 1 Properties
# ============================================================================


assert (
    int(pp_voltage_generator_1["bus"])
    == int(bus_2_index)
)

assert (
    pp_voltage_generator_1["name"]
    == "Voltage Generator 1"
)

assert pp_voltage_generator_1["p_mw"] == pytest.approx(0.8)
assert pp_voltage_generator_1["q_mvar"] == pytest.approx(0.15)

assert pp_voltage_generator_1["scaling"] == pytest.approx(1.0)

assert pp_voltage_generator_1["sn_mva"] == pytest.approx(1.5)

assert pp_voltage_generator_1["min_p_mw"] == pytest.approx(0.0)
assert pp_voltage_generator_1["max_p_mw"] == pytest.approx(1.2)

assert pp_voltage_generator_1["min_q_mvar"] == pytest.approx(-0.3)
assert pp_voltage_generator_1["max_q_mvar"] == pytest.approx(0.4)

assert bool(
    pp_voltage_generator_1["in_service"]
) is True


# ============================================================================
# Voltage Generator 2 Mapping
# ============================================================================

# Voltage Generator 2 has:
#
#     voltage_control_enabled = True
#     voltage_setpoint_pu = 1.02
#
# Therefore it must be represented by pandapower gen.


assert voltage_generator_2.id in conversion.element_indices

voltage_generator_2_mapping = (
    conversion.element_indices[voltage_generator_2.id]
)

print("\n=== Voltage Generator 2 Mapping ===")
print(voltage_generator_2_mapping)

assert isinstance(
    voltage_generator_2_mapping,
    Integral,
)

voltage_generator_2_index = int(
    voltage_generator_2_mapping
)

assert voltage_generator_2_index in pp_net.gen.index

pp_voltage_generator_2 = pp_net.gen.loc[
    voltage_generator_2_index
]


# ============================================================================
# Voltage-Controlled Generator Connectivity
# ============================================================================


assert (
    int(pp_voltage_generator_2["bus"])
    == int(bus_2_index)
)

assert (
    pp_voltage_generator_2["name"]
    == "Voltage Generator 2"
)


# ============================================================================
# Voltage-Controlled Generator P-V Boundary
# ============================================================================

# Unlike sgen, pandapower gen represents a voltage-controlled
# generator using specified active power and voltage magnitude.
#
# Reactive power is not transferred as a fixed operating-point
# q_mvar value. It is determined by the power-flow solution,
# subject to reactive-power limits.


assert pp_voltage_generator_2["p_mw"] == pytest.approx(1.2)

assert pp_voltage_generator_2["vm_pu"] == pytest.approx(1.02)


# ============================================================================
# Voltage-Controlled Generator Scaling
# ============================================================================


assert pp_voltage_generator_2["scaling"] == pytest.approx(1.0)


# ============================================================================
# Voltage-Controlled Generator Rating
# ============================================================================


assert pp_voltage_generator_2["sn_mva"] == pytest.approx(2.0)


# ============================================================================
# Voltage-Controlled Generator Active-Power Limits
# ============================================================================


assert pp_voltage_generator_2["min_p_mw"] == pytest.approx(0.0)
assert pp_voltage_generator_2["max_p_mw"] == pytest.approx(1.8)


# ============================================================================
# Voltage-Controlled Generator Reactive-Power Limits
# ============================================================================


assert pp_voltage_generator_2["min_q_mvar"] == pytest.approx(-0.4)
assert pp_voltage_generator_2["max_q_mvar"] == pytest.approx(0.6)


# ============================================================================
# Voltage-Controlled Generator Operational State
# ============================================================================


assert bool(
    pp_voltage_generator_2["in_service"]
) is True


# ============================================================================
# Cross-Table Generator Classification
# ============================================================================

# Verify the classification boundary explicitly:
#
#     Generator 1
#         -> sgen
#
#     Voltage Generator 1
#         -> sgen
#
#     Voltage Generator 2
#         -> gen


sgen_names = set(pp_net.sgen["name"].tolist())
gen_names = set(pp_net.gen["name"].tolist())

assert "Generator 1" in sgen_names
assert "Voltage Generator 1" in sgen_names
assert "Voltage Generator 2" not in sgen_names

assert "Voltage Generator 2" in gen_names
assert "Generator 1" not in gen_names
assert "Voltage Generator 1" not in gen_names


# ============================================================================
# Solar PQ Mapping
# ============================================================================

assert solar_pq.id in conversion.element_indices
solar_pq_mapping = conversion.element_indices[solar_pq.id]

print("\n=== Solar PQ Mapping ===")
print(solar_pq_mapping)

assert isinstance(solar_pq_mapping, Integral)
solar_pq_index = int(solar_pq_mapping)
assert solar_pq_index in pp_net.sgen.index

pp_solar_pq = pp_net.sgen.loc[solar_pq_index]

assert int(pp_solar_pq["bus"]) == int(bus_1_index)
assert pp_solar_pq["name"] == "Solar PQ 1"
assert pp_solar_pq["p_mw"] == pytest.approx(1.5)
assert pp_solar_pq["q_mvar"] == pytest.approx(0.20)
assert pp_solar_pq["scaling"] == pytest.approx(0.90)
assert pp_solar_pq["sn_mva"] == pytest.approx(2.0)
assert pp_solar_pq["min_p_mw"] == pytest.approx(0.0)
assert pp_solar_pq["max_p_mw"] == pytest.approx(2.0)
assert pp_solar_pq["min_q_mvar"] == pytest.approx(-0.6)
assert pp_solar_pq["max_q_mvar"] == pytest.approx(0.6)
assert bool(pp_solar_pq["in_service"]) is True

effective_pp_solar_p_mw = float(pp_solar_pq["p_mw"]) * float(pp_solar_pq["scaling"])
effective_pp_solar_q_mvar = float(pp_solar_pq["q_mvar"]) * float(pp_solar_pq["scaling"])

assert effective_pp_solar_p_mw == pytest.approx(solar_pq.active_generation_mw)
assert effective_pp_solar_q_mvar == pytest.approx(solar_pq.reactive_generation_mvar)


# ============================================================================
# Voltage-Controlled Solar Mapping
# ============================================================================

assert solar_voltage_controlled.id in conversion.element_indices
solar_voltage_mapping = conversion.element_indices[solar_voltage_controlled.id]

print("\n=== Voltage-Controlled Solar Mapping ===")
print(solar_voltage_mapping)

assert isinstance(solar_voltage_mapping, Integral)
solar_voltage_index = int(solar_voltage_mapping)
assert solar_voltage_index in pp_net.gen.index

pp_solar_voltage = pp_net.gen.loc[solar_voltage_index]

assert int(pp_solar_voltage["bus"]) == int(bus_2_index)
assert pp_solar_voltage["name"] == "Solar Voltage Controlled 1"
assert pp_solar_voltage["p_mw"] == pytest.approx(1.8)
assert pp_solar_voltage["vm_pu"] == pytest.approx(1.015)
assert pp_solar_voltage["scaling"] == pytest.approx(1.0)
assert pp_solar_voltage["sn_mva"] == pytest.approx(2.5)
assert pp_solar_voltage["min_p_mw"] == pytest.approx(0.0)
assert pp_solar_voltage["max_p_mw"] == pytest.approx(2.5)
assert pp_solar_voltage["min_q_mvar"] == pytest.approx(-0.8)
assert pp_solar_voltage["max_q_mvar"] == pytest.approx(0.8)
assert bool(pp_solar_voltage["in_service"]) is True

# These exact counts also guard against duplicate Solar conversion.
assert list(pp_net.sgen["name"]).count("Solar PQ 1") == 1
assert list(pp_net.gen["name"]).count("Solar Voltage Controlled 1") == 1

sgen_names = set(pp_net.sgen["name"].tolist())
gen_names = set(pp_net.gen["name"].tolist())

assert "Solar PQ 1" in sgen_names
assert "Solar PQ 1" not in gen_names
assert "Solar Voltage Controlled 1" in gen_names
assert "Solar Voltage Controlled 1" not in sgen_names



# ============================================================================
# Wind PQ Mapping
# ============================================================================

assert wind_pq.id in conversion.element_indices
wind_pq_mapping = conversion.element_indices[wind_pq.id]

print("\n=== Wind PQ Mapping ===")
print(wind_pq_mapping)

assert isinstance(wind_pq_mapping, Integral)
wind_pq_index = int(wind_pq_mapping)
assert wind_pq_index in pp_net.sgen.index

pp_wind_pq = pp_net.sgen.loc[wind_pq_index]

assert int(pp_wind_pq["bus"]) == int(bus_1_index)
assert pp_wind_pq["name"] == "Wind PQ 1"
assert pp_wind_pq["p_mw"] == pytest.approx(2.1)
assert pp_wind_pq["q_mvar"] == pytest.approx(0.25)
assert pp_wind_pq["scaling"] == pytest.approx(0.80)
assert pp_wind_pq["sn_mva"] == pytest.approx(3.2)
assert pp_wind_pq["min_p_mw"] == pytest.approx(0.0)
assert pp_wind_pq["max_p_mw"] == pytest.approx(3.0)
assert pp_wind_pq["min_q_mvar"] == pytest.approx(-0.8)
assert pp_wind_pq["max_q_mvar"] == pytest.approx(0.8)
assert bool(pp_wind_pq["in_service"]) is True

effective_pp_wind_p_mw = (
    float(pp_wind_pq["p_mw"])
    * float(pp_wind_pq["scaling"])
)
effective_pp_wind_q_mvar = (
    float(pp_wind_pq["q_mvar"])
    * float(pp_wind_pq["scaling"])
)

assert effective_pp_wind_p_mw == pytest.approx(
    wind_pq.active_generation_mw
)
assert effective_pp_wind_q_mvar == pytest.approx(
    wind_pq.reactive_generation_mvar
)


# ============================================================================
# Voltage-Controlled Wind Mapping
# ============================================================================

assert wind_voltage_controlled.id in conversion.element_indices
wind_voltage_mapping = conversion.element_indices[
    wind_voltage_controlled.id
]

print("\n=== Voltage-Controlled Wind Mapping ===")
print(wind_voltage_mapping)

assert isinstance(wind_voltage_mapping, Integral)
wind_voltage_index = int(wind_voltage_mapping)
assert wind_voltage_index in pp_net.gen.index

pp_wind_voltage = pp_net.gen.loc[wind_voltage_index]

assert int(pp_wind_voltage["bus"]) == int(bus_2_index)
assert pp_wind_voltage["name"] == "Wind Voltage Controlled 1"
assert pp_wind_voltage["p_mw"] == pytest.approx(3.0)
assert pp_wind_voltage["vm_pu"] == pytest.approx(1.01)
assert pp_wind_voltage["scaling"] == pytest.approx(1.0)
assert pp_wind_voltage["sn_mva"] == pytest.approx(4.5)
assert pp_wind_voltage["min_p_mw"] == pytest.approx(0.0)
assert pp_wind_voltage["max_p_mw"] == pytest.approx(4.0)
assert pp_wind_voltage["min_q_mvar"] == pytest.approx(-1.0)
assert pp_wind_voltage["max_q_mvar"] == pytest.approx(1.0)
assert bool(pp_wind_voltage["in_service"]) is True

# Exact-name counts guard against duplicate Wind conversion through both the
# dedicated Network.wind collection and the generic Generator/Injection paths.
assert list(pp_net.sgen["name"]).count("Wind PQ 1") == 1
assert list(pp_net.gen["name"]).count("Wind Voltage Controlled 1") == 1

sgen_names = set(pp_net.sgen["name"].tolist())
gen_names = set(pp_net.gen["name"].tolist())

assert "Wind PQ 1" in sgen_names
assert "Wind PQ 1" not in gen_names
assert "Wind Voltage Controlled 1" in gen_names
assert "Wind Voltage Controlled 1" not in sgen_names


# ============================================================================
# Battery Mapping and Conversion
# ============================================================================

for battery in (
    battery_discharging,
    battery_charging,
    battery_idle_var,
):
    assert battery.id in conversion.element_indices


battery_discharging_mapping = conversion.element_indices[
    battery_discharging.id
]
battery_charging_mapping = conversion.element_indices[
    battery_charging.id
]
battery_idle_var_mapping = conversion.element_indices[
    battery_idle_var.id
]

print("\n=== Battery Discharging Mapping ===")
print(battery_discharging_mapping)

print("\n=== Battery Charging Mapping ===")
print(battery_charging_mapping)

print("\n=== Battery Idle VAR Mapping ===")
print(battery_idle_var_mapping)

assert isinstance(battery_discharging_mapping, Integral)
assert isinstance(battery_charging_mapping, Integral)
assert isinstance(battery_idle_var_mapping, Integral)

battery_discharging_index = int(
    battery_discharging_mapping
)
battery_charging_index = int(
    battery_charging_mapping
)
battery_idle_var_index = int(
    battery_idle_var_mapping
)

assert battery_discharging_index in pp_net.storage.index
assert battery_charging_index in pp_net.storage.index
assert battery_idle_var_index in pp_net.storage.index

pp_battery_discharging = pp_net.storage.loc[
    battery_discharging_index
]
pp_battery_charging = pp_net.storage.loc[
    battery_charging_index
]
pp_battery_idle_var = pp_net.storage.loc[
    battery_idle_var_index
]


# ============================================================================
# Battery Connectivity
# ============================================================================

assert (
    int(pp_battery_discharging["bus"])
    == int(bus_1_index)
)

assert (
    int(pp_battery_charging["bus"])
    == int(bus_2_index)
)

assert (
    int(pp_battery_idle_var["bus"])
    == int(bus_2_index)
)


# ============================================================================
# Battery Names
# ============================================================================

assert pp_battery_discharging["name"] == "Battery Discharging"
assert pp_battery_charging["name"] == "Battery Charging"
assert pp_battery_idle_var["name"] == "Battery Idle VAR"


# ============================================================================
# Battery Active-Power Sign Convention
# ============================================================================

# GridStudio:
#
#     +P = discharge
#     -P = charge
#
# pandapower storage:
#
#     -P = discharge
#     +P = charge

assert pp_battery_discharging["p_mw"] == pytest.approx(-2.0)
assert pp_battery_charging["p_mw"] == pytest.approx(1.5)
assert pp_battery_idle_var["p_mw"] == pytest.approx(0.0)


# ============================================================================
# Battery Reactive-Power Sign Convention
# ============================================================================

# GridStudio:
#
#     +Q = injection
#     -Q = absorption
#
# pandapower storage:
#
#     -Q = injection
#     +Q = absorption

assert pp_battery_discharging["q_mvar"] == pytest.approx(-0.40)
assert pp_battery_charging["q_mvar"] == pytest.approx(0.30)
assert pp_battery_idle_var["q_mvar"] == pytest.approx(-0.25)


# ============================================================================
# Battery Scaling
# ============================================================================

assert pp_battery_discharging["scaling"] == pytest.approx(0.75)
assert pp_battery_charging["scaling"] == pytest.approx(0.80)
assert pp_battery_idle_var["scaling"] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Effective Battery Grid Exchange
# ---------------------------------------------------------------------------

effective_pp_battery_discharging_p_mw = (
    float(pp_battery_discharging["p_mw"])
    * float(pp_battery_discharging["scaling"])
)

effective_pp_battery_charging_p_mw = (
    float(pp_battery_charging["p_mw"])
    * float(pp_battery_charging["scaling"])
)

effective_pp_battery_idle_p_mw = (
    float(pp_battery_idle_var["p_mw"])
    * float(pp_battery_idle_var["scaling"])
)

assert effective_pp_battery_discharging_p_mw == pytest.approx(
    -battery_discharging.effective_active_power_mw
)

assert effective_pp_battery_charging_p_mw == pytest.approx(
    -battery_charging.effective_active_power_mw
)

assert effective_pp_battery_idle_p_mw == pytest.approx(
    -battery_idle_var.effective_active_power_mw
)


# ============================================================================
# Battery Energy and SOC
# ============================================================================

assert pp_battery_discharging["max_e_mwh"] == pytest.approx(8.0)
assert pp_battery_charging["max_e_mwh"] == pytest.approx(6.0)
assert pp_battery_idle_var["max_e_mwh"] == pytest.approx(4.0)

assert pp_battery_discharging["soc_percent"] == pytest.approx(60.0)
assert pp_battery_charging["soc_percent"] == pytest.approx(35.0)
assert pp_battery_idle_var["soc_percent"] == pytest.approx(50.0)


# ============================================================================
# Battery Ratings
# ============================================================================

assert pp_battery_discharging["sn_mva"] == pytest.approx(3.5)
assert pp_battery_charging["sn_mva"] == pytest.approx(3.0)
assert pp_battery_idle_var["sn_mva"] == pytest.approx(2.0)


# ============================================================================
# Battery Active-Power Limits
# ============================================================================

# pandapower storage:
#
#     negative P = discharge
#     positive P = charge
#
# Therefore:
#
#     min_p_mw = -maximum_discharge_power_mw
#     max_p_mw = +maximum_charge_power_mw

assert pp_battery_discharging["min_p_mw"] == pytest.approx(-3.0)
assert pp_battery_discharging["max_p_mw"] == pytest.approx(2.5)

assert pp_battery_charging["min_p_mw"] == pytest.approx(-2.5)
assert pp_battery_charging["max_p_mw"] == pytest.approx(2.0)

assert pp_battery_idle_var["min_p_mw"] == pytest.approx(-1.5)
assert pp_battery_idle_var["max_p_mw"] == pytest.approx(1.5)


# ============================================================================
# Battery Reactive-Power Limits
# ============================================================================

# GridStudio [Qmin, Qmax] maps to:
#
#     pandapower [-Qmax, -Qmin]

assert pp_battery_discharging["min_q_mvar"] == pytest.approx(-1.0)
assert pp_battery_discharging["max_q_mvar"] == pytest.approx(0.8)

assert pp_battery_charging["min_q_mvar"] == pytest.approx(-0.9)
assert pp_battery_charging["max_q_mvar"] == pytest.approx(0.7)

assert pp_battery_idle_var["min_q_mvar"] == pytest.approx(-0.6)
assert pp_battery_idle_var["max_q_mvar"] == pytest.approx(0.5)


# ============================================================================
# Battery Operational State
# ============================================================================

assert bool(pp_battery_discharging["in_service"]) is True
assert bool(pp_battery_charging["in_service"]) is True
assert bool(pp_battery_idle_var["in_service"]) is True


# ============================================================================
# Battery Classification and Duplicate Protection
# ============================================================================

storage_names = set(pp_net.storage["name"].tolist())

assert "Battery Discharging" in storage_names
assert "Battery Charging" in storage_names
assert "Battery Idle VAR" in storage_names

# Each Battery must be converted exactly once.
assert list(pp_net.storage["name"]).count("Battery Discharging") == 1
assert list(pp_net.storage["name"]).count("Battery Charging") == 1
assert list(pp_net.storage["name"]).count("Battery Idle VAR") == 1

# Batteries must not leak into generic generator conversion.
assert "Battery Discharging" not in sgen_names
assert "Battery Charging" not in sgen_names
assert "Battery Idle VAR" not in sgen_names

assert "Battery Discharging" not in gen_names
assert "Battery Charging" not in gen_names
assert "Battery Idle VAR" not in gen_names


# ============================================================================
# EV Mapping and Conversion
# ============================================================================

for ev in (
    ev_charging,
    ev_v2g,
    ev_disconnected,
):
    assert ev.id in conversion.element_indices


ev_charging_mapping = conversion.element_indices[
    ev_charging.id
]
ev_v2g_mapping = conversion.element_indices[
    ev_v2g.id
]
ev_disconnected_mapping = conversion.element_indices[
    ev_disconnected.id
]

print("\n=== EV Charging Mapping ===")
print(ev_charging_mapping)

print("\n=== EV V2G Mapping ===")
print(ev_v2g_mapping)

print("\n=== EV Disconnected Mapping ===")
print(ev_disconnected_mapping)

assert isinstance(ev_charging_mapping, Integral)
assert isinstance(ev_v2g_mapping, Integral)
assert isinstance(ev_disconnected_mapping, Integral)

ev_charging_index = int(ev_charging_mapping)
ev_v2g_index = int(ev_v2g_mapping)
ev_disconnected_index = int(ev_disconnected_mapping)

assert ev_charging_index in pp_net.storage.index
assert ev_v2g_index in pp_net.storage.index
assert ev_disconnected_index in pp_net.storage.index

pp_ev_charging = pp_net.storage.loc[
    ev_charging_index
]
pp_ev_v2g = pp_net.storage.loc[
    ev_v2g_index
]
pp_ev_disconnected = pp_net.storage.loc[
    ev_disconnected_index
]


# ============================================================================
# EV Connectivity
# ============================================================================

assert int(pp_ev_charging["bus"]) == int(bus_2_index)
assert int(pp_ev_v2g["bus"]) == int(bus_1_index)
assert int(pp_ev_disconnected["bus"]) == int(bus_2_index)


# ============================================================================
# EV Names
# ============================================================================

assert pp_ev_charging["name"] == "EV Charging"
assert pp_ev_v2g["name"] == "EV V2G"
assert pp_ev_disconnected["name"] == "EV Disconnected"


# ============================================================================
# EV Active-Power Sign Convention
# ============================================================================

# GridStudio EV:
#
#     -P = charging
#     +P = V2G discharge
#
# pandapower storage:
#
#     +P = charging
#     -P = discharge

assert pp_ev_charging["p_mw"] == pytest.approx(0.018)
assert pp_ev_v2g["p_mw"] == pytest.approx(-0.020)
assert pp_ev_disconnected["p_mw"] == pytest.approx(0.0)


# ============================================================================
# EV Reactive-Power Sign Convention
# ============================================================================

assert pp_ev_charging["q_mvar"] == pytest.approx(0.004)
assert pp_ev_v2g["q_mvar"] == pytest.approx(-0.005)
assert pp_ev_disconnected["q_mvar"] == pytest.approx(0.0)


# ============================================================================
# EV Scaling
# ============================================================================

assert pp_ev_charging["scaling"] == pytest.approx(0.80)
assert pp_ev_v2g["scaling"] == pytest.approx(0.75)
assert pp_ev_disconnected["scaling"] == pytest.approx(1.0)


# ============================================================================
# EV Effective Grid Exchange
# ============================================================================

effective_pp_ev_charging_p_mw = (
    float(pp_ev_charging["p_mw"])
    * float(pp_ev_charging["scaling"])
)

effective_pp_ev_v2g_p_mw = (
    float(pp_ev_v2g["p_mw"])
    * float(pp_ev_v2g["scaling"])
)

assert effective_pp_ev_charging_p_mw == pytest.approx(
    -ev_charging.effective_active_power_mw
)

assert effective_pp_ev_v2g_p_mw == pytest.approx(
    -ev_v2g.effective_active_power_mw
)


# ============================================================================
# EV Energy Capacity and SOC
# ============================================================================

assert pp_ev_charging["max_e_mwh"] == pytest.approx(0.080)
assert pp_ev_v2g["max_e_mwh"] == pytest.approx(0.100)
assert pp_ev_disconnected["max_e_mwh"] == pytest.approx(0.060)

assert pp_ev_charging["soc_percent"] == pytest.approx(40.0)
assert pp_ev_v2g["soc_percent"] == pytest.approx(70.0)
assert pp_ev_disconnected["soc_percent"] == pytest.approx(55.0)


# ============================================================================
# EV Charger Rating
# ============================================================================

assert pp_ev_charging["sn_mva"] == pytest.approx(0.025)
assert pp_ev_v2g["sn_mva"] == pytest.approx(0.035)
assert pp_ev_disconnected["sn_mva"] == pytest.approx(0.015)


# ============================================================================
# EV Active-Power Limits
# ============================================================================

# GridStudio:
#
#     maximum_charge_power_mw    = positive charging magnitude
#     maximum_discharge_power_mw = positive V2G magnitude
#
# pandapower storage:
#
#     positive P = charging
#     negative P = discharging
#
# Therefore:
#
#     min_p_mw = -maximum_discharge_power_mw
#     max_p_mw = +maximum_charge_power_mw

assert pp_ev_charging["min_p_mw"] == pytest.approx(0.0)
assert pp_ev_charging["max_p_mw"] == pytest.approx(0.022)

assert pp_ev_v2g["min_p_mw"] == pytest.approx(-0.025)
assert pp_ev_v2g["max_p_mw"] == pytest.approx(0.030)

assert pp_ev_disconnected["min_p_mw"] == pytest.approx(0.0)
assert pp_ev_disconnected["max_p_mw"] == pytest.approx(0.011)


# ============================================================================
# EV Reactive-Power Limits
# ============================================================================

# GridStudio [Qmin, Qmax] maps to pandapower [-Qmax, -Qmin].

assert pp_ev_charging["min_q_mvar"] == pytest.approx(-0.010)
assert pp_ev_charging["max_q_mvar"] == pytest.approx(0.010)

assert pp_ev_v2g["min_q_mvar"] == pytest.approx(-0.015)
assert pp_ev_v2g["max_q_mvar"] == pytest.approx(0.012)


# ============================================================================
# EV Operational / Connection State
# ============================================================================

assert bool(pp_ev_charging["in_service"]) is True
assert bool(pp_ev_v2g["in_service"]) is True

# The asset itself may be operational, but a physically disconnected
# EV must not participate electrically in the pandapower network.

assert ev_disconnected.is_operational is True
assert ev_disconnected.is_connected is False
assert bool(pp_ev_disconnected["in_service"]) is False


# ============================================================================
# EV Classification and Duplicate Protection
# ============================================================================

storage_names = list(pp_net.storage["name"])

assert storage_names.count("EV Charging") == 1
assert storage_names.count("EV V2G") == 1
assert storage_names.count("EV Disconnected") == 1

# EVs must not leak into generic generator conversion.

assert "EV Charging" not in sgen_names
assert "EV V2G" not in sgen_names
assert "EV Disconnected" not in sgen_names

assert "EV Charging" not in gen_names
assert "EV V2G" not in gen_names
assert "EV Disconnected" not in gen_names


# ============================================================================
# Capacitor-Bank Mapping
# ============================================================================


assert capacitor_bank.id in conversion.element_indices

capacitor_mapping = conversion.element_indices[
    capacitor_bank.id
]

print("\n=== Capacitor Bank Mapping ===")
print(capacitor_mapping)

assert isinstance(capacitor_mapping, Integral)

capacitor_index = int(capacitor_mapping)

assert capacitor_index in pp_net.shunt.index

pp_capacitor = pp_net.shunt.loc[
    capacitor_index
]


# ============================================================================
# Capacitor-Bank Connectivity
# ============================================================================


assert int(pp_capacitor["bus"]) == int(bus_2_index)

assert pp_capacitor["name"] == "Capacitor Bank 2"


# ============================================================================
# Capacitor-Bank Step Conversion
# ============================================================================

# GridStudio:
#
#     total rated Q = +1.20 MVAr
#     step_count    = 4
#     scaling       = 0.50
#
# GridStudio rated Q per physical step:
#
#     +1.20 / 4 = +0.30 MVAr
#
# The converter applies GridStudio scaling to the per-step value:
#
#     +0.30 * 0.50 = +0.15 MVAr/step
#
# pandapower uses the opposite sign convention for shunt Q:
#
#     capacitive injection -> negative q_mvar
#
# Therefore:
#
#     pandapower q_mvar = -0.15 MVAr/step
#
# active_steps maps to pandapower step:
#
#     step = 3
#
# Effective nominal-voltage exchange:
#
#     -0.15 * 3 = -0.45 MVAr
#
# which is the sign-inverted equivalent of GridStudio's
# configured_reactive_power_mvar = +0.45 MVAr.


assert pp_capacitor["q_mvar"] == pytest.approx(-0.15)

assert int(pp_capacitor["step"]) == 3


effective_pp_capacitor_q_mvar = (
    float(pp_capacitor["q_mvar"])
    * int(pp_capacitor["step"])
)


assert effective_pp_capacitor_q_mvar == pytest.approx(
    -capacitor_bank.configured_reactive_power_mvar
)


# ============================================================================
# Capacitor-Bank Active Power
# ============================================================================

# Shunt active_power_mw represents active losses when required.
#
# This capacitor bank has no active losses.


assert pp_capacitor["p_mw"] == pytest.approx(0.0)


# ============================================================================
# Capacitor-Bank Operational State
# ============================================================================


assert bool(pp_capacitor["in_service"]) is True


# ============================================================================
# Shunt-Reactor Mapping
# ============================================================================


assert shunt_reactor.id in conversion.element_indices

reactor_mapping = conversion.element_indices[
    shunt_reactor.id
]

print("\n=== Shunt Reactor Mapping ===")
print(reactor_mapping)

assert isinstance(reactor_mapping, Integral)

reactor_index = int(reactor_mapping)

assert reactor_index in pp_net.shunt.index

pp_reactor = pp_net.shunt.loc[
    reactor_index
]


# ============================================================================
# Shunt-Reactor Connectivity
# ============================================================================


assert int(pp_reactor["bus"]) == int(bus_1_index)

assert pp_reactor["name"] == "Shunt Reactor 1"


# ============================================================================
# Shunt-Reactor Step Conversion
# ============================================================================

# GridStudio:
#
#     total rated Q = -0.80 MVAr
#     step_count    = 2
#     scaling       = 0.75
#
# GridStudio rated Q per physical step:
#
#     -0.80 / 2 = -0.40 MVAr
#
# Apply GridStudio scaling:
#
#     -0.40 * 0.75 = -0.30 MVAr/step
#
# pandapower uses the opposite shunt-Q sign convention:
#
#     inductive absorption -> positive q_mvar
#
# Therefore:
#
#     pandapower q_mvar = +0.30 MVAr/step
#
# active_steps maps to pandapower step:
#
#     step = 1
#
# Effective nominal-voltage exchange:
#
#     +0.30 * 1 = +0.30 MVAr
#
# which is the sign-inverted equivalent of GridStudio's
# configured_reactive_power_mvar = -0.30 MVAr.


assert pp_reactor["q_mvar"] == pytest.approx(0.30)

assert int(pp_reactor["step"]) == 1


effective_pp_reactor_q_mvar = (
    float(pp_reactor["q_mvar"])
    * int(pp_reactor["step"])
)


assert effective_pp_reactor_q_mvar == pytest.approx(
    -shunt_reactor.configured_reactive_power_mvar
)


# ============================================================================
# Shunt-Reactor Active Power
# ============================================================================


assert pp_reactor["p_mw"] == pytest.approx(0.0)


# ============================================================================
# Shunt-Reactor Operational State
# ============================================================================


assert bool(pp_reactor["in_service"]) is True


# ============================================================================
# Cross-Table Shunt Classification
# ============================================================================


shunt_names = set(pp_net.shunt["name"].tolist())

assert "Capacitor Bank 2" in shunt_names
assert "Shunt Reactor 1" in shunt_names

assert "Capacitor Bank 2" not in sgen_names
assert "Shunt Reactor 1" not in sgen_names


# ============================================================================
# Transformer Mapping and Conversion
# ============================================================================

assert fixed_transformer.id in conversion.element_indices
assert tapped_transformer.id in conversion.element_indices

fixed_transformer_mapping = conversion.element_indices[fixed_transformer.id]
tapped_transformer_mapping = conversion.element_indices[tapped_transformer.id]

print("\n=== Fixed Transformer Mapping ===")
print(fixed_transformer_mapping)

print("\n=== Tapped Transformer Mapping ===")
print(tapped_transformer_mapping)

assert isinstance(fixed_transformer_mapping, Integral)
assert isinstance(tapped_transformer_mapping, Integral)

fixed_transformer_index = int(fixed_transformer_mapping)
tapped_transformer_index = int(tapped_transformer_mapping)

assert fixed_transformer_index in pp_net.trafo.index
assert tapped_transformer_index in pp_net.trafo.index

pp_fixed_transformer = pp_net.trafo.loc[fixed_transformer_index]
pp_tapped_transformer = pp_net.trafo.loc[tapped_transformer_index]

# Fixed-ratio transformer
assert pp_fixed_transformer["name"] == "Transformer Fixed 33/11 kV"
assert int(pp_fixed_transformer["hv_bus"]) == int(bus_hv_index)
assert int(pp_fixed_transformer["lv_bus"]) == int(bus_1_index)
assert pp_fixed_transformer["sn_mva"] == pytest.approx(10.0)
assert pp_fixed_transformer["vn_hv_kv"] == pytest.approx(33.0)
assert pp_fixed_transformer["vn_lv_kv"] == pytest.approx(11.0)
assert pp_fixed_transformer["vk_percent"] == pytest.approx(6.0)
assert pp_fixed_transformer["vkr_percent"] == pytest.approx(0.8)
assert pp_fixed_transformer["pfe_kw"] == pytest.approx(12.0)
assert pp_fixed_transformer["i0_percent"] == pytest.approx(0.25)
assert pp_fixed_transformer["shift_degree"] == pytest.approx(0.0)
assert bool(pp_fixed_transformer["in_service"]) is True

# Tapped transformer
assert pp_tapped_transformer["name"] == "Transformer Tapped 33/11 kV"
assert int(pp_tapped_transformer["hv_bus"]) == int(bus_hv_index)
assert int(pp_tapped_transformer["lv_bus"]) == int(bus_2_index)
assert pp_tapped_transformer["sn_mva"] == pytest.approx(16.0)
assert pp_tapped_transformer["vn_hv_kv"] == pytest.approx(33.0)
assert pp_tapped_transformer["vn_lv_kv"] == pytest.approx(11.0)
assert pp_tapped_transformer["vk_percent"] == pytest.approx(8.0)
assert pp_tapped_transformer["vkr_percent"] == pytest.approx(1.0)
assert pp_tapped_transformer["pfe_kw"] == pytest.approx(18.0)
assert pp_tapped_transformer["i0_percent"] == pytest.approx(0.30)
assert pp_tapped_transformer["shift_degree"] == pytest.approx(30.0)
assert pp_tapped_transformer["tap_side"] == "hv"
assert int(pp_tapped_transformer["tap_neutral"]) == 0
assert int(pp_tapped_transformer["tap_pos"]) == 2
assert int(pp_tapped_transformer["tap_min"]) == -5
assert int(pp_tapped_transformer["tap_max"]) == 5
assert pp_tapped_transformer["tap_step_percent"] == pytest.approx(1.25)
assert bool(pp_tapped_transformer["in_service"]) is True

trafo_names = set(pp_net.trafo["name"].tolist())
assert "Transformer Fixed 33/11 kV" in trafo_names
assert "Transformer Tapped 33/11 kV" in trafo_names


# ============================================================================
# Switch Mapping and Conversion
# ============================================================================

assert closed_switch.id in conversion.element_indices
assert open_switch.id in conversion.element_indices
assert disabled_closed_switch.id in conversion.element_indices

closed_switch_mapping = conversion.element_indices[closed_switch.id]
open_switch_mapping = conversion.element_indices[open_switch.id]
disabled_closed_switch_mapping = (
    conversion.element_indices[disabled_closed_switch.id]
)

print("\n=== Closed Switch Mapping ===")
print(closed_switch_mapping)

print("\n=== Open Switch Mapping ===")
print(open_switch_mapping)

print("\n=== Disabled Closed Switch Mapping ===")
print(disabled_closed_switch_mapping)

assert isinstance(closed_switch_mapping, Integral)
assert isinstance(open_switch_mapping, Integral)
assert isinstance(disabled_closed_switch_mapping, Integral)

closed_switch_index = int(closed_switch_mapping)
open_switch_index = int(open_switch_mapping)
disabled_closed_switch_index = int(
    disabled_closed_switch_mapping
)

assert closed_switch_index in pp_net.switch.index
assert open_switch_index in pp_net.switch.index
assert disabled_closed_switch_index in pp_net.switch.index

pp_closed_switch = pp_net.switch.loc[closed_switch_index]
pp_open_switch = pp_net.switch.loc[open_switch_index]
pp_disabled_closed_switch = pp_net.switch.loc[
    disabled_closed_switch_index
]


# ---------------------------------------------------------------------------
# Switch Connectivity
# ---------------------------------------------------------------------------

# GridStudio Switch is converted as a pandapower bus-bus switch:
#
#     bus     = from_node_id
#     element = to_node_id
#     et      = "b"

for pp_switch in (
    pp_closed_switch,
    pp_open_switch,
    pp_disabled_closed_switch,
):
    assert int(pp_switch["bus"]) == int(bus_1_index)
    assert int(pp_switch["element"]) == int(bus_2_index)
    assert pp_switch["et"] == "b"


# ---------------------------------------------------------------------------
# Switch Names
# ---------------------------------------------------------------------------

assert pp_closed_switch["name"] == "Switch Closed"
assert pp_open_switch["name"] == "Switch Open"
assert (
    pp_disabled_closed_switch["name"]
    == "Switch Disabled Closed"
)


# ---------------------------------------------------------------------------
# Switch Current Ratings
# ---------------------------------------------------------------------------

assert pp_closed_switch["in_ka"] == pytest.approx(0.50)
assert pp_open_switch["in_ka"] == pytest.approx(0.40)
assert pp_disabled_closed_switch["in_ka"] == pytest.approx(0.30)


# ---------------------------------------------------------------------------
# Switch State Boundary
# ---------------------------------------------------------------------------

# Configured closed + operational -> electrically closed.
assert bool(pp_closed_switch["closed"]) is True

# Configured open + operational -> electrically open.
assert bool(pp_open_switch["closed"]) is False

# Configured closed but non-operational -> electrically isolated.
assert bool(pp_disabled_closed_switch["closed"]) is False


# ---------------------------------------------------------------------------
# Switch Classification
# ---------------------------------------------------------------------------

switch_names = set(pp_net.switch["name"].tolist())

assert "Switch Closed" in switch_names
assert "Switch Open" in switch_names
assert "Switch Disabled Closed" in switch_names

# ============================================================================
# Element Mapping
# ============================================================================

expected_tables = {
    line.id: "line",
    load.id: "load",
    generator.id: "sgen",
    voltage_generator_1.id: "sgen",
    voltage_generator_2.id: "gen",
    solar_pq.id: "sgen",
    solar_voltage_controlled.id: "gen",
    wind_pq.id: "sgen",
    wind_voltage_controlled.id: "gen",
    capacitor_bank.id: "shunt",
    shunt_reactor.id: "shunt",
    fixed_transformer.id: "trafo",
    tapped_transformer.id: "trafo",
    closed_switch.id: "switch",
    open_switch.id: "switch",
    disabled_closed_switch.id: "switch",
    battery_discharging.id: "storage",
    battery_charging.id: "storage",
    battery_idle_var.id: "storage",
    ev_charging.id: "storage",
    ev_v2g.id: "storage",
    ev_disconnected.id: "storage",
}

for asset_id, expected_table in expected_tables.items():
    mapping = conversion.element_mappings[asset_id]

    assert mapping.table == expected_table
    assert mapping.index == conversion.element_indices[asset_id]

# ============================================================================
# Final Result
# ============================================================================


# ---------------------------------------------------------------------------
# Reference Source Boundary
# ---------------------------------------------------------------------------

print("\nVerified Reference Source conversion boundary:")

print(
    "  GridStudio ReferenceSource:"
    f" bus_id={reference_source.bus_id},"
    f" V={reference_source.voltage_magnitude_pu} pu,"
    f" angle={reference_source.voltage_angle_deg} deg"
)

print(
    "  Pandapower ext_grid:"
    f" bus={int(pp_reference_source['bus'])},"
    f" V={pp_reference_source['vm_pu']} pu,"
    f" angle={pp_reference_source['va_degree']} deg"
)

# ---------------------------------------------------------------------------
# Load Boundary
# ---------------------------------------------------------------------------


print("\nVerified Load conversion boundary:")

print(
    "  GridStudio Load:"
    f" P={load.active_power_mw} MW,"
    f" Q={load.reactive_power_mvar} MVAr,"
    f" scaling={load.scaling}"
)

print(
    "  Pandapower Load:"
    f" P={pp_load['p_mw']} MW,"
    f" Q={pp_load['q_mvar']} MVAr,"
    f" scaling={pp_load['scaling']}"
)

print(
    "  Effective Demand:"
    f" P={effective_pp_load_p_mw} MW,"
    f" Q={effective_pp_load_q_mvar} MVAr"
)


# ---------------------------------------------------------------------------
# Static Generator Boundary
# ---------------------------------------------------------------------------


print("\nVerified Static Generator conversion boundary:")

print(
    "  GridStudio Generator:"
    f" P={generator.active_power_mw} MW,"
    f" Q={generator.reactive_power_mvar} MVAr,"
    f" scaling={generator.scaling}"
)

print(
    "  Pandapower sgen:"
    f" P={pp_generator['p_mw']} MW,"
    f" Q={pp_generator['q_mvar']} MVAr,"
    f" scaling={pp_generator['scaling']}"
)

print(
    "  Effective Generation:"
    f" P={effective_pp_generator_p_mw} MW,"
    f" Q={effective_pp_generator_q_mvar} MVAr"
)


# ---------------------------------------------------------------------------
# Voltage Setpoint Without Voltage Control
# ---------------------------------------------------------------------------


print(
    "\nVerified voltage-setpoint-without-control boundary:"
)

print(
    "  GridStudio Voltage Generator 1:"
    f" voltage_control_enabled="
    f"{voltage_generator_1.voltage_control_enabled},"
    f" Vset={voltage_generator_1.voltage_setpoint_pu} pu"
)

print(
    "  Classification:"
    f" is_voltage_controlled="
    f"{voltage_generator_1.is_voltage_controlled}"
)

print(
    "  Pandapower representation: sgen"
)


# ---------------------------------------------------------------------------
# Voltage-Controlled Generator Boundary
# ---------------------------------------------------------------------------


print(
    "\nVerified Voltage-Controlled Generator "
    "conversion boundary:"
)

print(
    "  GridStudio Voltage Generator 2:"
    f" P={voltage_generator_2.active_power_mw} MW,"
    f" V={voltage_generator_2.voltage_setpoint_pu} pu,"
    f" voltage_control_enabled="
    f"{voltage_generator_2.voltage_control_enabled}"
)

print(
    "  Pandapower gen:"
    f" P={pp_voltage_generator_2['p_mw']} MW,"
    f" V={pp_voltage_generator_2['vm_pu']} pu"
)

print(
    "  Reactive limits:"
    f" Qmin={pp_voltage_generator_2['min_q_mvar']} MVAr,"
    f" Qmax={pp_voltage_generator_2['max_q_mvar']} MVAr"
)

# ---------------------------------------------------------------------------
# Solar Boundary
# ---------------------------------------------------------------------------

print("\nVerified Static/PQ Solar conversion boundary:")
print(
    "  GridStudio Solar PQ:"
    f" P={solar_pq.active_power_mw} MW,"
    f" Q={solar_pq.reactive_power_mvar} MVAr,"
    f" scaling={solar_pq.scaling},"
    f" DC={solar_pq.dc_capacity_mw} MW,"
    f" AC={solar_pq.inverter_rating_mva} MVA"
)
print(
    "  Pandapower sgen:"
    f" P={pp_solar_pq['p_mw']} MW,"
    f" Q={pp_solar_pq['q_mvar']} MVAr,"
    f" scaling={pp_solar_pq['scaling']}"
)
print(
    "  Effective Generation:"
    f" P={effective_pp_solar_p_mw} MW,"
    f" Q={effective_pp_solar_q_mvar} MVAr"
)
print(
    "  PV availability:"
    f" available={solar_pq.available_generation_mw} MW,"
    f" curtailed={solar_pq.curtailed_power_mw} MW"
)

print("\nVerified Voltage-Controlled Solar conversion boundary:")
print(
    "  GridStudio Solar:"
    f" P={solar_voltage_controlled.active_power_mw} MW,"
    f" V={solar_voltage_controlled.voltage_setpoint_pu} pu,"
    f" voltage_control_enabled={solar_voltage_controlled.voltage_control_enabled}"
)
print(
    "  Pandapower gen:"
    f" P={pp_solar_voltage['p_mw']} MW,"
    f" V={pp_solar_voltage['vm_pu']} pu"
)
print(
    "  Reactive limits:"
    f" Qmin={pp_solar_voltage['min_q_mvar']} MVAr,"
    f" Qmax={pp_solar_voltage['max_q_mvar']} MVAr"
)



# ---------------------------------------------------------------------------
# Wind Boundary
# ---------------------------------------------------------------------------

print("\nVerified Static/PQ Wind conversion boundary:")
print(
    "  GridStudio Wind PQ:"
    f" P={wind_pq.active_power_mw} MW,"
    f" Q={wind_pq.reactive_power_mvar} MVAr,"
    f" scaling={wind_pq.scaling},"
    f" rated P={wind_pq.rated_active_power_mw} MW,"
    f" rated S={wind_pq.rated_power_mva} MVA"
)
print(
    "  Pandapower sgen:"
    f" P={pp_wind_pq['p_mw']} MW,"
    f" Q={pp_wind_pq['q_mvar']} MVAr,"
    f" scaling={pp_wind_pq['scaling']}"
)
print(
    "  Effective Generation:"
    f" P={effective_pp_wind_p_mw} MW,"
    f" Q={effective_pp_wind_q_mvar} MVAr"
)
print(
    "  Wind availability:"
    f" available={wind_pq.available_generation_mw} MW,"
    f" curtailed={wind_pq.curtailed_power_mw} MW,"
    f" fraction={wind_pq.curtailment_fraction}"
)

print("\nVerified Voltage-Controlled Wind conversion boundary:")
print(
    "  GridStudio Wind:"
    f" P={wind_voltage_controlled.active_power_mw} MW,"
    f" V={wind_voltage_controlled.voltage_setpoint_pu} pu,"
    f" voltage_control_enabled="
    f"{wind_voltage_controlled.voltage_control_enabled}"
)
print(
    "  Pandapower gen:"
    f" P={pp_wind_voltage['p_mw']} MW,"
    f" V={pp_wind_voltage['vm_pu']} pu"
)
print(
    "  Reactive limits:"
    f" Qmin={pp_wind_voltage['min_q_mvar']} MVAr,"
    f" Qmax={pp_wind_voltage['max_q_mvar']} MVAr"
)

# ---------------------------------------------------------------------------
# Battery Boundary
# ---------------------------------------------------------------------------

print("\nVerified Battery Discharging conversion boundary:")

print(
    "  GridStudio Battery:"
    f" P={battery_discharging.active_power_mw} MW,"
    f" Q={battery_discharging.reactive_power_mvar} MVAr,"
    f" scaling={battery_discharging.scaling},"
    f" SOC={battery_discharging.state_of_charge}"
)

print(
    "  Pandapower storage:"
    f" P={pp_battery_discharging['p_mw']} MW,"
    f" Q={pp_battery_discharging['q_mvar']} MVAr,"
    f" scaling={pp_battery_discharging['scaling']},"
    f" SOC={pp_battery_discharging['soc_percent']}%"
)

print("\nVerified Battery Charging conversion boundary:")

print(
    "  GridStudio Battery:"
    f" P={battery_charging.active_power_mw} MW,"
    f" Q={battery_charging.reactive_power_mvar} MVAr,"
    f" scaling={battery_charging.scaling},"
    f" SOC={battery_charging.state_of_charge}"
)

print(
    "  Pandapower storage:"
    f" P={pp_battery_charging['p_mw']} MW,"
    f" Q={pp_battery_charging['q_mvar']} MVAr,"
    f" scaling={pp_battery_charging['scaling']},"
    f" SOC={pp_battery_charging['soc_percent']}%"
)

print("\nVerified Battery Idle VAR conversion boundary:")

print(
    "  GridStudio Battery:"
    f" P={battery_idle_var.active_power_mw} MW,"
    f" Q={battery_idle_var.reactive_power_mvar} MVAr,"
    f" SOC={battery_idle_var.state_of_charge}"
)

print(
    "  Pandapower storage:"
    f" P={pp_battery_idle_var['p_mw']} MW,"
    f" Q={pp_battery_idle_var['q_mvar']} MVAr,"
    f" SOC={pp_battery_idle_var['soc_percent']}%"
)

# ---------------------------------------------------------------------------
# Capacitor-Bank Boundary
# ---------------------------------------------------------------------------


print("\nVerified Capacitor-Bank conversion boundary:")

print(
    "  GridStudio Capacitor Bank:"
    f" Qrated={capacitor_bank.reactive_power_mvar} MVAr,"
    f" Q/step="
    f"{capacitor_bank.reactive_power_per_step_mvar} MVAr,"
    f" steps={capacitor_bank.active_steps}/"
    f"{capacitor_bank.step_count},"
    f" scaling={capacitor_bank.scaling}"
)

print(
    "  GridStudio configured Q:"
    f" {capacitor_bank.configured_reactive_power_mvar} MVAr"
)

print(
    "  Pandapower shunt:"
    f" q_mvar={pp_capacitor['q_mvar']} MVAr/step,"
    f" step={int(pp_capacitor['step'])}"
)

print(
    "  Pandapower effective Q:"
    f" {effective_pp_capacitor_q_mvar} MVAr"
)


# ---------------------------------------------------------------------------
# Shunt-Reactor Boundary
# ---------------------------------------------------------------------------


print("\nVerified Shunt-Reactor conversion boundary:")

print(
    "  GridStudio Shunt Reactor:"
    f" Qrated={shunt_reactor.reactive_power_mvar} MVAr,"
    f" Q/step="
    f"{shunt_reactor.reactive_power_per_step_mvar} MVAr,"
    f" steps={shunt_reactor.active_steps}/"
    f"{shunt_reactor.step_count},"
    f" scaling={shunt_reactor.scaling}"
)

print(
    "  GridStudio configured Q:"
    f" {shunt_reactor.configured_reactive_power_mvar} MVAr"
)

print(
    "  Pandapower shunt:"
    f" q_mvar={pp_reactor['q_mvar']} MVAr/step,"
    f" step={int(pp_reactor['step'])}"
)

print(
    "  Pandapower effective Q:"
    f" {effective_pp_reactor_q_mvar} MVAr"
)


# ---------------------------------------------------------------------------
# Transformer Boundary
# ---------------------------------------------------------------------------

print("\nVerified Fixed Transformer conversion boundary:")
print(
    "  GridStudio:"
    f" S={fixed_transformer.rated_power_mva} MVA,"
    f" V={fixed_transformer.high_voltage_kv}/"
    f"{fixed_transformer.low_voltage_kv} kV,"
    f" Z={fixed_transformer.impedance_percent}%,"
    f" R={fixed_transformer.resistance_percent}%"
)
print(
    "  Pandapower trafo:"
    f" S={pp_fixed_transformer['sn_mva']} MVA,"
    f" V={pp_fixed_transformer['vn_hv_kv']}/"
    f"{pp_fixed_transformer['vn_lv_kv']} kV,"
    f" vk={pp_fixed_transformer['vk_percent']}%,"
    f" vkr={pp_fixed_transformer['vkr_percent']}%"
)

print("\nVerified Tapped Transformer conversion boundary:")
print(
    "  GridStudio:"
    f" tap={tapped_transformer.tap_position},"
    f" limits=[{tapped_transformer.minimum_tap_position},"
    f" {tapped_transformer.maximum_tap_position}],"
    f" step={tapped_transformer.tap_step_percent}%,"
    f" HV-side={tapped_transformer.tap_on_high_voltage_side}"
)
print(
    "  Pandapower trafo:"
    f" tap_side={pp_tapped_transformer['tap_side']},"
    f" tap_neutral={int(pp_tapped_transformer['tap_neutral'])},"
    f" tap_pos={int(pp_tapped_transformer['tap_pos'])},"
    f" tap_min={int(pp_tapped_transformer['tap_min'])},"
    f" tap_max={int(pp_tapped_transformer['tap_max'])},"
    f" tap_step_percent={pp_tapped_transformer['tap_step_percent']}"
)


# ---------------------------------------------------------------------------
# Switch Boundary
# ---------------------------------------------------------------------------

print("\nVerified Switch conversion boundary:")

print(
    "  Switch Closed:"
    f" configured_closed={closed_switch.is_closed},"
    f" operational={closed_switch.is_operational},"
    f" pandapower_closed={bool(pp_closed_switch['closed'])},"
    f" in_ka={pp_closed_switch['in_ka']}"
)

print(
    "  Switch Open:"
    f" configured_closed={open_switch.is_closed},"
    f" operational={open_switch.is_operational},"
    f" pandapower_closed={bool(pp_open_switch['closed'])},"
    f" in_ka={pp_open_switch['in_ka']}"
)

print(
    "  Switch Disabled Closed:"
    f" configured_closed={disabled_closed_switch.is_closed},"
    f" operational={disabled_closed_switch.is_operational},"
    f" pandapower_closed="
    f"{bool(pp_disabled_closed_switch['closed'])},"
    f" in_ka={pp_disabled_closed_switch['in_ka']}"
)


# ---------------------------------------------------------------------------
# Classification Summary
# ---------------------------------------------------------------------------


print(
    "\nElement classification verified:"
    "\n  ReferenceSource -> pandapower ext_grid"
    "\n  Generator 1 -> pandapower sgen"
    "\n  Voltage Generator 1 -> pandapower sgen"
    "\n  Voltage Generator 2 -> pandapower gen"

    "\n  Solar PQ 1 -> pandapower sgen"
    "\n  Solar Voltage Controlled 1 -> pandapower gen"

    "\n  Wind PQ 1 -> pandapower sgen"
    "\n  Wind Voltage Controlled 1 -> pandapower gen"

    "\n  Capacitor Bank 2 -> pandapower shunt"

    "\n  Shunt Reactor 1 -> pandapower shunt"

    "\n  Transformer Fixed 33/11 kV -> pandapower trafo"
    "\n  Transformer Tapped 33/11 kV -> pandapower trafo"

    "\n  Switch Closed -> pandapower switch (closed)"
    "\n  Switch Open -> pandapower switch (open)"
    "\n  Switch Disabled Closed -> pandapower switch (open)"

    "\n  Battery Discharging -> pandapower storage"
    "\n  Battery Charging -> pandapower storage"
    "\n  Battery Idle VAR -> pandapower storage"
    
    "\n  EV Charging -> pandapower storage"
    "\n  EV V2G -> pandapower storage"
    "\n  EV Disconnected -> pandapower storage (out of service)"
)

print("\nVerified element-table mappings:")

for name, asset in (
    ("Line", line),
    ("Load", load),
    ("Generator", generator),
    ("Voltage Generator", voltage_generator_2),
    ("Solar PQ", solar_pq),
    ("Solar VC", solar_voltage_controlled),
    ("Wind PQ", wind_pq),
    ("Wind VC", wind_voltage_controlled),
    ("Battery Discharging", battery_discharging),
    ("Battery Charging", battery_charging),
    ("Battery Idle VAR", battery_idle_var),
    ("EV Charging", ev_charging),
    ("EV V2G", ev_v2g),
    ("EV Disconnected", ev_disconnected),
    ("Capacitor Bank", capacitor_bank),
    ("Transformer", fixed_transformer),
    ("Switch", closed_switch),
):
    mapping = conversion.element_mappings[asset.id]

    print(
        f"  {name:<18}"
        f" -> "
        f"{mapping.table}[{mapping.index}]"
    )

print(
    "\nSUCCESS: GridStudio Bus + Reference Source + Line + Load + "
    "Static Generator + Voltage-Controlled Generator + "
    "Solar + Wind + Battery + EV + Shunt + Transformer + Switch "
    "conversion passed all smoke-test assertions."
)
