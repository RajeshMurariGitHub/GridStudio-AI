"""
GridStudio AI

Module:
    asset.py

Description:
    Defines the foundational electrical asset model used throughout
    the GridStudio AI domain.

    ElectricalAsset extends ElectricalComponent with lifecycle and
    operational availability information appropriate for physical
    electrical equipment.

    The model is solver-independent and is shared by balanced and
    unbalanced network representations.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from pydantic import Field

from src.core.enums import (
    AssetStatus,
    AvailabilityState,
)
from src.domain.base import DomainModel


# ============================================================================
# Electrical Asset
# ============================================================================


class Asset(DomainModel):
    """
    Base class for physical electrical assets.

    ElectricalAsset represents equipment that physically exists in
    the electrical system and may participate in network operation.

    Examples include:

    * buses,
    * lines,
    * transformers,
    * switches,
    * loads,
    * generators,
    * solar PV,
    * wind generation,
    * batteries,
    * electric vehicles,
    * shunts.

    Responsibilities
    ----------------
    ElectricalAsset adds:

    * lifecycle / service status,
    * temporary operational availability.

    Notes
    -----
    ``status`` and ``availability`` represent different concepts.

    ``status`` describes the broader lifecycle or service condition
    of the physical asset.

    ``availability`` describes whether the asset can currently
    participate in operation.

    For example, an asset may be:

        status = AssetStatus.IN_SERVICE
        availability = AvailabilityState.LIMITED

    meaning that the asset remains commissioned and operational but
    currently has reduced capability.

    Switching position, dispatch state, tap position, state of
    charge, and other equipment-specific operating states do not
    belong in this generic base class.
    """

    # ------------------------------------------------------------------
    # Service Status
    # ------------------------------------------------------------------

    status: AssetStatus = Field(
        default=AssetStatus.IN_SERVICE,
        description=(
            "Lifecycle and service status of the physical "
            "electrical asset."
        ),
    )

    # ------------------------------------------------------------------
    # Operational Availability
    # ------------------------------------------------------------------

    availability: AvailabilityState = Field(
        default=AvailabilityState.AVAILABLE,
        description=(
            "Current operational availability of the asset."
        ),
    )

    # ------------------------------------------------------------------
    # Convenience Properties
    # ------------------------------------------------------------------

    @property
    def is_in_service(self) -> bool:
        """
        Return whether the asset is in normal service.
        """

        return self.status == AssetStatus.IN_SERVICE

    @property
    def is_available(self) -> bool:
        """
        Return whether the asset is fully available.
        """

        return (
            self.availability
            == AvailabilityState.AVAILABLE
        )

    @property
    def is_limited(self) -> bool:
        """
        Return whether the asset has limited availability.
        """

        return (
            self.availability
            == AvailabilityState.LIMITED
        )

    @property
    def is_operational(self) -> bool:
        """
        Return whether the asset can participate in the model.

        An asset is considered operational when:

        * the GridStudio component is enabled,
        * the physical asset is in service,
        * the asset is not operationally unavailable.

        Limited assets remain operational because their available
        capability may still be used.
        """

        return (
            self.enabled
            and self.status == AssetStatus.IN_SERVICE
            and self.availability
            != AvailabilityState.UNAVAILABLE
        )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Asset",
]