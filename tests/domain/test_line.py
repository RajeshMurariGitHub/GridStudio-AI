"""
Unit tests for the Line domain model.

Module:
    test_line.py

Description:
    Tests the Line domain model, electrical parameter integration,
    current-rating behavior, and validation.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.domain.bus import Bus
from src.domain.line import Line
from src.domain.electrical.line_parameters import LineParameters


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def create_bus(name: str) -> Bus:
    """
    Create a valid test bus.
    """

    return Bus(
        name=name,
        nominal_voltage_kv=11.0,
    )


def create_parameters(
    *,
    r1_ohm_per_km: float = 0.05,
    x1_ohm_per_km: float = 0.20,
    c1_nf_per_km: float = 0.0,
) -> LineParameters:
    """
    Create valid balanced line parameters.
    """

    return LineParameters.balanced(
        r1_ohm_per_km=r1_ohm_per_km,
        x1_ohm_per_km=x1_ohm_per_km,
        c1_nf_per_km=c1_nf_per_km,
    )


def create_line(**kwargs):
    """
    Create a valid line together with the buses it connects.
    """

    bus1 = create_bus("BUS1")
    bus2 = create_bus("BUS2")

    defaults = {
        "name": "L1",
        "from_node_id": bus1.id,
        "to_node_id": bus2.id,
        "length_km": 10.0,
        "parameters": create_parameters(),
        "maximum_current_ka": 1.0,
    }

    defaults.update(kwargs)

    line = Line(**defaults)

    return line, bus1, bus2


# ---------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------


def test_create_line():
    """
    Verify that a valid Line object can be created.
    """

    line, bus1, bus2 = create_line()

    assert line.name == "L1"

    assert line.from_node_id == bus1.id
    assert line.to_node_id == bus2.id

    assert line.length_km == pytest.approx(10.0)

    assert line.parameters.r1_ohm_per_km == pytest.approx(0.05)
    assert line.parameters.x1_ohm_per_km == pytest.approx(0.20)
    assert line.parameters.c1_nf_per_km == pytest.approx(0.0)

    assert line.maximum_current_ka == pytest.approx(1.0)

    assert line.has_current_rating is True
    assert line.parallel_count == 1


# ---------------------------------------------------------------------
# Electrical parameter integration
# ---------------------------------------------------------------------


def test_balanced_parameter_model():
    """
    Verify balanced line parameters are recognized correctly.
    """

    line, _, _ = create_line()

    assert line.is_balanced_parameter_model is True
    assert line.is_phase_domain_parameter_model is False


def test_positive_sequence_impedance():
    """
    Verify positive-sequence impedance is exposed by parameters.
    """

    parameters = create_parameters(
        r1_ohm_per_km=0.082,
        x1_ohm_per_km=0.317,
    )

    line, _, _ = create_line(
        parameters=parameters,
    )

    assert (
        line.parameters.positive_sequence_impedance_ohm_per_km
        == pytest.approx(complex(0.082, 0.317))
    )


def test_line_length_and_parameters_are_separate():
    """
    Verify physical length and reusable electrical parameters
    remain separate domain concepts.
    """

    parameters = create_parameters(
        r1_ohm_per_km=0.082,
        x1_ohm_per_km=0.317,
        c1_nf_per_km=5.2,
    )

    line, _, _ = create_line(
        length_km=32.5,
        parameters=parameters,
    )

    assert line.length_km == pytest.approx(32.5)

    assert line.parameters.r1_ohm_per_km == pytest.approx(0.082)
    assert line.parameters.x1_ohm_per_km == pytest.approx(0.317)
    assert line.parameters.c1_nf_per_km == pytest.approx(5.2)


# ---------------------------------------------------------------------
# Current rating
# ---------------------------------------------------------------------


def test_current_rating():
    """
    Verify a configured current rating is reported correctly.
    """

    line, _, _ = create_line(
        maximum_current_ka=1.25,
    )

    assert line.has_current_rating is True
    assert line.maximum_current_ka == pytest.approx(1.25)
    assert line.total_current_capacity_ka == pytest.approx(1.25)


def test_no_current_rating():
    """
    Verify current-rating properties when no rating is defined.
    """

    line, _, _ = create_line(
        maximum_current_ka=None,
    )

    assert line.has_current_rating is False
    assert line.total_current_capacity_ka is None


def test_parallel_current_capacity():
    """
    Verify aggregate capacity for parallel circuits.
    """

    line, _, _ = create_line(
        maximum_current_ka=1.2,
        parallel_count=3,
    )

    assert line.parallel_count == 3
    assert line.total_current_capacity_ka == pytest.approx(3.6)


# ---------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------


def test_zero_length_line_invalid():
    """
    Verify that a zero-length line is rejected.
    """

    with pytest.raises(ValidationError):
        create_line(length_km=0.0)


@pytest.mark.parametrize(
    "length_km",
    [
        -1.0,
        -0.001,
    ],
)
def test_negative_length_invalid(length_km):
    """
    Verify that negative line lengths are rejected.
    """

    with pytest.raises(ValidationError):
        create_line(length_km=length_km)


@pytest.mark.parametrize(
    "current",
    [
        0.0,
        -1.0,
        -0.001,
    ],
)
def test_invalid_maximum_current(current):
    """
    Verify that non-positive current ratings are rejected.
    """

    with pytest.raises(ValidationError):
        create_line(maximum_current_ka=current)


@pytest.mark.parametrize(
    "parallel_count",
    [
        0,
        -1,
        -5,
    ],
)
def test_invalid_parallel_count(parallel_count):
    """
    Verify that at least one parallel circuit is required.
    """

    with pytest.raises(ValidationError):
        create_line(parallel_count=parallel_count)