"""
GridStudio AI

Module:
    engine.py

Description:
    Defines the solver-independent base contract for simulation
    engines used by GridStudio AI.

    A simulation engine provides a common interface between the
    GridStudio domain model and an external or internal numerical
    solver.

    Concrete engine implementations are responsible for translating
    GridStudio models into solver-specific representations, executing
    the requested engineering study, and mapping solver outputs back
    into GridStudio-compatible results.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from src.core.enums.simulation import SimulationMode
from src.core.enums.simulation import StudyType

from .capabilities import EngineCapabilities


# ============================================================================
# Simulation Engine
# ============================================================================


class SimulationEngine(ABC):
    """
    Solver-independent simulation-engine contract.

    Concrete engines provide the boundary between GridStudio AI and
    numerical simulation backends such as pandapower or OpenDSS.

    Design Principles
    -----------------
    A SimulationEngine:

    * identifies the concrete simulation backend,
    * declares its supported engineering capabilities,
    * exposes solver-independent capability checks,
    * provides a common execution boundary,
    * does not introduce solver-specific concepts into the domain
      model.

    Notes
    -----
    The base engine deliberately does not inherit from the GridStudio
    Pydantic BaseModel.

    Engines are runtime service objects rather than immutable
    engineering data models. Concrete engines may contain solver
    objects, caches, converters, configuration, or other runtime
    state.

    Solver-specific conversion and result mapping belong to concrete
    engine packages rather than this base abstraction.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the canonical engine name.

        Returns
        -------
        str
            Stable human-readable name of the simulation engine.

        Examples
        --------
        Concrete implementations may return names such as:

            "pandapower"

        or:

            "opendss"
        """

        raise NotImplementedError

    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def capabilities(self) -> EngineCapabilities:
        """
        Return the capabilities supported by this engine.

        Returns
        -------
        EngineCapabilities
            Solver-independent engine capability metadata.
        """

        raise NotImplementedError

    def supports_study(
        self,
        study_type: StudyType,
    ) -> bool:
        """
        Return whether the engine supports an engineering study.

        Parameters
        ----------
        study_type
            Engineering study type to check.

        Returns
        -------
        bool
            True when the study is supported.
        """

        return self.capabilities.supports_study(
            study_type
        )

    def supports_mode(
        self,
        simulation_mode: SimulationMode,
    ) -> bool:
        """
        Return whether the engine supports a simulation mode.

        Parameters
        ----------
        simulation_mode
            Simulation execution mode to check.

        Returns
        -------
        bool
            True when the simulation mode is supported.
        """

        return self.capabilities.supports_mode(
            simulation_mode
        )

    def supports(
        self,
        study_type: StudyType,
        simulation_mode: SimulationMode,
    ) -> bool:
        """
        Return whether the requested study and mode are supported.

        Parameters
        ----------
        study_type
            Engineering study type to check.

        simulation_mode
            Simulation execution mode to check.

        Returns
        -------
        bool
            True when both capabilities are supported.

        Notes
        -----
        This delegates to EngineCapabilities and therefore currently
        represents independent study and mode membership.

        It does not imply support for every possible combination of
        a supported StudyType and SimulationMode.
        """

        return self.capabilities.supports(
            study_type,
            simulation_mode,
        )

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    @abstractmethod
    def run(
        self,
        request: Any,
    ) -> Any:
        """
        Execute a simulation request.

        Parameters
        ----------
        request
            Solver-independent simulation request supplied by
            GridStudio AI.

        Returns
        -------
        Any
            Solver-independent simulation result.

        Notes
        -----
        The request and result types are intentionally generic at
        this stage of the architecture.

        Concrete request and result models should replace Any once
        the canonical GridStudio simulation input/output contracts
        are introduced.

        Concrete engines are responsible for:

        1. validating that the requested study is supported,
        2. converting GridStudio domain objects into solver-specific
           representations,
        3. invoking the numerical solver,
        4. mapping solver outputs into GridStudio-compatible results.

        Solver-specific objects should not escape through this
        public interface.
        """

        raise NotImplementedError


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "SimulationEngine",
]