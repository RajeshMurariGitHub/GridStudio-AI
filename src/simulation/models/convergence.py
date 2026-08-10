"""
GridStudio AI

Module:
    convergence.py

Description:
    Defines solver-independent convergence information produced by
    GridStudio simulation engines.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class ConvergenceInfo(BaseModel):
    """
    Solver-independent convergence information.

    This model records whether a numerical simulation converged and
    provides optional diagnostic information supplied by the
    simulation engine.

    It deliberately avoids solver-specific exception types and
    internal solver objects.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    converged: bool = Field(
        ...,
        description=(
            "Whether the numerical simulation converged."
        ),
    )

    iterations: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Number of numerical iterations when available."
        ),
    )

    tolerance: float | None = Field(
        default=None,
        ge=0.0,
        description=(
            "Convergence tolerance used by the solver when known."
        ),
    )

    message: str | None = Field(
        default=None,
        description=(
            "Solver-independent convergence or diagnostic message."
        ),
    )


__all__ = [
    "ConvergenceInfo",
]