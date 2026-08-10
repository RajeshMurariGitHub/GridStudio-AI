"""
GridStudio AI

Module:
    capabilities.py

Description:
    Defines solver-independent capability metadata for simulation
    engines used by GridStudio AI.

    Engine capabilities describe which engineering study types and
    simulation modes an engine supports.

    Capability metadata allows higher-level GridStudio services to
    determine whether an engine is suitable for a requested study
    without depending on solver-specific implementation details.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from src.core.enums.simulation import SimulationMode
from src.core.enums.simulation import StudyType
from src.core.models import BaseModel


# ============================================================================
# Engine Capabilities
# ============================================================================


class EngineCapabilities(BaseModel):
    """
    Solver-independent description of simulation-engine capabilities.

    Parameters
    ----------
    study_types
        Engineering study types supported by the engine.

    simulation_modes
        Simulation execution modes supported by the engine.

    Notes
    -----
    Capabilities describe what an engine can perform, not how the
    corresponding numerical problem is solved.

    Solver-specific algorithms, methods, tolerances, and execution
    options belong to the concrete engine implementation.

    Using sets of StudyType and SimulationMode keeps the capability
    model extensible as GridStudio AI introduces additional studies
    and execution modes.
    """

    study_types: frozenset[StudyType] = frozenset()

    simulation_modes: frozenset[SimulationMode] = frozenset()

    # ------------------------------------------------------------------
    # Study Support
    # ------------------------------------------------------------------

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
            True when the study type is supported.
        """

        return study_type in self.study_types

    # ------------------------------------------------------------------
    # Simulation-Mode Support
    # ------------------------------------------------------------------

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

        return simulation_mode in self.simulation_modes

    # ------------------------------------------------------------------
    # Combined Support
    # ------------------------------------------------------------------

    def supports(
        self,
        study_type: StudyType,
        simulation_mode: SimulationMode,
    ) -> bool:
        """
        Return whether both the requested study and mode are supported.

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
        This method represents independent capability membership.

        It does not imply that every supported StudyType can
        necessarily be combined with every supported SimulationMode.

        More detailed compatibility constraints may be introduced
        later if concrete engines require them.
        """

        return (
            self.supports_study(
                study_type
            )
            and self.supports_mode(
                simulation_mode
            )
        )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "EngineCapabilities",
]