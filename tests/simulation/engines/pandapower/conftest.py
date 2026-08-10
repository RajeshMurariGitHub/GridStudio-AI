"""
GridStudio AI

Module:
    conftest.py

Description:
    Shared pytest fixtures for pandapower converter tests.

    Fixtures construct reusable GridStudio networks and converter
    instances used across all converter regression tests.

    No assertions belong here.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

import pytest

from src.simulation.engines.pandapower import (
    PandapowerConverter,
)

from tests.simulation.engines.pandapower.builders import (
    build_network,
)


# ============================================================================
# Converter
# ============================================================================


@pytest.fixture(scope="session")
def converter() -> PandapowerConverter:
    """
    Shared pandapower converter.
    """
    return PandapowerConverter()


# ============================================================================
# Network
# ============================================================================


@pytest.fixture
def network():
    """
    Fresh GridStudio network.

    Every test receives an independent network instance.
    """
    return build_network()


# ============================================================================
# Conversion
# ============================================================================


@pytest.fixture
def conversion(
    converter,
    network,
):
    """
    Convert the network using the PandapowerConverter.
    """
    return converter.convert(network)