"""
GridStudio

Module:
    base_model.py

Description:
    Common base class for all Pydantic models used throughout
    GridStudio.

    This class centralizes project-wide validation,
    serialization, and configuration so that every model
    behaves consistently.

Author:
    Rajesh Murari

License:
    MIT

Python:
    >=3.12
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict


class BaseModel(PydanticBaseModel):
    """
    Common base class for all GridStudio models.

    Notes
    -----
    Every project model should inherit from this class
    instead of directly inheriting from
    ``pydantic.BaseModel``.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
        validate_default=True,
    )

    def to_dict(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Convert model to a Python dictionary.
        """
        return self.model_dump(**kwargs)

    def to_json(
        self,
        **kwargs: Any,
    ) -> str:
        """
        Convert model to JSON.
        """
        return self.model_dump_json(**kwargs)

    def clone(
        self,
        **kwargs: Any,
    ) -> "BaseModel":
        """
        Return a deep copy of the model.
        """
        return self.model_copy(
            deep=True,
            update=kwargs,
        )
