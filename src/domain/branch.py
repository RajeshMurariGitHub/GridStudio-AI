"""
GridStudio AI

Module:
    branch.py

Description:
    Defines the foundational electrical branch model used
    throughout the GridStudio AI domain.

    A Branch represents a two-terminal electrical element connecting
    two nodes in the network topology.

    The model provides solver-independent connectivity shared by
    lines, switches, transformers, and other branch-type equipment.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from uuid import UUID

from pydantic import Field
from pydantic import model_validator

from src.domain.element import Element


# ============================================================================
# Branch
# ============================================================================


class Branch(Element):
    """
    Base class for two-terminal electrical network elements.

    A Branch connects two distinct electrical nodes.

    Examples include:

    * transmission lines,
    * distribution lines,
    * switches,
    * two-winding transformers,
    * future series devices.

    Parameters
    ----------
    from_node_id
        Identifier of the node at the first branch terminal.

    to_node_id
        Identifier of the node at the second branch terminal.

    Notes
    -----
    ``from_node_id`` and ``to_node_id`` define topology only.

    They do not necessarily imply physical power-flow direction.
    AC power flow may reverse depending on the operating condition.

    Electrical parameters such as impedance, admittance, length,
    thermal rating, transformer ratio, or switch position belong
    to specialized branch models.

    Branch objects store node identifiers rather than Node objects
    directly. This avoids circular object graphs and keeps network
    ownership and topology validation centralized in the Network
    layer.
    """

    # ------------------------------------------------------------------
    # Connectivity
    # ------------------------------------------------------------------

    from_node_id: UUID = Field(
        ...,
        description=(
            "Identifier of the node connected to the first "
            "branch terminal."
        ),
    )

    to_node_id: UUID = Field(
        ...,
        description=(
            "Identifier of the node connected to the second "
            "branch terminal."
        ),
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def _validate_terminals(
        self,
    ) -> Branch:
        """
        Validate branch terminal connectivity.

        Returns
        -------
        Branch
            Validated branch instance.

        Raises
        ------
        ValueError
            If both branch terminals reference the same node.
        """

        if self.from_node_id == self.to_node_id:
            raise ValueError(
                "A branch must connect two distinct nodes."
            )

        return self

    # ------------------------------------------------------------------
    # Convenience Properties
    # ------------------------------------------------------------------

    @property
    def terminal_node_ids(
        self,
    ) -> tuple[UUID, UUID]:
        """
        Return both branch terminal node identifiers.
        """

        return (
            self.from_node_id,
            self.to_node_id,
        )

    # ------------------------------------------------------------------
    # Connectivity Queries
    # ------------------------------------------------------------------

    def connects(
        self,
        node_id: UUID,
    ) -> bool:
        """
        Return whether the branch connects to the given node.

        Parameters
        ----------
        node_id
            Node identifier.

        Returns
        -------
        bool
            True when the node is one of the branch terminals.
        """

        return node_id in self.terminal_node_ids

    def connects_between(
        self,
        node_a_id: UUID,
        node_b_id: UUID,
    ) -> bool:
        """
        Return whether the branch connects the two given nodes.

        Terminal ordering is ignored.

        Parameters
        ----------
        node_a_id
            First node identifier.

        node_b_id
            Second node identifier.

        Returns
        -------
        bool
            True when the branch connects the requested node pair.
        """

        return (
            (
                self.from_node_id == node_a_id
                and self.to_node_id == node_b_id
            )
            or (
                self.from_node_id == node_b_id
                and self.to_node_id == node_a_id
            )
        )

    def opposite_node(
        self,
        node_id: UUID,
    ) -> UUID:
        """
        Return the node at the opposite branch terminal.

        Parameters
        ----------
        node_id
            Identifier of one branch terminal.

        Returns
        -------
        UUID
            Identifier of the opposite terminal.

        Raises
        ------
        ValueError
            If the requested node is not connected to this branch.
        """

        if node_id == self.from_node_id:
            return self.to_node_id

        if node_id == self.to_node_id:
            return self.from_node_id

        raise ValueError(
            f"Node {node_id} is not connected to branch {self.id}."
        )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Branch",
]