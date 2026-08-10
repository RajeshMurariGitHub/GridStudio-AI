"""
GridStudio AI

Module:
    graph.py

Description:
    Defines lightweight, generic, dependency-free graph primitives
    used by GridStudio AI.

    Graph contains no electrical-domain semantics. It provides
    reusable undirected graph structure and algorithms for topology,
    dependency analysis, connectivity analysis, and future services.

    Electrical interpretation belongs to:

        src.domain.network.topology

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Generic, TypeVar


# ============================================================================
# Type Variables
# ============================================================================


NodeT = TypeVar(
    "NodeT",
    bound=object,
)


# ============================================================================
# Edge
# ============================================================================


@dataclass(
    frozen=True,
    slots=True,
)
class Edge(Generic[NodeT]):
    """
    Undirected graph edge.

    Parameters
    ----------
    u
        First endpoint.

    v
        Second endpoint.

    Notes
    -----
    Edge endpoint order is not intended to carry direction.

    Graph itself enforces undirected connectivity and prevents
    duplicate logical edges.
    """

    u: NodeT
    v: NodeT

    def __iter__(
        self,
    ) -> Iterator[NodeT]:
        """
        Iterate over edge endpoints.
        """

        yield self.u
        yield self.v


# ============================================================================
# Graph
# ============================================================================


class Graph(Generic[NodeT]):
    """
    Lightweight undirected graph.

    Graph is intentionally independent of electrical-domain models.

    It knows nothing about:

    * buses,
    * lines,
    * transformers,
    * switches,
    * phases,
    * voltage,
    * power flow,
    * pandapower,
    * OpenDSS.

    Those semantics belong to higher-level GridStudio layers.

    Internal Representation
    -----------------------
    The graph uses an adjacency mapping:

        node -> set(neighbors)

    This provides efficient lookup for common topology operations.

    Parallel Edges
    --------------
    Parallel edges are collapsed into a single logical graph edge.

    For example:

        A -- Line 1 -- B
        A -- Line 2 -- B

    becomes:

        A ----------- B

    at the graph-connectivity level.

    Physical branch multiplicity remains available in Network.

    Self-Loops
    ----------
    Self-loops are representable by this generic graph.

    Whether a self-loop is valid in an electrical network is a
    domain-integrity decision and therefore belongs outside Graph.
    """

    def __init__(
        self,
        *,
        nodes: Iterable[NodeT] | None = None,
        edges: Iterable[
            Edge[NodeT]
            | tuple[NodeT, NodeT]
        ]
        | None = None,
    ) -> None:
        """
        Create an undirected graph.

        Parameters
        ----------
        nodes
            Optional initial nodes.

        edges
            Optional initial edges. Edge endpoints are automatically
            added as graph nodes.
        """

        self._adjacency: dict[
            NodeT,
            set[NodeT],
        ] = {}

        if nodes is not None:
            self.add_nodes(
                nodes
            )

        if edges is not None:
            self.add_edges(
                edges
            )

    # ------------------------------------------------------------------
    # Python Container Protocol
    # ------------------------------------------------------------------

    def __len__(
        self,
    ) -> int:
        """
        Return number of graph nodes.
        """

        return len(
            self._adjacency
        )

    def __iter__(
        self,
    ) -> Iterator[NodeT]:
        """
        Iterate over graph nodes.
        """

        return iter(
            self._adjacency
        )

    def __contains__(
        self,
        node: object,
    ) -> bool:
        """
        Return whether a node exists.
        """

        return (
            node
            in self._adjacency
        )

    def __bool__(
        self,
    ) -> bool:
        """
        Return whether the graph contains at least one node.
        """

        return bool(
            self._adjacency
        )

    # ------------------------------------------------------------------
    # Basic Views
    # ------------------------------------------------------------------

    @property
    def nodes(
        self,
    ) -> frozenset[NodeT]:
        """
        Return graph nodes.
        """

        return frozenset(
            self._adjacency
        )

    @property
    def node_count(
        self,
    ) -> int:
        """
        Return number of graph nodes.
        """

        return len(
            self._adjacency
        )

    @property
    def edges(
        self,
    ) -> tuple[Edge[NodeT], ...]:
        """
        Return unique undirected graph edges.

        Notes
        -----
        No ordering relationship between generic node values is
        assumed.

        Edge uniqueness is determined using endpoint frozensets,
        allowing Graph to support arbitrary hashable node objects.
        """

        result: list[
            Edge[NodeT]
        ] = []

        seen: set[
            frozenset[NodeT]
        ] = set()

        for u, neighbors in (
            self._adjacency.items()
        ):

            for v in neighbors:

                key = frozenset(
                    (u, v)
                )

                if key in seen:
                    continue

                seen.add(
                    key
                )

                result.append(
                    Edge(
                        u=u,
                        v=v,
                    )
                )

        return tuple(
            result
        )

    @property
    def edge_count(
        self,
    ) -> int:
        """
        Return number of unique undirected graph edges.

        Self-loops count as one edge.
        """

        return len(
            self.edges
        )

    @property
    def adjacency(
        self,
    ) -> dict[
        NodeT,
        frozenset[NodeT],
    ]:
        """
        Return a read-only-style snapshot of adjacency.

        The returned mapping and neighbor collections are detached
        from the graph's internal mutable sets.
        """

        return {
            node: frozenset(
                neighbors
            )
            for node, neighbors
            in self._adjacency.items()
        }

    # ------------------------------------------------------------------
    # Node Management
    # ------------------------------------------------------------------

    def add_node(
        self,
        node: NodeT,
    ) -> None:
        """
        Add a node.

        Adding an existing node is idempotent.
        """

        self._adjacency.setdefault(
            node,
            set(),
        )

    def add_nodes(
        self,
        nodes: Iterable[NodeT],
    ) -> None:
        """
        Add multiple nodes.
        """

        for node in nodes:
            self.add_node(
                node
            )

    def remove_node(
        self,
        node: NodeT,
    ) -> None:
        """
        Remove a node and all incident edges.

        Raises
        ------
        KeyError
            If the node does not exist.

        Notes
        -----
        Graph deliberately uses standard Python exceptions.

        Domain-specific exceptions belong to higher layers such as
        Network and Topology.
        """

        self._require_node(
            node
        )

        neighbors = tuple(
            self._adjacency[node]
        )

        for neighbor in neighbors:

            if neighbor == node:
                continue

            self._adjacency[
                neighbor
            ].discard(
                node
            )

        del self._adjacency[
            node
        ]

    def clear(
        self,
    ) -> None:
        """
        Remove all nodes and edges.
        """

        self._adjacency.clear()

    # ------------------------------------------------------------------
    # Edge Management
    # ------------------------------------------------------------------

    def add_edge(
        self,
        u: NodeT,
        v: NodeT,
    ) -> None:
        """
        Add an undirected edge.

        Missing endpoint nodes are created automatically.

        Adding an existing edge is idempotent.
        """

        self.add_node(
            u
        )
        self.add_node(
            v
        )

        self._adjacency[
            u
        ].add(
            v
        )

        self._adjacency[
            v
        ].add(
            u
        )

    def add_edges(
        self,
        edges: Iterable[
            Edge[NodeT]
            | tuple[NodeT, NodeT]
        ],
    ) -> None:
        """
        Add multiple undirected edges.
        """

        for edge in edges:

            if isinstance(
                edge,
                Edge,
            ):
                u = edge.u
                v = edge.v
            else:
                u, v = edge

            self.add_edge(
                u,
                v,
            )

    def remove_edge(
        self,
        u: NodeT,
        v: NodeT,
    ) -> None:
        """
        Remove an undirected edge.

        Raises
        ------
        KeyError
            If either endpoint or the edge does not exist.
        """

        self._require_node(
            u
        )
        self._require_node(
            v
        )

        if (
            v
            not in self._adjacency[u]
        ):
            raise KeyError(
                f"Graph edge "
                f"({u!r}, {v!r}) "
                "does not exist."
            )

        self._adjacency[
            u
        ].remove(
            v
        )

        if u != v:
            self._adjacency[
                v
            ].remove(
                u
            )

    def has_edge(
        self,
        u: NodeT,
        v: NodeT,
    ) -> bool:
        """
        Return whether an undirected edge exists.
        """

        return (
            u in self._adjacency
            and v
            in self._adjacency[u]
        )

    # ------------------------------------------------------------------
    # Neighborhood
    # ------------------------------------------------------------------

    def neighbors(
        self,
        node: NodeT,
    ) -> frozenset[NodeT]:
        """
        Return direct neighbors of a node.

        Raises
        ------
        KeyError
            If the node does not exist.
        """

        self._require_node(
            node
        )

        return frozenset(
            self._adjacency[node]
        )

    def degree(
        self,
        node: NodeT,
    ) -> int:
        """
        Return node degree.

        For a self-loop, the loop contributes one adjacency entry.

        This graph abstraction uses adjacency cardinality rather than
        graph-theory multigraph degree conventions.
        """

        self._require_node(
            node
        )

        return len(
            self._adjacency[node]
        )

    @property
    def isolated_nodes(
        self,
    ) -> frozenset[NodeT]:
        """
        Return nodes having zero neighbors.
        """

        return frozenset(
            node
            for node, neighbors
            in self._adjacency.items()
            if not neighbors
        )

    # ------------------------------------------------------------------
    # Reachability
    # ------------------------------------------------------------------

    def reachable_from(
        self,
        start: NodeT,
    ) -> frozenset[NodeT]:
        """
        Return all nodes reachable from ``start``.

        Breadth-first search is used.

        The starting node is included.
        """

        self._require_node(
            start
        )

        visited: set[NodeT] = {
            start
        }

        queue: deque[NodeT] = deque(
            [start]
        )

        while queue:

            node = queue.popleft()

            for neighbor in (
                self._adjacency[node]
            ):

                if neighbor in visited:
                    continue

                visited.add(
                    neighbor
                )

                queue.append(
                    neighbor
                )

        return frozenset(
            visited
        )

    def is_reachable(
        self,
        source: NodeT,
        target: NodeT,
    ) -> bool:
        """
        Return whether ``target`` is reachable from ``source``.

        Raises
        ------
        KeyError
            If either node does not exist.
        """

        self._require_node(
            source
        )
        self._require_node(
            target
        )

        if source == target:
            return True

        visited: set[NodeT] = {
            source
        }

        queue: deque[NodeT] = deque(
            [source]
        )

        while queue:

            node = queue.popleft()

            for neighbor in (
                self._adjacency[node]
            ):

                if neighbor == target:
                    return True

                if neighbor in visited:
                    continue

                visited.add(
                    neighbor
                )

                queue.append(
                    neighbor
                )

        return False

    # ------------------------------------------------------------------
    # Shortest Path
    # ------------------------------------------------------------------

    def shortest_path(
        self,
        source: NodeT,
        target: NodeT,
    ) -> tuple[NodeT, ...] | None:
        """
        Return an unweighted shortest path.

        Breadth-first search is used.

        Returns
        -------
        tuple | None
            Node sequence from source to target, inclusive.

            None is returned when no path exists.

        Raises
        ------
        KeyError
            If either endpoint does not exist.
        """

        self._require_node(
            source
        )
        self._require_node(
            target
        )

        if source == target:
            return (
                source,
            )

        parents: dict[
            NodeT,
            NodeT | None,
        ] = {
            source: None
        }

        queue: deque[NodeT] = deque(
            [source]
        )

        while queue:

            node = queue.popleft()

            for neighbor in (
                self._adjacency[node]
            ):

                if neighbor in parents:
                    continue

                parents[
                    neighbor
                ] = node

                if neighbor == target:
                    return self._reconstruct_path(
                        parents=parents,
                        target=target,
                    )

                queue.append(
                    neighbor
                )

        return None

    # ------------------------------------------------------------------
    # Connected Components
    # ------------------------------------------------------------------

    def connected_components(
        self,
    ) -> tuple[
        frozenset[NodeT],
        ...,
    ]:
        """
        Return connected components.

        Every isolated node forms a one-node component.

        An empty graph has zero components.
        """

        components: list[
            frozenset[NodeT]
        ] = []

        unvisited: set[NodeT] = set(
            self._adjacency
        )

        while unvisited:

            start = next(
                iter(unvisited)
            )

            component = (
                self.reachable_from(
                    start
                )
            )

            components.append(
                component
            )

            unvisited.difference_update(
                component
            )

        return tuple(
            components
        )

    @property
    def component_count(
        self,
    ) -> int:
        """
        Return number of connected components.
        """

        return len(
            self.connected_components()
        )

    @property
    def is_connected(
        self,
    ) -> bool:
        """
        Return whether the graph is connected.

        Empty-graph Semantics
        ---------------------
        An empty graph is considered not connected.

        A one-node graph is connected.
        """

        if not self._adjacency:
            return False

        start = next(
            iter(self._adjacency)
        )

        return (
            len(
                self.reachable_from(
                    start
                )
            )
            == self.node_count
        )

    # ------------------------------------------------------------------
    # Cycle Detection
    # ------------------------------------------------------------------

    @property
    def has_cycles(
        self,
    ) -> bool:
        """
        Return whether the undirected graph contains a cycle.

        The algorithm checks each connected component using
        depth-first traversal.

        A self-loop is considered a cycle.
        """

        visited: set[NodeT] = set()

        for start in self._adjacency:

            if start in visited:
                continue

            if self._component_has_cycle(
                start=start,
                visited=visited,
            ):
                return True

        return False

    @property
    def is_acyclic(
        self,
    ) -> bool:
        """
        Return whether the graph contains no cycles.
        """

        return not self.has_cycles

    @property
    def is_tree(
        self,
    ) -> bool:
        """
        Return whether the graph is a tree.

        A tree is:

        * non-empty,
        * connected,
        * acyclic.

        Therefore a single isolated node is a valid tree.
        """

        return (
            bool(self)
            and self.is_connected
            and self.is_acyclic
        )

    @property
    def is_forest(
        self,
    ) -> bool:
        """
        Return whether the graph is a forest.

        A forest is an acyclic graph and may be disconnected.

        The empty graph is considered a forest.
        """

        return self.is_acyclic

    # ------------------------------------------------------------------
    # Subgraphs
    # ------------------------------------------------------------------

    def subgraph(
        self,
        nodes: Iterable[NodeT],
    ) -> "Graph[NodeT]":
        """
        Return the induced subgraph over supplied nodes.

        Raises
        ------
        KeyError
            If any supplied node does not exist in this graph.
        """

        selected = frozenset(
            nodes
        )

        for node in selected:
            self._require_node(
                node
            )

        result: Graph[NodeT] = Graph(
            nodes=selected
        )

        for edge in self.edges:

            if (
                edge.u in selected
                and edge.v in selected
            ):
                result.add_edge(
                    edge.u,
                    edge.v,
                )

        return result

    # ------------------------------------------------------------------
    # Copy
    # ------------------------------------------------------------------

    def copy(
        self,
    ) -> "Graph[NodeT]":
        """
        Return an independent shallow graph copy.

        Node objects themselves are not deep-copied.
        """

        return Graph(
            nodes=self.nodes,
            edges=self.edges,
        )

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _require_node(
        self,
        node: NodeT,
    ) -> None:
        """
        Require that a node exists.
        """

        if node not in self._adjacency:
            raise KeyError(
                f"Graph node "
                f"{node!r} "
                "does not exist."
            )

    @staticmethod
    def _reconstruct_path(
        *,
        parents: dict[
            NodeT,
            NodeT | None,
        ],
        target: NodeT,
    ) -> tuple[NodeT, ...]:
        """
        Reconstruct a path from a BFS parent mapping.
        """

        path: list[NodeT] = []

        current: NodeT | None = target

        while current is not None:

            path.append(
                current
            )

            current = parents[
                current
            ]

        path.reverse()

        return tuple(
            path
        )

    def _component_has_cycle(
        self,
        *,
        start: NodeT,
        visited: set[NodeT],
    ) -> bool:
        """
        Return whether a connected component contains a cycle.

        Uses iterative depth-first traversal.
        """

        stack: list[
            tuple[
                NodeT,
                NodeT | None,
            ]
        ] = [
            (
                start,
                None,
            )
        ]

        while stack:

            node, parent = (
                stack.pop()
            )

            if node in visited:
                continue

            visited.add(
                node
            )

            for neighbor in (
                self._adjacency[node]
            ):

                # A self-loop is a cycle.
                if neighbor == node:
                    return True

                if neighbor not in visited:

                    stack.append(
                        (
                            neighbor,
                            node,
                        )
                    )

                    continue

                # In an undirected graph, encountering an already
                # visited neighbor other than the parent indicates
                # a cycle.
                if neighbor != parent:
                    return True

        return False


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Edge",
    "Graph",
]