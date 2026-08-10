"""
GridStudio AI

Module:
    injection.py

Description:
    Defines the foundational electrical injection model used
    throughout the GridStudio AI domain.

    An Injection represents electrical equipment connected to a
    network node that may inject or absorb active and reactive
    power.

    The abstraction is solver-independent and provides a common
    foundation for loads, generators, distributed energy resources,
    batteries, electric vehicles, and other power-injection devices.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from src.domain.element import Element


# ============================================================================
# Injection
# ============================================================================


class Injection(Element):
    """
    Base class for electrical power injections.

    An Injection represents an electrical element connected to one
    network node that may exchange active and reactive power with
    the electrical network.

    Examples include:

    * loads,
    * generators,
    * solar PV,
    * wind generation,
    * batteries,
    * electric vehicles,
    * future controllable DER resources.

    Sign Convention
    ---------------
    GridStudio AI uses a network-injection sign convention:

    * positive active power means injection into the network,
    * negative active power means absorption from the network,
    * positive reactive power means reactive-power injection,
    * negative reactive power means reactive-power absorption.

    Therefore:

        generator:
            P > 0

        consuming load:
            P < 0

        battery discharging:
            P > 0

        battery charging:
            P < 0

    Notes
    -----
    External simulation engines may use different conventions.

    Conversion between GridStudio's canonical sign convention and
    engine-specific conventions belongs in the corresponding engine
    adapter or converter.

    For example, pandapower load values are normally represented as
    positive consumption. The pandapower converter must therefore
    perform the required sign conversion rather than changing the
    GridStudio domain convention.
    """

    # ------------------------------------------------------------------
    # Network Connectivity
    # ------------------------------------------------------------------

    node_id: UUID = Field(
        ...,
        description=(
            "Identifier of the network node to which the "
            "injection is connected."
        ),
    )

    # ------------------------------------------------------------------
    # Active Power
    # ------------------------------------------------------------------

    active_power_mw: float = Field(
        default=0.0,
        description=(
            "Active-power injection in MW. Positive values inject "
            "power into the network; negative values absorb power "
            "from the network."
        ),
    )

    # ------------------------------------------------------------------
    # Reactive Power
    # ------------------------------------------------------------------

    reactive_power_mvar: float = Field(
        default=0.0,
        description=(
            "Reactive-power injection in MVAr. Positive values "
            "inject reactive power into the network; negative "
            "values absorb reactive power from the network."
        ),
    )

    # ------------------------------------------------------------------
    # Scaling
    # ------------------------------------------------------------------

    scaling: float = Field(
        default=1.0,
        ge=0.0,
        description=(
            "Multiplicative scaling factor applied to the "
            "specified active and reactive power."
        ),
    )

    # ------------------------------------------------------------------
    # Effective Power
    # ------------------------------------------------------------------

    @property
    def effective_active_power_mw(self) -> float:
        """
        Return scaled active-power injection.
        """

        return (
            self.active_power_mw
            * self.scaling
        )

    @property
    def effective_reactive_power_mvar(self) -> float:
        """
        Return scaled reactive-power injection.
        """

        return (
            self.reactive_power_mvar
            * self.scaling
        )

    @property
    def effective_complex_power_mva(self) -> complex:
        """
        Return scaled complex-power injection.

        Returns
        -------
        complex
            Complex power represented as P + jQ.
        """

        return complex(
            self.effective_active_power_mw,
            self.effective_reactive_power_mvar,
        )

    # ------------------------------------------------------------------
    # Power Exchange Properties
    # ------------------------------------------------------------------

    @property
    def is_injecting_active_power(self) -> bool:
        """
        Return whether the element injects active power.
        """

        return self.effective_active_power_mw > 0.0

    @property
    def is_absorbing_active_power(self) -> bool:
        """
        Return whether the element absorbs active power.
        """

        return self.effective_active_power_mw < 0.0

    @property
    def is_injecting_reactive_power(self) -> bool:
        """
        Return whether the element injects reactive power.
        """

        return (
            self.effective_reactive_power_mvar
            > 0.0
        )

    @property
    def is_absorbing_reactive_power(self) -> bool:
        """
        Return whether the element absorbs reactive power.
        """

        return (
            self.effective_reactive_power_mvar
            < 0.0
        )

    @property
    def is_idle(self) -> bool:
        """
        Return whether the element exchanges no active or
        reactive power.
        """

        return (
            self.effective_active_power_mw == 0.0
            and
            self.effective_reactive_power_mvar == 0.0
        )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Injection",
]