"""
GridStudio AI

Module:
    transformer.py

Description:
    Defines the two-winding electrical transformer model used
    throughout GridStudio AI.

    Transformer represents a solver-independent two-terminal
    transformer suitable for balanced and unbalanced power-flow
    studies.

    The model captures transformer ratings, impedance, winding
    connections, phase displacement, and basic tap configuration
    without adopting pandapower- or OpenDSS-specific representations.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from typing import Self

from pydantic import Field
from pydantic import model_validator

from src.domain.branch import Branch
from src.domain.electrical import (
    GROUNDED_WYE,
    ElectricalConnection,
)


# ============================================================================
# Transformer
# ============================================================================


class Transformer(Branch):
    """
    Two-winding electrical transformer.

    Transformer specializes Branch by adding electrical properties
    associated with a two-winding power or distribution transformer.

    Terminal Convention
    -------------------
    The inherited branch terminals are interpreted as:

        from_node_id -> high-voltage winding
        to_node_id   -> low-voltage winding

    Unlike a generic Branch, terminal ordering therefore has
    transformer-specific meaning.

    Parameters
    ----------
    rated_power_mva
        Transformer rated apparent power.

    high_voltage_kv
        Rated line-to-line voltage of the high-voltage winding.

    low_voltage_kv
        Rated line-to-line voltage of the low-voltage winding.

    impedance_percent
        Magnitude of transformer short-circuit impedance expressed
        as a percentage on the transformer rating.

    resistance_percent
        Resistive component of short-circuit impedance expressed
        as a percentage on the transformer rating.

    high_voltage_connection
        Electrical connection of the high-voltage winding.

    low_voltage_connection
        Electrical connection of the low-voltage winding.

    phase_shift_deg
        Low-voltage winding phase displacement relative to the
        high-voltage winding.

    Notes
    -----
    This model represents a two-winding transformer.

    Three-winding and multi-winding transformers should eventually
    use dedicated winding/terminal domain models rather than
    overloading this class.

    Transformer solved quantities such as winding currents,
    loading, losses, and terminal powers belong in TransformerState
    rather than this domain model.
    """

    # ------------------------------------------------------------------
    # Ratings
    # ------------------------------------------------------------------

    rated_power_mva: float = Field(
        ...,
        gt=0.0,
        description=(
            "Rated apparent power of the transformer in MVA."
        ),
    )

    high_voltage_kv: float = Field(
        ...,
        gt=0.0,
        description=(
            "Rated line-to-line voltage of the high-voltage "
            "winding in kV."
        ),
    )

    low_voltage_kv: float = Field(
        ...,
        gt=0.0,
        description=(
            "Rated line-to-line voltage of the low-voltage "
            "winding in kV."
        ),
    )

    # ------------------------------------------------------------------
    # Short-Circuit Impedance
    # ------------------------------------------------------------------

    impedance_percent: float = Field(
        ...,
        gt=0.0,
        description=(
            "Magnitude of transformer short-circuit impedance "
            "in percent on transformer rated power."
        ),
    )

    resistance_percent: float = Field(
        default=0.0,
        ge=0.0,
        description=(
            "Resistive component of transformer short-circuit "
            "impedance in percent on transformer rated power."
        ),
    )

    # ------------------------------------------------------------------
    # No-Load Characteristics
    # ------------------------------------------------------------------

    no_load_loss_kw: float = Field(
        default=0.0,
        ge=0.0,
        description=(
            "Transformer no-load active-power loss in kW."
        ),
    )

    exciting_current_percent: float = Field(
        default=0.0,
        ge=0.0,
        description=(
            "Transformer exciting current as a percentage of "
            "rated current."
        ),
    )

    # ------------------------------------------------------------------
    # Winding Connections
    # ------------------------------------------------------------------

    high_voltage_connection: ElectricalConnection = Field(
        default=GROUNDED_WYE,
        description=(
            "Electrical connection of the high-voltage winding."
        ),
    )

    low_voltage_connection: ElectricalConnection = Field(
        default=GROUNDED_WYE,
        description=(
            "Electrical connection of the low-voltage winding."
        ),
    )

    # ------------------------------------------------------------------
    # Phase Displacement
    # ------------------------------------------------------------------

    phase_shift_deg: float = Field(
        default=0.0,
        ge=-180.0,
        le=180.0,
        description=(
            "Low-voltage winding phase displacement relative to "
            "the high-voltage winding in electrical degrees."
        ),
    )

    # ------------------------------------------------------------------
    # Tap Configuration
    # ------------------------------------------------------------------

    tap_position: int = Field(
        default=0,
        description=(
            "Current transformer tap position relative to the "
            "neutral tap."
        ),
    )

    minimum_tap_position: int | None = Field(
        default=None,
        description=(
            "Optional minimum transformer tap position."
        ),
    )

    maximum_tap_position: int | None = Field(
        default=None,
        description=(
            "Optional maximum transformer tap position."
        ),
    )

    tap_step_percent: float | None = Field(
        default=None,
        gt=0.0,
        description=(
            "Optional voltage-ratio change per tap step in percent."
        ),
    )

    tap_on_high_voltage_side: bool = Field(
        default=True,
        description=(
            "Whether the tap changer is located on the "
            "high-voltage winding."
        ),
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def _validate_transformer_configuration(
        self,
    ) -> Self:
        """
        Validate transformer electrical configuration.
        """

        if self.high_voltage_kv <= self.low_voltage_kv:
            raise ValueError(
                "high_voltage_kv must be greater than "
                "low_voltage_kv."
            )

        if self.resistance_percent > self.impedance_percent:
            raise ValueError(
                "resistance_percent cannot exceed "
                "impedance_percent."
            )

        if (
            self.minimum_tap_position is not None
            and self.maximum_tap_position is not None
            and self.minimum_tap_position
            > self.maximum_tap_position
        ):
            raise ValueError(
                "minimum_tap_position cannot exceed "
                "maximum_tap_position."
            )

        if (
            self.minimum_tap_position is not None
            and self.tap_position
            < self.minimum_tap_position
        ):
            raise ValueError(
                "tap_position cannot be below "
                "minimum_tap_position."
            )

        if (
            self.maximum_tap_position is not None
            and self.tap_position
            > self.maximum_tap_position
        ):
            raise ValueError(
                "tap_position cannot exceed "
                "maximum_tap_position."
            )

        has_tap_limits = (
            self.minimum_tap_position is not None
            or self.maximum_tap_position is not None
        )

        if has_tap_limits and self.tap_step_percent is None:
            raise ValueError(
                "tap_step_percent is required when transformer "
                "tap limits are defined."
            )

        return self

    # ------------------------------------------------------------------
    # Impedance Properties
    # ------------------------------------------------------------------

    @property
    def impedance_pu(self) -> float:
        """
        Return short-circuit impedance magnitude in per unit.
        """

        return self.impedance_percent / 100.0

    @property
    def resistance_pu(self) -> float:
        """
        Return transformer resistance in per unit.
        """

        return self.resistance_percent / 100.0

    @property
    def reactance_percent(self) -> float:
        """
        Return transformer short-circuit reactance in percent.

        The value is derived from impedance magnitude and
        resistance:

            X = sqrt(Z^2 - R^2)
        """

        z_squared = self.impedance_percent ** 2
        r_squared = self.resistance_percent ** 2

        return (z_squared - r_squared) ** 0.5

    @property
    def reactance_pu(self) -> float:
        """
        Return transformer reactance in per unit.
        """

        return self.reactance_percent / 100.0

    # ------------------------------------------------------------------
    # Ratio Properties
    # ------------------------------------------------------------------

    @property
    def nominal_voltage_ratio(self) -> float:
        """
        Return nominal high-voltage to low-voltage ratio.
        """

        return (
            self.high_voltage_kv
            / self.low_voltage_kv
        )

    # ------------------------------------------------------------------
    # Tap Properties
    # ------------------------------------------------------------------

    @property
    def has_tap_changer(self) -> bool:
        """
        Return whether tap-changing capability is configured.
        """

        return self.tap_step_percent is not None

    @property
    def tap_ratio_multiplier(self) -> float:
        """
        Return the configured tap ratio multiplier.

        Neutral tap corresponds to 1.0.
        """

        if self.tap_step_percent is None:
            return 1.0

        return (
            1.0
            + self.tap_position
            * self.tap_step_percent
            / 100.0
        )

    @property
    def effective_voltage_ratio(self) -> float:
        """
        Return nominal voltage ratio adjusted for tap position.

        Notes
        -----
        This property describes the configured domain-level ratio.
        Engine adapters remain responsible for translating tap
        conventions into backend-specific representations.
        """

        if not self.has_tap_changer:
            return self.nominal_voltage_ratio

        if self.tap_on_high_voltage_side:
            return (
                self.nominal_voltage_ratio
                * self.tap_ratio_multiplier
            )

        return (
            self.nominal_voltage_ratio
            / self.tap_ratio_multiplier
        )

    # ------------------------------------------------------------------
    # Winding Properties
    # ------------------------------------------------------------------

    @property
    def high_voltage_node_id(self):
        """
        Return the high-voltage winding node identifier.
        """

        return self.from_node_id

    @property
    def low_voltage_node_id(self):
        """
        Return the low-voltage winding node identifier.
        """

        return self.to_node_id

    @property
    def has_phase_shift(self) -> bool:
        """
        Return whether the transformer introduces phase displacement.
        """

        return self.phase_shift_deg != 0.0


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Transformer",
]