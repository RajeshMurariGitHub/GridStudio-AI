"""
GridStudio

Module:
    exceptions.py

Description:
    Defines the custom exception hierarchy used throughout the GridStudio
    platform. All application-specific exceptions inherit from
    ``GridStudioError`` to provide a consistent error handling strategy.

Author:
    Rajesh Murari

License:
    MIT

Python:
    >=3.12
"""

from __future__ import annotations


class GridStudioError(Exception):
    """
    Base exception for all GridStudio errors.

    All custom exceptions in the application should inherit from this class.
    """

    pass


# ============================================================================
# Configuration Exceptions
# ============================================================================


class ConfigurationError(GridStudioError):
    """
    Base exception for configuration-related errors.
    """

    pass


class ConfigurationFileNotFoundError(ConfigurationError):
    """
    Raised when a required configuration file cannot be found.
    """

    pass


class ConfigurationValidationError(ConfigurationError):
    """
    Raised when configuration validation fails.
    """

    pass


class ConfigurationLoadError(ConfigurationError):
    """
    Raised when a configuration file cannot be loaded or parsed.
    """

    pass


# ============================================================================
# Network Exceptions
# ============================================================================


class NetworkError(GridStudioError):
    """
    Base exception for electrical network errors.
    """

    pass


class NetworkLoadError(NetworkError):
    """
    Raised when a network model cannot be loaded.
    """

    pass


class NetworkValidationError(NetworkError):
    """
    Raised when a network model fails validation.
    """

    pass


class UnsupportedNetworkError(NetworkError):
    """
    Raised when an unsupported network type is requested.
    """

    pass


# ============================================================================
# Simulation Exceptions
# ============================================================================


class SimulationError(GridStudioError):
    """
    Base exception for simulation-related errors.
    """

    pass


class PowerFlowError(SimulationError):
    """
    Raised when a power flow calculation fails.
    """

    pass


class OptimalPowerFlowError(SimulationError):
    """
    Raised when an optimal power flow calculation fails.
    """

    pass


class StateEstimationError(SimulationError):
    """
    Raised when state estimation fails.
    """

    pass


class ConvergenceError(SimulationError):
    """
    Raised when an iterative algorithm fails to converge.
    """

    pass


# ============================================================================
# Forecasting Exceptions
# ============================================================================


class ForecastingError(GridStudioError):
    """
    Base exception for forecasting-related errors.
    """

    pass


# ============================================================================
# Optimization Exceptions
# ============================================================================


class OptimizationError(GridStudioError):
    """
    Base exception for optimization-related errors.
    """

    pass


# ============================================================================
# Storage Exceptions
# ============================================================================


class StorageError(GridStudioError):
    """
    Base exception for storage-related errors.
    """

    pass


# ============================================================================
# Dashboard Exceptions
# ============================================================================


class DashboardError(GridStudioError):
    """
    Base exception for dashboard-related errors.
    """

    pass


# ============================================================================
# API Exceptions
# ============================================================================


class APIError(GridStudioError):
    """
    Base exception for REST API errors.
    """

    pass


# ============================================================================
# Artificial Intelligence Exceptions
# ============================================================================


class AIError(GridStudioError):
    """
    Base exception for AI-related errors.
    """

    pass


__all__ = [
    "GridStudioError",
    # Configuration
    "ConfigurationError",
    "ConfigurationFileNotFoundError",
    "ConfigurationValidationError",
    "ConfigurationLoadError",
    # Network
    "NetworkError",
    "NetworkLoadError",
    "NetworkValidationError",
    "UnsupportedNetworkError",
    # Simulation
    "SimulationError",
    "PowerFlowError",
    "OptimalPowerFlowError",
    "StateEstimationError",
    "ConvergenceError",
    # Forecasting
    "ForecastingError",
    # Optimization
    "OptimizationError",
    # Storage
    "StorageError",
    # Dashboard
    "DashboardError",
    # API
    "APIError",
    # AI
    "AIError",
]
