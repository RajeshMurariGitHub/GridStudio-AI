"""
GridStudio AI

Module:
    models.py

Description:
    Defines the canonical base model used throughout GridStudio AI.

    The model establishes common validation, immutability,
    serialization, and equality behavior for GridStudio domain,
    configuration, simulation, and result models.

    All GridStudio data models should normally inherit directly or
    indirectly from this class unless a specific subsystem requires
    fundamentally different behavior.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict


# ============================================================================
# Base Model
# ============================================================================


class BaseModel(PydanticBaseModel):
    """
    Canonical base model for GridStudio AI.

    Design Principles
    -----------------
    GridStudio models are:

    * strongly validated,
    * immutable after construction,
    * explicit about accepted fields,
    * serializable through standard Pydantic APIs,
    * compatible with arbitrary engineering value types where
      required.

    Notes
    -----
    Immutability is important because electrical network models
    should describe a well-defined system state.

    Operational changes, time-series updates, optimization
    decisions, and simulation states should therefore normally
    create updated model instances rather than silently mutating
    shared domain objects.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        populate_by_name=True,
        arbitrary_types_allowed=True,
        validate_default=True,
        str_strip_whitespace=True,
    )

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(
        self,
        *,
        exclude_none: bool = False,
    ) -> dict[str, Any]:
        """
        Convert the model to a Python dictionary.

        Parameters
        ----------
        exclude_none
            If True, fields whose value is None are omitted.

        Returns
        -------
        dict[str, Any]
            Serialized model data.
        """

        return self.model_dump(
            mode="python",
            exclude_none=exclude_none,
        )

    def to_json(
        self,
        *,
        exclude_none: bool = False,
        indent: int | None = None,
    ) -> str:
        """
        Serialize the model to JSON.

        Parameters
        ----------
        exclude_none
            If True, fields whose value is None are omitted.

        indent
            Optional JSON indentation level.

        Returns
        -------
        str
            JSON representation of the model.
        """

        return self.model_dump_json(
            exclude_none=exclude_none,
            indent=indent,
        )

    # ------------------------------------------------------------------
    # Immutable Update
    # ------------------------------------------------------------------

    def updated(
        self,
        **changes: Any,
    ) -> BaseModel:
        """
        Return a new model containing the requested field changes.

        Parameters
        ----------
        **changes
            Field values to replace.

        Returns
        -------
        BaseModel
            New immutable model instance.

        Notes
        -----
        The original instance is never modified.

        Example
        -------
        A model may be updated using:

            updated_bus = bus.updated(
                nominal_voltage_kv=11.0,
            )
        """

        return self.model_copy(
            update=changes,
            deep=True,
        )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "BaseModel",
]