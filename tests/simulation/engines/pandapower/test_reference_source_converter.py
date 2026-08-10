"""
GridStudio AI

Module:
    test_reference_source_converter.py

Description:
    Regression tests for GridStudio ReferenceSource ->
    pandapower ext_grid conversion.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

import pytest

from .builders import (
    build_bus_hv,
    build_reference_source,
)


# ============================================================================
# Helpers
# ============================================================================


def _build_reference_network(network):
    """
    Build the minimal network required for an ext_grid.
    """

    bus = build_bus_hv()

    network.add(bus)

    reference = build_reference_source(bus)

    return bus, reference


# ============================================================================
# ext_grid Creation
# ============================================================================


def test_reference_source_conversion(
    converter,
    network,
):
    """
    A GridStudio ReferenceSource shall be converted to one
    pandapower ext_grid.
    """

    bus, reference = _build_reference_network(network)

    conversion = converter.convert(
        network,
        reference_sources=[reference],
    )

    pp_net = conversion.network

    assert len(pp_net.ext_grid) == 1

    row = pp_net.ext_grid.loc[0]

    assert row["bus"] == conversion.bus_indices[bus.id]

    assert row["vm_pu"] == reference.voltage_magnitude_pu

    assert row["va_degree"] == reference.voltage_angle_deg

    assert bool(row["in_service"])


# ============================================================================
# Mapping
# ============================================================================


def test_reference_source_mapping(
    converter,
    network,
):
    """
    ReferenceSource shall participate in the generic element
    mapping.
    """

    bus, reference = _build_reference_network(
        network,
    )

    conversion = converter.convert(
        network,
        reference_sources=(reference,),
    )

    pp_net = conversion.network

    assert len(pp_net.ext_grid) == 1

    ext_grid = pp_net.ext_grid.iloc[0]

    assert ext_grid["bus"] == (
        conversion.bus_indices[bus.id]
    )

    assert ext_grid["vm_pu"] == pytest.approx(
        reference.voltage_magnitude_pu
        )

    assert ext_grid["va_degree"] == pytest.approx(
        reference.voltage_angle_deg
    )

# ============================================================================
# Empty Reference List
# ============================================================================


def test_no_reference_source(
    converter,
    network,
):
    """
    Converting without ReferenceSources shall not create an
    ext_grid.
    """

    bus = build_bus_hv()

    network.add(bus)

    conversion = converter.convert(network)

    pp_net = conversion.network

    assert len(pp_net.ext_grid) == 0