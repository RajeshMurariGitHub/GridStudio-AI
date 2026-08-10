"""
GridStudio

Module:
    base_state.py

Description:
    Base class for all simulation state objects.

    A state object represents the calculated operating
    condition of a domain asset during a simulation.

Author:
    Rajesh Murari

License:
    MIT

Python:
    >=3.12
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import ConfigDict, Field


from src.core.enums.validation import ValidationStatus
from src.core.models import BaseModel

class BaseState(BaseModel):
    """
    Base class for all simulation state objects.

    Notes
    -----
    This class contains only metadata common to every
    simulated asset. Electrical quantities are introduced
    in derived classes.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    asset_id: UUID

    validation_status: ValidationStatus = ValidationStatus.VALID

    warnings: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )
