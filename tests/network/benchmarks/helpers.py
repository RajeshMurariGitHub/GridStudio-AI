"""
GridStudio AI

Module:
    helpers.py

Description:
    Common helper functions for benchmark integration tests.

    These helpers construct solver-independent simulation
    requests from benchmark networks, allowing benchmark
    tests to focus on simulation behaviour rather than
    request construction.

    All helpers operate exclusively on the public
    GridStudio API.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from src.core.enums.electrical import (
    BusType,
)

from src.domain.network.network import (
    Network,
)

from src.simulation.models.requests.power_flow_request import (
    PowerFlowRequest,
)

from src.simulation.models.requests.reference_source import (
    ReferenceSource,
)


# ============================================================================
# Slack Bus Helpers
# ============================================================================


def find_slack_bus(
    network: Network,
):
    """
    Return the unique slack bus.

    Raises
    ------
    AssertionError
        If the network does not contain exactly one slack bus.
    """

    slack_buses = [

        bus

        for bus in network.buses

        if bus.bus_type == BusType.SLACK

    ]

    assert (
        len(slack_buses) == 1
    ), (
        "Benchmark network must contain exactly "
        "one slack bus."
    )

    return slack_buses[0]


# ============================================================================
# Reference Source Helpers
# ============================================================================


def build_reference_source(
    network: Network,
) -> ReferenceSource:
    """
    Build the default electrical reference source
    for a benchmark network.
    """

    slack_bus = find_slack_bus(
        network,
    )

    return ReferenceSource(

        bus_id=slack_bus.id,

        voltage_magnitude_pu=1.0,

        voltage_angle_deg=0.0,
    )


# ============================================================================
# Request Helpers
# ============================================================================


def build_power_flow_request(
    network: Network,
) -> PowerFlowRequest:
    """
    Build a solver-independent power-flow request
    for a benchmark network.
    """

    return PowerFlowRequest(

        network=network,

        reference_sources=(

            build_reference_source(
                network,
            ),

        ),
    )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "find_slack_bus",
    "build_reference_source",
    "build_power_flow_request",
]