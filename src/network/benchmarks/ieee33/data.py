"""
GridStudio AI

Module:
    data.py

Description:
    Canonical IEEE 33-Bus Distribution Test Feeder benchmark data.

Reference:
    Baran, M. E., and Wu, F. F.
    "Network Reconfiguration in Distribution Systems for Loss Reduction
    and Load Balancing."
    IEEE Transactions on Power Delivery,
    Vol. 4, No. 2, April 1989.

Notes
-----
Loads are stored exactly as published
(kW / kVAr).

Branch impedances are stored in Ohms.

Conversion to per-unit is performed by
IEEE33BusBuilder.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from src.core.enums.electrical import BusType

from src.network.benchmarks.common.types import (
    BranchData,
    BusData,
    GeneratorData,
    LoadData,
)

from src.network.benchmarks.common.types import (
    BenchmarkDataset,
)

from .metadata import (
    IEEE33_METADATA,
)

#
# ---------------------------------------------------------
# Bus Data
# ---------------------------------------------------------
#

BUS_DATA = [
    BusData(
        bus_number=i,
        bus_type=BusType.SLACK if i == 1 else BusType.PQ,
        base_voltage_kv=IEEE33_METADATA.base_voltage_kv,
        voltage_magnitude_pu=1.0,
        voltage_angle_deg=0.0,
    )
    for i in range(1, 34)
]

#
# ---------------------------------------------------------
# Branch Data
# Resistance (Ohm)
# Reactance (Ohm)
# ---------------------------------------------------------
#

BRANCH_DATA = [
    BranchData(
        branch_number=1,
        from_bus_number=1,
        to_bus_number=2,
        resistance_ohm=0.0922,
        reactance_ohm=0.0477,
    ),
    BranchData(
        branch_number=2,
        from_bus_number=2,
        to_bus_number=3,
        resistance_ohm=0.4930,
        reactance_ohm=0.2511,
    ),
    BranchData(
        branch_number=3,
        from_bus_number=3,
        to_bus_number=4,
        resistance_ohm=0.3660,
        reactance_ohm=0.1864,
    ),
    BranchData(
        branch_number=4,
        from_bus_number=4,
        to_bus_number=5,
        resistance_ohm=0.3811,
        reactance_ohm=0.1941,
    ),
    BranchData(
        branch_number=5,
        from_bus_number=5,
        to_bus_number=6,
        resistance_ohm=0.8190,
        reactance_ohm=0.7070,
    ),
    BranchData(
        branch_number=6,
        from_bus_number=6,
        to_bus_number=7,
        resistance_ohm=0.1872,
        reactance_ohm=0.6188,
    ),
    BranchData(
        branch_number=7,
        from_bus_number=7,
        to_bus_number=8,
        resistance_ohm=1.7114,
        reactance_ohm=1.2351,
    ),
    BranchData(
        branch_number=8,
        from_bus_number=8,
        to_bus_number=9,
        resistance_ohm=1.0300,
        reactance_ohm=0.7400,
    ),
    BranchData(
        branch_number=9,
        from_bus_number=9,
        to_bus_number=10,
        resistance_ohm=1.0040,
        reactance_ohm=0.7400,
    ),
    BranchData(
        branch_number=10,
        from_bus_number=10,
        to_bus_number=11,
        resistance_ohm=0.1966,
        reactance_ohm=0.0650,
    ),
    BranchData(
        branch_number=11,
        from_bus_number=11,
        to_bus_number=12,
        resistance_ohm=0.3744,
        reactance_ohm=0.1238,
    ),
    BranchData(
        branch_number=12,
        from_bus_number=12,
        to_bus_number=13,
        resistance_ohm=1.4680,
        reactance_ohm=1.1550,
    ),
    BranchData(
        branch_number=13,
        from_bus_number=13,
        to_bus_number=14,
        resistance_ohm=0.5416,
        reactance_ohm=0.7129,
    ),
    BranchData(
        branch_number=14,
        from_bus_number=14,
        to_bus_number=15,
        resistance_ohm=0.5910,
        reactance_ohm=0.5260,
    ),
    BranchData(
        branch_number=15,
        from_bus_number=15,
        to_bus_number=16,
        resistance_ohm=0.7463,
        reactance_ohm=0.5450,
    ),
    BranchData(
        branch_number=16,
        from_bus_number=16,
        to_bus_number=17,
        resistance_ohm=1.2890,
        reactance_ohm=1.7210,
    ),
    BranchData(
        branch_number=17,
        from_bus_number=17,
        to_bus_number=18,
        resistance_ohm=0.7320,
        reactance_ohm=0.5740,
    ),
    BranchData(
        branch_number=18,
        from_bus_number=2,
        to_bus_number=19,
        resistance_ohm=0.1640,
        reactance_ohm=0.1565,
    ),
    BranchData(
        branch_number=19,
        from_bus_number=19,
        to_bus_number=20,
        resistance_ohm=1.5042,
        reactance_ohm=1.3554,
    ),
    BranchData(
        branch_number=20,
        from_bus_number=20,
        to_bus_number=21,
        resistance_ohm=0.4095,
        reactance_ohm=0.4784,
    ),
    BranchData(
        branch_number=21,
        from_bus_number=21,
        to_bus_number=22,
        resistance_ohm=0.7089,
        reactance_ohm=0.9373,
    ),
    BranchData(
        branch_number=22,
        from_bus_number=3,
        to_bus_number=23,
        resistance_ohm=0.4512,
        reactance_ohm=0.3083,
    ),
    BranchData(
        branch_number=23,
        from_bus_number=23,
        to_bus_number=24,
        resistance_ohm=0.8980,
        reactance_ohm=0.7091,
    ),
    BranchData(
        branch_number=24,
        from_bus_number=24,
        to_bus_number=25,
        resistance_ohm=0.8960,
        reactance_ohm=0.7011,
    ),
    BranchData(
        branch_number=25,
        from_bus_number=6,
        to_bus_number=26,
        resistance_ohm=0.2030,
        reactance_ohm=0.1034,
    ),
    BranchData(
        branch_number=26,
        from_bus_number=26,
        to_bus_number=27,
        resistance_ohm=0.2842,
        reactance_ohm=0.1477,
    ),
    BranchData(
        branch_number=27,
        from_bus_number=27,
        to_bus_number=28,
        resistance_ohm=1.0590,
        reactance_ohm=0.9337,
    ),
    BranchData(
        branch_number=28,
        from_bus_number=28,
        to_bus_number=29,
        resistance_ohm=0.8042,
        reactance_ohm=0.7006,
    ),
    BranchData(
        branch_number=29,
        from_bus_number=29,
        to_bus_number=30,
        resistance_ohm=0.5075,
        reactance_ohm=0.2585,
    ),
    BranchData(
        branch_number=30,
        from_bus_number=30,
        to_bus_number=31,
        resistance_ohm=0.9744,
        reactance_ohm=0.9630,
    ),
    BranchData(
        branch_number=31,
        from_bus_number=31,
        to_bus_number=32,
        resistance_ohm=0.3105,
        reactance_ohm=0.3619,
    ),
    BranchData(
        branch_number=32,
        from_bus_number=32,
        to_bus_number=33,
        resistance_ohm=0.3410,
        reactance_ohm=0.5302,
    ),
]

#
# ---------------------------------------------------------
# Load Data
# Active Power : kW
# Reactive Power : kVAr
# ---------------------------------------------------------
#

LOAD_DATA = [
    LoadData(load_number=1, bus_number=2, active_power_kw=100, reactive_power_kvar=60),
    LoadData(load_number=2, bus_number=3, active_power_kw=90, reactive_power_kvar=40),
    LoadData(load_number=3, bus_number=4, active_power_kw=120, reactive_power_kvar=80),
    LoadData(load_number=4, bus_number=5, active_power_kw=60, reactive_power_kvar=30),
    LoadData(load_number=5, bus_number=6, active_power_kw=60, reactive_power_kvar=20),
    LoadData(load_number=6, bus_number=7, active_power_kw=200, reactive_power_kvar=100),
    LoadData(load_number=7, bus_number=8, active_power_kw=200, reactive_power_kvar=100),
    LoadData(load_number=8, bus_number=9, active_power_kw=60, reactive_power_kvar=20),
    LoadData(load_number=9, bus_number=10, active_power_kw=60, reactive_power_kvar=20),
    LoadData(load_number=10, bus_number=11, active_power_kw=45, reactive_power_kvar=30),
    LoadData(load_number=11, bus_number=12, active_power_kw=60, reactive_power_kvar=35),
    LoadData(load_number=12, bus_number=13, active_power_kw=60, reactive_power_kvar=35),
    LoadData(load_number=13, bus_number=14, active_power_kw=120, reactive_power_kvar=80),
    LoadData(load_number=14, bus_number=15, active_power_kw=60, reactive_power_kvar=10),
    LoadData(load_number=15, bus_number=16, active_power_kw=60, reactive_power_kvar=20),
    LoadData(load_number=16, bus_number=17, active_power_kw=60, reactive_power_kvar=20),
    LoadData(load_number=17, bus_number=18, active_power_kw=90, reactive_power_kvar=40),
    LoadData(load_number=18, bus_number=19, active_power_kw=90, reactive_power_kvar=40),
    LoadData(load_number=19, bus_number=20, active_power_kw=90, reactive_power_kvar=40),
    LoadData(load_number=20, bus_number=21, active_power_kw=90, reactive_power_kvar=40),
    LoadData(load_number=21, bus_number=22, active_power_kw=90, reactive_power_kvar=40),
    LoadData(load_number=22, bus_number=23, active_power_kw=90, reactive_power_kvar=50),
    LoadData(load_number=23, bus_number=24, active_power_kw=420, reactive_power_kvar=200),
    LoadData(load_number=24, bus_number=25, active_power_kw=420, reactive_power_kvar=200),
    LoadData(load_number=25, bus_number=26, active_power_kw=60, reactive_power_kvar=25),
    LoadData(load_number=26, bus_number=27, active_power_kw=60, reactive_power_kvar=25),
    LoadData(load_number=27, bus_number=28, active_power_kw=60, reactive_power_kvar=20),
    LoadData(load_number=28, bus_number=29, active_power_kw=120, reactive_power_kvar=70),
    LoadData(load_number=29, bus_number=30, active_power_kw=200, reactive_power_kvar=600),
    LoadData(load_number=30, bus_number=31, active_power_kw=150, reactive_power_kvar=70),
    LoadData(load_number=31, bus_number=32, active_power_kw=210, reactive_power_kvar=100),
    LoadData(load_number=32, bus_number=33, active_power_kw=60, reactive_power_kvar=40),
]

#
# ---------------------------------------------------------
# Generator Data
# ---------------------------------------------------------
#

GENERATOR_DATA = [
    GeneratorData(
        generator_number=1,
        bus_number=1,
        active_power_mw=0.0,
        reactive_power_mvar=0.0,
        voltage_setpoint_pu=1.0,
        rated_power_mva=IEEE33_METADATA.base_power_mva,
    ),
]


#
# ---------------------------------------------------------
# Benchmark Validation
# ---------------------------------------------------------
#

EXPECTED_COUNTS = {
    "buses": 33,
    "branches": 32,
    "loads": 32,
    "generators": 1,
}

EXPECTED_TOTALS = {
    "active_load_mw": 3.715,
    "reactive_load_mvar": 2.300,
}

#
# ---------------------------------------------------------
# Expected Solver Results
#
# Filled after validating the GridStudio
# Newton-Raphson implementation.
# ---------------------------------------------------------
#

EXPECTED_RESULTS = {
    "minimum_voltage_pu": None,
    "maximum_voltage_pu": None,
    "active_loss_mw": None,
    "reactive_loss_mvar": None,
}


#
# IEEE 33 benchmark dataset.
#

IEEE33_DATASET = BenchmarkDataset(
    buses=tuple(BUS_DATA),
    branches=tuple(BRANCH_DATA),
    loads=tuple(LOAD_DATA),
    generators=tuple(GENERATOR_DATA),
)


#
# ---------------------------------------------------------
# Dataset Validation
# ---------------------------------------------------------
#


def validate_dataset() -> None:
    """
    Validate the IEEE 33-Bus benchmark dataset.
    """

    #
    # Bus count
    #

    assert len(BUS_DATA) == EXPECTED_COUNTS["buses"]

    #
    # Branch count
    #

    assert len(BRANCH_DATA) == EXPECTED_COUNTS["branches"]

    #
    # Load count
    #

    assert len(LOAD_DATA) == EXPECTED_COUNTS["loads"]

    #
    # Generator count
    #

    assert len(GENERATOR_DATA) == EXPECTED_COUNTS["generators"]

    #
    # Bus numbers unique
    #

    bus_numbers = [bus.bus_number for bus in BUS_DATA]

    assert len(bus_numbers) == len(set(bus_numbers))

    #
    # Branch numbers unique
    #

    branch_numbers = [branch.branch_number for branch in BRANCH_DATA]

    assert len(branch_numbers) == len(set(branch_numbers))

    #
    # Branch endpoints exist
    #

    valid_buses = set(bus_numbers)

    for branch in BRANCH_DATA:
        assert branch.from_bus_number in valid_buses

        assert branch.to_bus_number in valid_buses

    #
    # Total load
    #

    total_p = sum(load.active_power_kw for load in LOAD_DATA) / 1000.0

    total_q = sum(load.reactive_power_kvar for load in LOAD_DATA) / 1000.0

    assert abs(total_p - EXPECTED_TOTALS["active_load_mw"]) < 1e-9

    assert abs(total_q - EXPECTED_TOTALS["reactive_load_mvar"]) < 1e-9


#
# Validate immediately when imported.
#

validate_dataset()


__all__ = [
    "IEEE33_DATASET",

    "BUS_DATA",
    "BRANCH_DATA",
    "LOAD_DATA",
    "GENERATOR_DATA",

    "EXPECTED_COUNTS",
    "EXPECTED_TOTALS",
    "EXPECTED_RESULTS",

    "validate_dataset",
]
