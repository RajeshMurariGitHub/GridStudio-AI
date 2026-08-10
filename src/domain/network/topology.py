"""
GridStudio AI

Module:
    topology.py

Description:
    Defines solver-independent electrical topology analysis for the
    canonical GridStudio Network.

    Topology translates physical network equipment into an electrical
    connectivity graph and delegates generic graph algorithms to the
    Graph abstraction.

    Electrical semantics such as switch state, islands, radiality,
    and source reachability belong here.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from collections.abc import Iterable
from uuid import UUID

from src.domain.branch import Branch
from src.domain.bus import Bus
from src.domain.switch import Switch

from src.domain.network.exceptions import (
    NoPathError,
)
from src.domain.network.graph import Graph
from src.domain.network.network import Network


# ============================================================================
# Topology
# ============================================================================


class Topology:
    """
    Electrical topology view of a GridStudio Network.

    Topology does not own electrical equipment. It references a
    canonical Network and derives electrical connectivity from the
    network's current configuration.

    Architecture
    ------------
    The responsibilities are separated as follows:

        Network
            Owns physical electrical equipment.

        Topology
            Interprets electrical connectivity.

        Graph
            Performs generic graph algorithms.

    Therefore Topology decides whether a physical branch participates
    in electrical connectivity, while Graph performs traversal,
    reachability, path finding, connected-component analysis, and
    cycle detection.

    Bus-Level Topology
    ------------------
    This version operates at bus level:

        Graph[UUID]

    where each graph node represents one Bus identifier.

    Phase-aware topology may later introduce nodes such as:

        (bus_id, phase)

    without changing the canonical Network model.

    Dynamic View
    ------------
    The graph is derived from the current Network whenever requested.

    Therefore changes such as opening or closing a switch are reflected
    in subsequent topology queries without maintaining a second
    authoritative network state.
    """

    def __init__(
        self,
        network: Network,
    ) -> None:
        """
        Create an electrical topology view.

        Parameters
        ----------
        network
            Canonical GridStudio electrical network.
        """

        self._network = network

    # ------------------------------------------------------------------
    # Network Access
    # ------------------------------------------------------------------

    @property
    def network(
        self,
    ) -> Network:
        """
        Return the canonical network represented by this topology.
        """

        return self._network

    # ------------------------------------------------------------------
    # Branch Electrical Participation
    # ------------------------------------------------------------------

    def branch_is_connected(
        self,
        branch: Branch,
    ) -> bool:
        """
        Return whether a physical branch currently forms an
        electrical connection.

        A branch participates in electrical topology only when it is
        operational.

        Switches have the additional requirement that they must be
        closed.
        """

        if not branch.is_operational:
            return False

        if isinstance(
            branch,
            Switch,
        ):
            return branch.is_closed

        return True

    @property
    def connected_branches(
        self,
    ) -> tuple[Branch, ...]:
        """
        Return physical branches currently participating in
        electrical connectivity.
        """

        return tuple(
            branch
            for branch
            in self.network.branches
            if self.branch_is_connected(
                branch
            )
        )

    @property
    def disconnected_switches(
        self,
    ) -> tuple[Switch, ...]:
        """
        Return currently open switches.
        """

        return tuple(
            switch
            for switch
            in self.network.switches
            if not self.branch_is_connected(
                switch
            )
        )

    # ------------------------------------------------------------------
    # Graph Construction
    # ------------------------------------------------------------------

    def graph(
        self,
    ) -> Graph[UUID]:
        """
        Build the current bus-level electrical connectivity graph.

        Returns
        -------
        Graph[UUID]
            Undirected electrical graph whose nodes are bus IDs.

        Construction Rules
        ------------------
        1. Every Bus becomes a graph node.

        2. Every electrically connected Branch whose terminal
           references resolve to existing buses becomes a graph edge.

        3. Open switches do not become graph edges.

        4. Invalid branch references do not create phantom graph
           nodes.

        Notes
        -----
        Reference integrity should normally be checked using:

            network.validate_references()

        before simulation or strict topology validation.

        Graph construction remains defensive so inspection of a
        partially constructed Network does not silently create
        nonexistent buses.
        """

        graph: Graph[UUID] = Graph(
            nodes=(
                bus.id
                for bus
                in self.network.buses
            )
        )

        bus_ids = self.network.bus_ids

        for branch in self.connected_branches:

            from_id = branch.from_node_id
            to_id = branch.to_node_id

            if (
                from_id not in bus_ids
                or to_id not in bus_ids
            ):
                continue

            graph.add_edge(
                from_id,
                to_id,
            )

        return graph

    # ------------------------------------------------------------------
    # Bus Validation
    # ------------------------------------------------------------------

    def require_bus(
        self,
        bus_id: UUID,
    ) -> Bus:
        """
        Return a bus and require that it exists.

        ElementNotFoundError or InvalidElementTypeError is propagated
        from Network.require_as().
        """

        return self.network.require_as(
            bus_id,
            Bus,
        )

    # ------------------------------------------------------------------
    # Electrical Branch Queries
    # ------------------------------------------------------------------

    def connected_branches_at(
        self,
        bus_id: UUID,
    ) -> tuple[Branch, ...]:
        """
        Return electrically connected physical branches incident on
        a bus.

        Unlike Network.branches_at(), open switches are excluded.
        """

        self.require_bus(
            bus_id
        )

        return tuple(
            branch
            for branch
            in self.network.branches_at(
                bus_id
            )
            if self.branch_is_connected(
                branch
            )
        )

    # ------------------------------------------------------------------
    # Neighborhood
    # ------------------------------------------------------------------

    def neighbors(
        self,
        bus_id: UUID,
    ) -> frozenset[UUID]:
        """
        Return electrically adjacent buses.

        Generic neighbor lookup is delegated to Graph.
        """

        self.require_bus(
            bus_id
        )

        return self.graph().neighbors(
            bus_id
        )

    def degree(
        self,
        bus_id: UUID,
    ) -> int:
        """
        Return electrical bus degree.

        Parallel physical branches collapse into one topological
        connection because Graph represents connectivity rather than
        branch multiplicity.
        """

        self.require_bus(
            bus_id
        )

        return self.graph().degree(
            bus_id
        )

    # ------------------------------------------------------------------
    # Reachability
    # ------------------------------------------------------------------

    def reachable_bus_ids(
        self,
        start_bus_id: UUID,
    ) -> frozenset[UUID]:
        """
        Return buses electrically reachable from a starting bus.

        The starting bus is included.
        """

        self.require_bus(
            start_bus_id
        )

        return self.graph().reachable_from(
            start_bus_id
        )

    def is_reachable(
        self,
        from_bus_id: UUID,
        to_bus_id: UUID,
    ) -> bool:
        """
        Return whether two buses are electrically connected through
        the current topology.
        """

        self.require_bus(
            from_bus_id
        )
        self.require_bus(
            to_bus_id
        )

        return self.graph().is_reachable(
            from_bus_id,
            to_bus_id,
        )

    # ------------------------------------------------------------------
    # Paths
    # ------------------------------------------------------------------

    def shortest_path(
        self,
        from_bus_id: UUID,
        to_bus_id: UUID,
    ) -> tuple[UUID, ...] | None:
        """
        Return a shortest electrical bus path.

        None is returned when no electrical path exists.
        """

        self.require_bus(
            from_bus_id
        )
        self.require_bus(
            to_bus_id
        )

        return self.graph().shortest_path(
            from_bus_id,
            to_bus_id,
        )

    def require_path(
        self,
        from_bus_id: UUID,
        to_bus_id: UUID,
    ) -> tuple[UUID, ...]:
        """
        Return a shortest electrical path and require that one exists.

        Raises
        ------
        NoPathError
            If no electrical path exists between the buses.
        """

        path = self.shortest_path(
            from_bus_id,
            to_bus_id,
        )

        if path is None:
            raise NoPathError(
                source_bus_id=from_bus_id,
                target_bus_id=to_bus_id,
            )

        return path

    # ------------------------------------------------------------------
    # Connected Components / Islands
    # ------------------------------------------------------------------

    def connected_components(
        self,
    ) -> tuple[frozenset[UUID], ...]:
        """
        Return electrical connected components.

        Generic component discovery is delegated to Graph.
        """

        return (
            self.graph()
            .connected_components()
        )

    @property
    def islands(
        self,
    ) -> tuple[frozenset[UUID], ...]:
        """
        Return bus-level electrical islands.

        At this abstraction level, every connected component is an
        electrical island.

        Source/energization semantics are intentionally separate.
        """

        return self.connected_components()

    @property
    def island_count(
        self,
    ) -> int:
        """
        Return number of bus-level electrical islands.
        """

        return (
            self.graph()
            .component_count
        )

    @property
    def is_connected(
        self,
    ) -> bool:
        """
        Return whether all buses belong to one electrical component.

        An empty network is considered disconnected by Graph.
        """

        return (
            self.graph()
            .is_connected
        )

    def island_of(
        self,
        bus_id: UUID,
    ) -> frozenset[UUID]:
        """
        Return the electrical island containing a bus.
        """

        return self.reachable_bus_ids(
            bus_id
        )

    # ------------------------------------------------------------------
    # Source Reachability
    # ------------------------------------------------------------------

    def buses_reachable_from(
        self,
        source_bus_ids: Iterable[UUID],
    ) -> frozenset[UUID]:
        """
        Return buses reachable from one or more source buses.

        Parameters
        ----------
        source_bus_ids
            Buses treated by the caller as electrical sources.

        Notes
        -----
        Topology does not decide which buses are sources.

        Source identification may eventually come from:

        * external-grid models,
        * slack/reference buses,
        * grid-forming generators,
        * grid-forming batteries,
        * microgrid controllers,
        * simulation configuration.
        """

        sources = tuple(
            source_bus_ids
        )

        graph = self.graph()

        reachable: set[UUID] = set()

        for source_bus_id in sources:

            self.require_bus(
                source_bus_id
            )

            reachable.update(
                graph.reachable_from(
                    source_bus_id
                )
            )

        return frozenset(
            reachable
        )

    def unreachable_from(
        self,
        source_bus_ids: Iterable[UUID],
    ) -> frozenset[UUID]:
        """
        Return buses not electrically reachable from supplied source
        buses.
        """

        sources = tuple(
            source_bus_ids
        )

        reachable = (
            self.buses_reachable_from(
                sources
            )
        )

        return frozenset(
            self.network.bus_ids
            - reachable
        )

    # ------------------------------------------------------------------
    # Electrical Edges
    # ------------------------------------------------------------------

    @property
    def electrical_edges(
        self,
    ) -> tuple[
        tuple[UUID, UUID],
        ...,
    ]:
        """
        Return unique bus-level electrical edges.

        Parallel physical branches collapse into one graph edge.

        Open switches are excluded.
        """

        return tuple(
            (
                edge.u,
                edge.v,
            )
            for edge
            in self.graph().edges
        )

    @property
    def electrical_edge_count(
        self,
    ) -> int:
        """
        Return number of unique bus-level electrical connections.
        """

        return (
            self.graph()
            .edge_count
        )

    # ------------------------------------------------------------------
    # Cycle Detection
    # ------------------------------------------------------------------

    @property
    def has_cycles(
        self,
    ) -> bool:
        """
        Return whether the electrical topology contains a cycle.

        Generic cycle detection is delegated to Graph.
        """

        return (
            self.graph()
            .has_cycles
        )

    @property
    def is_acyclic(
        self,
    ) -> bool:
        """
        Return whether the electrical topology contains no cycles.
        """

        return (
            self.graph()
            .is_acyclic
        )

    # ------------------------------------------------------------------
    # Radial / Meshed Classification
    # ------------------------------------------------------------------

    @property
    def is_radial(
        self,
    ) -> bool:
        """
        Return whether the complete electrical network is radial.

        At bus level, a radial network is represented by a tree:

        * non-empty,
        * connected,
        * acyclic.
        """

        return (
            self.graph()
            .is_tree
        )

    @property
    def is_forest(
        self,
    ) -> bool:
        """
        Return whether every electrical component is acyclic.

        A disconnected collection of radial islands is therefore a
        forest.
        """

        return (
            self.graph()
            .is_forest
        )

    @property
    def is_meshed(
        self,
    ) -> bool:
        """
        Return whether at least one electrical cycle exists.
        """

        return self.has_cycles

    # ------------------------------------------------------------------
    # Isolated Buses
    # ------------------------------------------------------------------

    @property
    def isolated_bus_ids(
        self,
    ) -> frozenset[UUID]:
        """
        Return buses with zero electrical degree.
        """

        return (
            self.graph()
            .isolated_nodes
        )

    @property
    def has_isolated_buses(
        self,
    ) -> bool:
        """
        Return whether any electrically isolated buses exist.
        """

        return bool(
            self.isolated_bus_ids
        )

    # ------------------------------------------------------------------
    # Component-Level Queries
    # ------------------------------------------------------------------

    def component_edge_count(
        self,
        bus_ids: Iterable[UUID],
    ) -> int:
        """
        Return number of electrical edges internal to a supplied bus
        set.

        The induced-subgraph operation is delegated to Graph.
        """

        component = frozenset(
            bus_ids
        )

        graph = self.graph()

        for bus_id in component:
            self.require_bus(
                bus_id
            )

        return (
            graph
            .subgraph(component)
            .edge_count
        )

    def component_is_radial(
        self,
        bus_ids: Iterable[UUID],
    ) -> bool:
        """
        Return whether a supplied bus set forms a radial connected
        component.

        A radial component is represented by a tree.
        """

        component = frozenset(
            bus_ids
        )

        if not component:
            return False

        graph = self.graph()

        for bus_id in component:
            self.require_bus(
                bus_id
            )

        return (
            graph
            .subgraph(component)
            .is_tree
        )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Topology",
]