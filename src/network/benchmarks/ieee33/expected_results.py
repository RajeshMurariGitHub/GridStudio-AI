"""
GridStudio AI

IEEE 33-Bus Benchmark Reference
===============================

Published reference data for the IEEE 33-bus radial distribution
system.

Notes
-----
This module contains ONLY immutable benchmark data.

No numerical calculations shall be performed here.

Every value should originate from the official IEEE benchmark
solution or another documented reference adopted by GridStudio.
"""

from __future__ import annotations

from typing import ClassVar

class IEEE33ExpectedResults:
    """
    Immutable IEEE 33-bus benchmark reference.
    """

    # -------------------------------------------------------------
    # Network
    # -------------------------------------------------------------

    BUS_COUNT: ClassVar[int] = 33

    BRANCH_COUNT: ClassVar[int] = 32

    BASE_POWER_MVA: ClassVar[float] = 100.0

    BASE_FREQUENCY_HZ: ClassVar[float] = 50.0

    BASE_VOLTAGE_KV: ClassVar[float] = 12.66

    # -------------------------------------------------------------
    # Solver reference
    # -------------------------------------------------------------

    MAXIMUM_ITERATIONS: ClassVar[int] = 10

    CONVERGENCE_TOLERANCE: ClassVar[float] = 1e-4

    # -------------------------------------------------------------
    # Engineering limits
    # -------------------------------------------------------------

    MINIMUM_ACCEPTABLE_VOLTAGE_PU: ClassVar[float] = 0.90

    MAXIMUM_ACCEPTABLE_VOLTAGE_PU: ClassVar[float] = 1.10

    # -------------------------------------------------------------
    # Summary statistics
    # -------------------------------------------------------------

    MINIMUM_BUS_VOLTAGE_PU: ClassVar[float] = 0.90394

    MAXIMUM_BUS_VOLTAGE_PU: ClassVar[float] = 1.00000

    AVERAGE_BUS_VOLTAGE_PU: ClassVar[float] = 0.94535

    TOTAL_ACTIVE_GENERATION_MW: ClassVar[float] = 3.9258466595

    TOTAL_REACTIVE_GENERATION_MVAR: ClassVar[float] = 2.4431521

    TOTAL_ACTIVE_LOAD_MW: ClassVar[float] = 3.7150

    TOTAL_REACTIVE_LOAD_MVAR: ClassVar[float] = 2.3000

    TOTAL_ACTIVE_LOSS_MW: ClassVar[float] = 0.2108466

    TOTAL_REACTIVE_LOSS_MVAR: ClassVar[float] = 0.1431521

    SYSTEM_POWER_FACTOR: ClassVar[float] = 0.8490175 #(Lagging)

    # -------------------------------------------------------------
    # Bus voltage magnitudes (per unit)
    # -------------------------------------------------------------

    VOLTAGE_MAGNITUDES: ClassVar[dict[int, float]] = {
        1: 1.00000,
        2: 0.99701,
        3: 0.98288,
        4: 0.97537,
        5: 0.96795,
        6: 0.94947,
        7: 0.94595,
        8: 0.93229,
        9: 0.92596,
        10:0.92025,
        11:0.91939,
        12:0.91787,
        13:0.91170,
        14:0.90941,
        15:0.90798,
        16:0.90660,
        17:0.90455,
        18:0.90394,
        19:0.99649,
        20:0.99291,
        21:0.99220,
        22:0.99157,
        23:0.97930,
        24:0.97263,
        25:0.96930,
        26:0.94754,
        27:0.94496,
        28:0.93351,
        29:0.92529,
        30:0.92174,
        31:0.91757,
        32:0.91666,
        33:0.91638,
    }

    # -------------------------------------------------------------
    # Bus voltage angles (degrees)
    # -------------------------------------------------------------

    VOLTAGE_ANGLES: ClassVar[dict[int, float]] = {
        1:  0.0000,
        2:  0.0136234963,
        3:  0.0959,
        4:  0.1620,
        5:  0.2292,
        6:  0.1351,
        7: -0.0966,
        8: -0.2500,
        9: -0.3245,
        10:-0.3932,
        11:-0.3858,
        12:-0.3741,
        13:-0.4672,
        14:-0.5474,
        15:-0.5859,
        16:-0.6096,
        17:-0.6884,
        18:-0.6982,
        19: 0.0028,
        20:-0.0642,
        21:-0.0835,
        22:-0.1039,
        23: 0.0649,
        24:-0.0238,
        25:-0.0675,
        26: 0.1745,
        27: 0.2297,
        28: 0.3126,
        29: 0.3906,
        30: 0.4959,
        31: 0.4115,
        32: 0.3884,
        33: 0.3807,
    }

    # -------------------------------------------------------------
    # Branch Power Flows
    # -------------------------------------------------------------

    BRANCH_POWER_FLOWS = {
        (1, 2):   {"p_from_mw":3.9258,	"q_from_mvar":2.4432,	"p_to_mw":-3.9135,	"q_to_mvar":-2.4368,},
        (2, 3):   {"p_from_mw":3.4524,	"q_from_mvar":2.2157,	"p_to_mw":-3.4003,	"q_to_mvar":-2.1892,},
        (3, 4):   {"p_from_mw":2.3707,	"q_from_mvar":1.6919,	"p_to_mw":-2.3507,	"q_to_mvar":-1.6817,},
        (4, 5):   {"p_from_mw":2.2307,	"q_from_mvar":1.6017,	"p_to_mw":-2.2118,	"q_to_mvar":-1.5921,},
        (5, 6):   {"p_from_mw":2.1518,	"q_from_mvar":1.5621,	"p_to_mw":-2.1133,	"q_to_mvar":-1.5288,},
        (6, 7):   {"p_from_mw":1.1025,	"q_from_mvar":0.5352,	"p_to_mw":-1.1005,	"q_to_mvar":-0.5287,},
        (7, 8):   {"p_from_mw":0.9005,	"q_from_mvar":0.4287,	"p_to_mw":-0.8886,	"q_to_mvar":-0.4202,},
        (8, 9):   {"p_from_mw":0.6886,	"q_from_mvar":0.3202,	"p_to_mw":-0.6844,	"q_to_mvar":-0.3171,},
        (9, 10):  {"p_from_mw":0.6244,	"q_from_mvar":0.2971,	"p_to_mw":-0.6209,	"q_to_mvar":-0.2945,},
        (10, 11): {"p_from_mw":0.5609,	"q_from_mvar":0.2745,	"p_to_mw":-0.5603,	"q_to_mvar":-0.2743,},
        (11, 12): {"p_from_mw":0.5153,	"q_from_mvar":0.2443,	"p_to_mw":-0.5144,	"q_to_mvar":-0.2440,},
        (12, 13): {"p_from_mw":0.4544,	"q_from_mvar":0.2090,	"p_to_mw":-0.4517,	"q_to_mvar":-0.2069,},
        (13, 14): {"p_from_mw":0.3917,	"q_from_mvar":0.1719,	"p_to_mw":-0.3910,	"q_to_mvar":-0.1709,},
        (14, 15): {"p_from_mw":0.2710,	"q_from_mvar":0.0909,	"p_to_mw":-0.2706,	"q_to_mvar":-0.0906,},
        (15, 16): {"p_from_mw":0.2106,	"q_from_mvar":0.0806,	"p_to_mw":-0.2103,	"q_to_mvar":-0.0804,},
        (16, 17): {"p_from_mw":0.1503,	"q_from_mvar":0.0604,	"p_to_mw":-0.1501,	"q_to_mvar":-0.0600,},
        (17, 18): {"p_from_mw":0.0901,	"q_from_mvar":0.0400,	"p_to_mw":-0.0900,	"q_to_mvar":-0.0400,},
        (2, 19):  {"p_from_mw":0.3611,	"q_from_mvar":0.1611,	"p_to_mw":-0.3610,	"q_to_mvar":-0.1609,},
        (19, 20): {"p_from_mw":0.2710,	"q_from_mvar":0.1209,	"p_to_mw":-0.2701,	"q_to_mvar":-0.1202,},
        (20, 21): {"p_from_mw":0.1801,	"q_from_mvar":0.0802,	"p_to_mw":-0.1800,	"q_to_mvar":-0.0801,},
        (21, 22): {"p_from_mw":0.0900,	"q_from_mvar":0.0401,	"p_to_mw":-0.0900,	"q_to_mvar":-0.0400,},
        (3, 23):  {"p_from_mw":0.9396,	"q_from_mvar":0.4572,	"p_to_mw":-0.9364,	"q_to_mvar":-0.4551,},
        (23, 24): {"p_from_mw":0.8464,	"q_from_mvar":0.4051,	"p_to_mw":-0.8413,	"q_to_mvar":-0.4010,},
        (24, 25): {"p_from_mw":0.4213,	"q_from_mvar":0.2010,	"p_to_mw":-0.4200,	"q_to_mvar":-0.2000,},
        (6, 26):  {"p_from_mw":0.9508,	"q_from_mvar":0.9737,	"p_to_mw":-0.9482,	"q_to_mvar":-0.9724,},
        (26, 27): {"p_from_mw":0.8882,	"q_from_mvar":0.9474,	"p_to_mw":-0.8849,	"q_to_mvar":-0.9456,},
        (27, 28): {"p_from_mw":0.8249,	"q_from_mvar":0.9206,	"p_to_mw":-0.8136,	"q_to_mvar":-0.9107,},
        (28, 29): {"p_from_mw":0.7536,	"q_from_mvar":0.8907,	"p_to_mw":-0.7457,	"q_to_mvar":-0.8838,},
        (29, 30): {"p_from_mw":0.6257,	"q_from_mvar":0.8138,	"p_to_mw":-0.6218,	"q_to_mvar":-0.8118,},
        (30, 31): {"p_from_mw":0.4218,	"q_from_mvar":0.2118,	"p_to_mw":-0.4202,	"q_to_mvar":-0.2103,},
        (31, 32): {"p_from_mw":0.2702,	"q_from_mvar":0.1403,	"p_to_mw":-0.2700,	"q_to_mvar":-0.1400,},
        (32, 33): {"p_from_mw":0.0600,	"q_from_mvar":0.0400,	"p_to_mw":-0.0600,	"q_to_mvar":-0.0400,},
}