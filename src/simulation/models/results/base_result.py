"""
GridStudio

Module:
    base_result.py

Description:
    Base model for all simulation results.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field

from src.core.models import BaseModel


class BaseSimulationResult(BaseModel):
    """
    Base class for all simulation results.
    """

    simulation_id: UUID

    simulation_name: str = Field(
        default="",
        description="Simulation name.",
    )

    successful: bool = Field(
        default=False,
        description="True if the simulation completed successfully.",
    )

    started_at: datetime = Field(
        description="Simulation start time.",
    )

    completed_at: datetime = Field(
        description="Simulation completion time.",
    )

    execution_time_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Wall-clock execution time.",
    )

    solver_name: str = Field(
        default="",
        description="Solver algorithm name.",
    )

    solver_version: str = Field(
        default="",
        description="Solver implementation version.",
    )

    notes: str = Field(
        default="",
        description="Additional execution notes.",
    )

    warnings: list[str] = Field(
        default_factory=list,
    )

    errors: list[str] = Field(
        default_factory=list,
    )

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    @property
    def has_warnings(self) -> bool:
        return bool(self.warnings)
