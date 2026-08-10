"""
GridStudio AI

Tests:
    test_network.py

Description:
    Tests the canonical physical Network registry.

    These tests verify ownership, typed lookup, duplicate protection,
    physical branch lookup, and reference integrity.
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from src.domain.bus import Bus
from src.domain.line import Line

from src.domain.network import (
    DuplicateElementError,
    ElementNotFoundError,
    InvalidElementTypeError,
    Network,
)


# ============================================================================
# Helpers
# ============================================================================


def make_bus(
    name: str,
) -> Bus:
    """
    Construct the smallest valid Bus supported by the domain model.

    IMPORTANT:
    Keep this helper aligned with the actual Bus constructor.
    """

    return Bus(
        id=uuid4(),
        name=name,
        nominal_voltage_kv=11.0,
    )


# ============================================================================
# Empty Network
# ============================================================================


def test_empty_network() -> None:
    network = Network(
        name="Test Network"
    )

    assert len(network) == 0
    assert network.bus_count == 0
    assert network.branch_count == 0


# ============================================================================
# Element Registry
# ============================================================================


def test_add_bus() -> None:
    network = Network(
        name="Test Network"
    )

    bus = make_bus("Bus 1")

    network.add(bus)

    assert len(network) == 1
    assert bus.id in network


def test_get_existing_element() -> None:
    network = Network(
        name="Test Network"
    )

    bus = make_bus("Bus 1")

    network.add(bus)

    assert network.get(bus.id) is bus


def test_get_missing_element_returns_none() -> None:
    network = Network(
        name="Test Network"
    )

    assert network.get(
        uuid4()
    ) is None


def test_require_missing_element_raises() -> None:
    network = Network(
        name="Test Network"
    )

    missing_id = uuid4()

    with pytest.raises(
        ElementNotFoundError
    ):
        network.require(
            missing_id
        )


def test_duplicate_element_id_is_rejected() -> None:
    network = Network(
        name="Test Network"
    )

    bus = make_bus("Bus 1")

    network.add(bus)

    with pytest.raises(
        DuplicateElementError
    ):
        network.add(bus)


# ============================================================================
# Typed Lookup
# ============================================================================


def test_require_as_returns_expected_type() -> None:
    network = Network(
        name="Test Network"
    )

    bus = make_bus("Bus 1")

    network.add(bus)

    result = network.require_as(
        bus.id,
        Bus,
    )

    assert result is bus


def test_require_as_rejects_wrong_type() -> None:
    network = Network(
        name="Test Network"
    )

    bus = make_bus("Bus 1")

    network.add(bus)

    with pytest.raises(
        InvalidElementTypeError
    ):
        network.require_as(
            bus.id,
            Line,
        )


# ============================================================================
# Removal
# ============================================================================


def test_remove_element() -> None:
    network = Network(
        name="Test Network"
    )

    bus = make_bus("Bus 1")

    network.add(bus)

    removed = network.remove(
        bus.id
    )

    assert removed is bus
    assert bus.id not in network


def test_remove_missing_element_raises() -> None:
    network = Network(
        name="Test Network"
    )

    with pytest.raises(
        ElementNotFoundError
    ):
        network.remove(
            uuid4()
        )


# ============================================================================
# Typed Views
# ============================================================================

    def test_buses_view_contains_only_buses() -> None:
        network = Network(
            name="Test Network"
        )

        bus_1 = make_bus("Bus 1")
        bus_2 = make_bus("Bus 2")

        network.add(bus_1)
        network.add(bus_2)

        buses = network.buses

        assert len(buses) == 2
        assert bus_1 in buses
        assert bus_2 in buses
        assert all(
            isinstance(bus, Bus)
            for bus in buses
        )

def test_bus_ids() -> None:
    network = Network(
        name="Test Network"
    )

    bus_1 = make_bus("Bus 1")
    bus_2 = make_bus("Bus 2")

    network.add(bus_1)
    network.add(bus_2)

    assert network.bus_ids == {
        bus_1.id,
        bus_2.id,
    }