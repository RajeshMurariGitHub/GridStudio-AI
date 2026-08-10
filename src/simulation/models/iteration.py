"""
GridStudio AI

Module:
    iteration.py

Description:
    Defines solver-independent numerical iteration records for
    GridStudio simulations.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class IterationRecord(BaseModel):
    """
    Solver-independent numerical iteration record.

    Engines may populate iteration history when their underlying
    solver exposes suitable iteration diagnostics.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    iteration: int = Field(
        ...,
        ge=0,
        description="Iteration number.",
    )

    residual: float | None = Field(
        default=None,
        ge=0.0,
        description=(
            "Representative numerical residual when available."
        ),
    )

    converged: bool | None = Field(
        default=None,
        description=(
            "Whether convergence had been achieved at this "
            "iteration when known."
        ),
    )


__all__ = [
    "IterationRecord",
]