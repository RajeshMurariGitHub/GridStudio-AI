"""
GridStudio AI

Module:
    types.py

Description:
    Common immutable data models used by benchmark networks.

    These classes describe benchmark topology, metadata and
    expected reference results.

    They contain NO behaviour.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from src.core.enums import BusType

#
# ---------------------------------------------------------------------
# Network data
# ---------------------------------------------------------------------
#


@dataclass(frozen=True, slots=True)
class BusData:
    """
    Benchmark bus definition.

    Values are stored exactly as published by the benchmark.
    """

    bus_number: int

    bus_type: BusType

    base_voltage_kv: float

    voltage_magnitude_pu: float = 1.0

    voltage_angle_deg: float = 0.0

    name: str | None = None

    x_coordinate: float = 0.0

    y_coordinate: float = 0.0


@dataclass(frozen=True, slots=True)
class BranchData:
    """
    Benchmark branch definition.
    """

    branch_number: int

    from_bus_number: int
    to_bus_number: int

    resistance_ohm: float
    reactance_ohm: float

    charging_susceptance_siemens: float = 0.0

    thermal_limit_mva: float | None = None


@dataclass(frozen=True, slots=True)
class TransformerData:
    """
    Benchmark transformer definition.
    """

    transformer_number: int

    hv_bus_number: int
    lv_bus_number: int

    rated_power_mva: float

    hv_voltage_kv: float
    lv_voltage_kv: float

    short_circuit_voltage_percent: float

    copper_loss_kw: float

    no_load_loss_kw: float = 0.0

    tap_position: int = 0


@dataclass(frozen=True, slots=True)
class LoadData:

    load_number: int

    bus_number: int

    active_power_kw: float

    reactive_power_kvar: float


@dataclass(frozen=True, slots=True)
class GeneratorData:
    """
    Benchmark generator definition.
    """

    generator_number: int

    bus_number: int

    active_power_mw: float

    reactive_power_mvar: float = 0.0

    rated_power_mva: float | None = None

    voltage_setpoint_pu: float = 1.0

    is_slack: bool = False


@dataclass(frozen=True, slots=True)
class ShuntData:
    """
    Benchmark shunt definition.
    """

    shunt_number: int

    bus_number: int

    reactive_power_mvar: float


@dataclass(frozen=True, slots=True)
class BatteryData:
    """
    Benchmark battery definition.
    """

    battery_number: int

    bus_number: int

    rated_power_mw: float

    rated_energy_mwh: float


@dataclass(frozen=True, slots=True)
class EVData:
    """
    Benchmark EV charger definition.
    """

    charger_number: int

    bus_number: int

    rated_power_mw: float


#
# ---------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------
#


@dataclass(frozen=True, slots=True)
class BenchmarkDataset:
    """
    Complete benchmark dataset.
    """

    buses: tuple[BusData, ...]

    branches: tuple[BranchData, ...]

    transformers: tuple[TransformerData, ...] = ()

    loads: tuple[LoadData, ...] = ()

    generators: tuple[GeneratorData, ...] = ()

    shunts: tuple[ShuntData, ...] = ()

    batteries: tuple[BatteryData, ...] = ()

    ev_chargers: tuple[EVData, ...] = ()


    @property
    def bus_numbers(
        self,
    ) -> frozenset[int]:

        return frozenset(
            bus.bus_number
            for bus in self.buses
        )


    @property
    def slack_bus(
        self,
    ) -> BusData | None:

        for bus in self.buses:

            if bus.bus_type.is_slack:

                return bus

        return None

#
# ---------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------
#


@dataclass(frozen=True, slots=True)
class BenchmarkMetadata:
    """
    Benchmark identification.
    """

    name: str

    description: str

    reference: str

    version: str

    base_power_mva: float

    base_voltage_kv: float

    base_frequency_hz: float = 50.0


#
# ---------------------------------------------------------------------
# Expected results
# ---------------------------------------------------------------------
#


@dataclass(frozen=True, slots=True)
class BenchmarkExpectedResults:
    """
    Published benchmark solution.
    """

    minimum_bus_voltage_pu: float

    maximum_bus_voltage_pu: float

    average_bus_voltage_pu: float

    total_active_generation_mw: float

    total_reactive_generation_mvar: float

    total_active_load_mw: float

    total_reactive_load_mvar: float

    total_active_loss_mw: float

    total_reactive_loss_mvar: float

    system_power_factor: float

    voltage_magnitudes: Mapping[int, float]

    voltage_angles_deg: Mapping[int, float]

    branch_power_flows: Mapping[
        tuple[int, int],
        Mapping[str, float],
    ]