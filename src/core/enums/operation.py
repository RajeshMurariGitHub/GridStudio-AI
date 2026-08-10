"""
GridStudio AI

Module:
    operation.py

Description:
    Core enumerations describing solver-independent operational
    states and control modes of electrical assets used throughout
    GridStudio AI.

    These enumerations represent the physical or operational state
    of network equipment. Simulation execution status, numerical
    convergence, and solver-specific concepts must not be defined
    in this module.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from enum import StrEnum


# ============================================================================
# Asset Status
# ============================================================================


class AssetStatus(StrEnum):
    """
    Lifecycle and availability status of a physical electrical asset.

    IN_SERVICE
        Asset is commissioned and available for normal operation.

    OUT_OF_SERVICE
        Asset exists in the network but is intentionally unavailable
        for electrical operation.

    MAINTENANCE
        Asset is unavailable or restricted because maintenance is
        being performed.

    PLANNED
        Asset is planned but has not yet been commissioned.

    DECOMMISSIONED
        Asset has been permanently removed from operational service.

    FAULTED
        Asset is unavailable because of a fault or abnormal condition.

    Notes
    -----
    AssetStatus describes the broader operational availability of
    physical equipment.

    It is intentionally distinct from the open/closed state of
    switching devices.
    """

    IN_SERVICE = "in_service"
    OUT_OF_SERVICE = "out_of_service"
    MAINTENANCE = "maintenance"
    PLANNED = "planned"
    DECOMMISSIONED = "decommissioned"
    FAULTED = "faulted"


# ============================================================================
# Switching State
# ============================================================================


class SwitchState(StrEnum):
    """
    Electrical state of a switching device.

    OPEN
        Switching device electrically disconnects its terminals.

    CLOSED
        Switching device electrically connects its terminals.

    UNKNOWN
        Switching state is unavailable or cannot be determined.

    Notes
    -----
    SwitchState represents electrical connectivity.

    AssetStatus independently describes whether the switching
    device itself is available for service.
    """

    OPEN = "open"
    CLOSED = "closed"
    UNKNOWN = "unknown"


# ============================================================================
# Operating Mode
# ============================================================================


class OperatingMode(StrEnum):
    """
    High-level operating mode of a controllable electrical asset.

    AUTOMATIC
        Asset operation is controlled automatically.

    MANUAL
        Asset operation is controlled manually.

    REMOTE
        Asset is controlled remotely by an external supervisory
        system or operator.

    LOCAL
        Asset is controlled locally at the equipment.

    SCHEDULED
        Asset follows a predefined operating schedule.

    DISABLED
        Automatic or commanded operation is disabled.

    Notes
    -----
    This enumeration describes broad operational control behavior.

    Equipment-specific control strategies such as Volt-VAR,
    Volt-Watt, constant power factor, battery SOC control, or
    transformer voltage regulation should be represented by
    dedicated control models rather than continually expanding
    this generic enumeration.
    """

    AUTOMATIC = "automatic"
    MANUAL = "manual"
    REMOTE = "remote"
    LOCAL = "local"
    SCHEDULED = "scheduled"
    DISABLED = "disabled"


# ============================================================================
# Dispatch State
# ============================================================================


class DispatchState(StrEnum):
    """
    High-level dispatch state of a controllable power resource.

    IDLE
        Resource is available but currently exchanging no commanded
        active power.

    GENERATING
        Resource is supplying active power to the network.

    CONSUMING
        Resource is absorbing active power from the network.

    CHARGING
        Energy-storage resource is charging.

    DISCHARGING
        Energy-storage resource is discharging.

    CURTAILED
        Resource output is intentionally limited below its available
        capability.

    UNAVAILABLE
        Resource is not currently available for dispatch.

    Notes
    -----
    This enumeration provides a common operational vocabulary for
    generators, DERs, storage, EVs, and other controllable resources.

    Detailed dispatch setpoints remain numerical properties of the
    corresponding domain or time-series models.
    """

    IDLE = "idle"
    GENERATING = "generating"
    CONSUMING = "consuming"
    CHARGING = "charging"
    DISCHARGING = "discharging"
    CURTAILED = "curtailed"
    UNAVAILABLE = "unavailable"


# ============================================================================
# Availability State
# ============================================================================


class AvailabilityState(StrEnum):
    """
    Availability state of an electrical resource.

    AVAILABLE
        Resource is available for normal operation or dispatch.

    UNAVAILABLE
        Resource cannot currently participate in operation.

    LIMITED
        Resource is available but subject to reduced capability.

    UNKNOWN
        Availability cannot currently be established.

    Notes
    -----
    AvailabilityState is useful for operational, time-series,
    forecasting, and future digital-twin workflows where temporary
    availability may differ from the asset's lifecycle status.
    """

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    LIMITED = "limited"
    UNKNOWN = "unknown"


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "AssetStatus",
    "AvailabilityState",
    "DispatchState",
    "OperatingMode",
    "SwitchState",
]