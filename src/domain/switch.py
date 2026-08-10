"""
GridStudio AI

Module:
    switch.py

Description:
    Defines the electrical switch model used throughout GridStudio AI.

    A Switch represents a controllable or fixed electrical connection
    between two network nodes.

    Switches directly influence network topology and may represent
    circuit breakers, disconnectors, load-break switches, reclosers,
    sectionalizers, or generic switching devices.

    The model is solver-independent and supports both balanced and
    unbalanced electrical networks.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from pydantic import Field
from pydantic import model_validator

from src.core.enums import SwitchType
from src.domain.branch import Branch


# ============================================================================
# Switch
# ============================================================================


class Switch(Branch):
    """
    Electrical switching device connecting two network nodes.

    A Switch specializes Branch by adding switching state,
    equipment classification, ratings, and optional small closed-state
    impedance.

    Topology
    --------
    The inherited branch terminals define the two nodes connected by
    the switch:

        from_node_id
        to_node_id

    When ``is_closed`` is True, the switch electrically connects its
    terminals.

    When ``is_closed`` is False, the switch electrically separates
    its terminals.

    Examples
    --------
    Switch may represent:

    * circuit breaker,
    * disconnector,
    * load-break switch,
    * recloser,
    * sectionalizer,
    * fuse-like switching representation,
    * generic topology switch.

    Notes
    -----
    ``is_closed`` represents the configured or commanded state of the
    device.

    Runtime operational information such as measured current,
    loading, protection operation, trip cause, or actual field state
    belongs in simulation/operational state models.

    Engine adapters are responsible for mapping this canonical model
    to pandapower, OpenDSS, or another backend.
    """

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    switch_type: SwitchType = Field(
        default=SwitchType.SWITCH,
        description=(
            "Classification of the electrical switching device."
        ),
    )

    # ------------------------------------------------------------------
    # Switching State
    # ------------------------------------------------------------------

    is_closed: bool = Field(
        default=True,
        description=(
            "Configured switch state. True means electrically "
            "closed; False means electrically open."
        ),
    )

    normally_closed: bool = Field(
        default=True,
        description=(
            "Normal operating state of the switch. Used to "
            "distinguish normal topology from temporary switching "
            "configurations."
        ),
    )

    # ------------------------------------------------------------------
    # Ratings
    # ------------------------------------------------------------------

    rated_voltage_kv: float | None = Field(
        default=None,
        gt=0.0,
        description=(
            "Optional rated line-to-line voltage of the switch "
            "in kV."
        ),
    )

    rated_current_ka: float | None = Field(
        default=None,
        gt=0.0,
        description=(
            "Optional continuous-current rating of the switch "
            "in kA."
        ),
    )

    # ------------------------------------------------------------------
    # Closed-State Electrical Characteristics
    # ------------------------------------------------------------------

    resistance_ohm: float = Field(
        default=0.0,
        ge=0.0,
        description=(
            "Closed-state series resistance of the switch in ohms."
        ),
    )

    reactance_ohm: float = Field(
        default=0.0,
        description=(
            "Closed-state series reactance of the switch in ohms."
        ),
    )

    # ------------------------------------------------------------------
    # Operational Capabilities
    # ------------------------------------------------------------------

    remotely_controllable: bool = Field(
        default=False,
        description=(
            "Whether the switch may be operated remotely."
        ),
    )

    automatic_operation_enabled: bool = Field(
        default=False,
        description=(
            "Whether automatic switching operation is enabled."
        ),
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def _validate_switch_configuration(
        self,
    ) -> "Switch":
        """
        Validate switch configuration.
        """

        if (
            self.automatic_operation_enabled
            and not self.remotely_controllable
        ):
            raise ValueError(
                "automatic_operation_enabled requires "
                "remotely_controllable to be True."
            )

        return self

    # ------------------------------------------------------------------
    # State Properties
    # ------------------------------------------------------------------

    @property
    def is_open(self) -> bool:
        """
        Return whether the switch is open.
        """

        return not self.is_closed

    @property
    def is_in_normal_state(self) -> bool:
        """
        Return whether the current configured state equals the
        normal operating state.
        """

        return self.is_closed == self.normally_closed

    @property
    def is_abnormally_open(self) -> bool:
        """
        Return whether a normally closed switch is currently open.
        """

        return (
            self.normally_closed
            and not self.is_closed
        )

    @property
    def is_abnormally_closed(self) -> bool:
        """
        Return whether a normally open switch is currently closed.
        """

        return (
            not self.normally_closed
            and self.is_closed
        )

    # ------------------------------------------------------------------
    # Electrical Properties
    # ------------------------------------------------------------------

    @property
    def closed_impedance_ohm(self) -> complex:
        """
        Return closed-state series impedance.
        """

        return complex(
            self.resistance_ohm,
            self.reactance_ohm,
        )

    @property
    def is_ideal(self) -> bool:
        """
        Return whether the switch is modeled as an ideal
        zero-impedance connection when closed.
        """

        return (
            self.resistance_ohm == 0.0
            and self.reactance_ohm == 0.0
        )

    # ------------------------------------------------------------------
    # Rating Properties
    # ------------------------------------------------------------------

    @property
    def has_voltage_rating(self) -> bool:
        """
        Return whether a voltage rating is defined.
        """

        return self.rated_voltage_kv is not None

    @property
    def has_current_rating(self) -> bool:
        """
        Return whether a current rating is defined.
        """

        return self.rated_current_ka is not None

    # ------------------------------------------------------------------
    # Operational Properties
    # ------------------------------------------------------------------

    @property
    def is_manually_operated(self) -> bool:
        """
        Return whether the switch is not remotely controllable.
        """

        return not self.remotely_controllable

    @property
    def supports_automatic_operation(self) -> bool:
        """
        Return whether automatic switching is enabled.
        """

        return (
            self.remotely_controllable
            and self.automatic_operation_enabled
        )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Switch",
]