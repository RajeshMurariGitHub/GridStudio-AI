"""
Base simulation-engine contracts.

This package defines the engine-independent interfaces used by
GridStudio simulation backends.

Concrete simulation engines, such as pandapower and OpenDSS, should
implement :class:`SimulationEngine` and declare their supported
features through :class:`EngineCapabilities`.
"""

from .capabilities import EngineCapabilities
from .engine import SimulationEngine


__all__ = [
    "EngineCapabilities",
    "SimulationEngine",
]