"""
GridStudio AI

Module:
    base.py

Description:
    Defines the foundational electrical component model used by
    the GridStudio AI domain layer.

    ElectricalComponent provides common identity, naming,
    enablement, tagging, and metadata fields shared by physical
    electrical assets and other identifiable network components.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from typing import Any
from uuid import UUID
from uuid import uuid4

from pydantic import Field

from src.core.models import BaseModel


# ============================================================================
# Electrical Component
# ============================================================================


class DomainModel(BaseModel):
    """
    Base class for identifiable electrical domain components.

    All physical electrical assets and network components should
    normally inherit from this model directly or indirectly.

    Responsibilities
    ----------------
    DomainModel provides:

    * stable unique identity,
    * human-readable naming,
    * model-level enablement,
    * lightweight classification tags,
    * extensible metadata.

    Notes
    -----
    ``enabled`` describes whether the component participates in the
    GridStudio model.

    It is intentionally different from operational concepts such as
    asset availability, in-service state, switch position, or
    dispatch state.

    Those concepts belong to the corresponding asset or operational
    models.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    id: UUID = Field(
        default_factory=uuid4,
        description="Globally unique identifier for the component.",
    )

    name: str = Field(
        ...,
        min_length=1,
        description="Human-readable component name.",
    )

    # ------------------------------------------------------------------
    # Model Participation
    # ------------------------------------------------------------------

    enabled: bool = Field(
        default=True,
        description=(
            "Whether the component is enabled in the GridStudio "
            "network model."
        ),
    )

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    tags: frozenset[str] = Field(
        default_factory=frozenset,
        description=(
            "User-defined classification tags associated with "
            "the component."
        ),
    )

    # ------------------------------------------------------------------
    # Extensible Metadata
    # ------------------------------------------------------------------

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Additional non-electrical metadata associated with "
            "the component."
        ),
    )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "DomainModel",
]