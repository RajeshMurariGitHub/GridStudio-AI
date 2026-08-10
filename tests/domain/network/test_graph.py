"""
GridStudio AI

Tests:
    test_graph.py

Description:
    Unit tests for the generic Graph abstraction.

    These tests deliberately contain no electrical-domain objects.
    They prove the behavior of the generic graph layer independently
    from Network and Topology.

License:
    MIT
"""

from __future__ import annotations

import pytest

from src.domain.network import Edge, Graph


# ============================================================================
# Construction
# ============================================================================


def test_empty_graph() -> None:
    graph: Graph[int] = Graph()

    assert len(graph) == 0
    assert graph.node_count == 0
    assert graph.edge_count == 0
    assert graph.nodes == frozenset()
    assert graph.edges == ()
    assert not graph
    assert graph.component_count == 0
    assert graph.is_connected is False
    assert graph.is_tree is False
    assert graph.is_forest is True
    assert graph.has_cycles is False
    assert graph.is_acyclic is True


def test_graph_constructed_with_nodes() -> None:
    graph = Graph(nodes=[1, 2, 3])

    assert graph.node_count == 3
    assert graph.nodes == frozenset({1, 2, 3})
    assert graph.edge_count == 0


def test_graph_constructed_with_edges() -> None:
    graph = Graph(
        edges=[
            (1, 2),
            (2, 3),
        ]
    )

    assert graph.nodes == frozenset({1, 2, 3})
    assert graph.edge_count == 2
    assert graph.has_edge(1, 2)
    assert graph.has_edge(2, 1)
    assert graph.has_edge(2, 3)


def test_graph_accepts_edge_objects() -> None:
    graph = Graph(
        edges=[
            Edge(1, 2),
            Edge(2, 3),
        ]
    )

    assert graph.edge_count == 2
    assert graph.is_connected is True


# ============================================================================
# Node Management
# ============================================================================


def test_add_node() -> None:
    graph: Graph[str] = Graph()

    graph.add_node("A")

    assert "A" in graph
    assert graph.node_count == 1


def test_add_existing_node_is_idempotent() -> None:
    graph = Graph(nodes=[1])

    graph.add_node(1)
    graph.add_node(1)

    assert graph.node_count == 1


def test_add_nodes() -> None:
    graph: Graph[int] = Graph()

    graph.add_nodes([1, 2, 3])

    assert graph.nodes == frozenset({1, 2, 3})


def test_remove_node_removes_incident_edges() -> None:
    graph = Graph(
        edges=[
            (1, 2),
            (2, 3),
        ]
    )

    graph.remove_node(2)

    assert graph.nodes == frozenset({1, 3})
    assert graph.edge_count == 0
    assert graph.neighbors(1) == frozenset()
    assert graph.neighbors(3) == frozenset()


def test_remove_missing_node_raises_key_error() -> None:
    graph = Graph(nodes=[1])

    with pytest.raises(KeyError):
        graph.remove_node(99)


def test_clear_graph() -> None:
    graph = Graph(
        edges=[
            (1, 2),
            (2, 3),
        ]
    )

    graph.clear()

    assert graph.node_count == 0
    assert graph.edge_count == 0


# ============================================================================
# Edge Management
# ============================================================================


def test_add_edge_adds_missing_nodes() -> None:
    graph: Graph[int] = Graph()

    graph.add_edge(1, 2)

    assert graph.nodes == frozenset({1, 2})
    assert graph.edge_count == 1


def test_edges_are_undirected() -> None:
    graph = Graph(edges=[(1, 2)])

    assert graph.has_edge(1, 2)
    assert graph.has_edge(2, 1)

    assert graph.neighbors(1) == frozenset({2})
    assert graph.neighbors(2) == frozenset({1})


def test_duplicate_edge_is_idempotent() -> None:
    graph: Graph[int] = Graph()

    graph.add_edge(1, 2)
    graph.add_edge(1, 2)
    graph.add_edge(2, 1)

    assert graph.edge_count == 1


def test_remove_edge() -> None:
    graph = Graph(edges=[(1, 2)])

    graph.remove_edge(1, 2)

    assert graph.edge_count == 0
    assert graph.has_edge(1, 2) is False
    assert graph.has_edge(2, 1) is False


def test_remove_missing_edge_raises_key_error() -> None:
    graph = Graph(nodes=[1, 2])

    with pytest.raises(KeyError):
        graph.remove_edge(1, 2)


# ============================================================================
# Neighborhood
# ============================================================================


def test_neighbors() -> None:
    graph = Graph(
        edges=[
            (1, 2),
            (1, 3),
        ]
    )

    assert graph.neighbors(1) == frozenset({2, 3})


def test_degree() -> None:
    graph = Graph(
        edges=[
            (1, 2),
            (1, 3),
        ]
    )

    assert graph.degree(1) == 2
    assert graph.degree(2) == 1


def test_neighbors_missing_node_raises_key_error() -> None:
    graph = Graph(nodes=[1])

    with pytest.raises(KeyError):
        graph.neighbors(99)


def test_isolated_nodes() -> None:
    graph = Graph(
        nodes=[1, 2, 3],
        edges=[(1, 2)],
    )

    assert graph.isolated_nodes == frozenset({3})


# ============================================================================
# Reachability
# ============================================================================


def test_reachable_from_chain() -> None:
    graph = Graph(
        edges=[
            (1, 2),
            (2, 3),
            (3, 4),
        ]
    )

    assert graph.reachable_from(1) == frozenset(
        {1, 2, 3, 4}
    )


def test_reachable_from_does_not_cross_components() -> None:
    graph = Graph(
        nodes=[1, 2, 3, 4],
        edges=[
            (1, 2),
            (3, 4),
        ],
    )

    assert graph.reachable_from(1) == frozenset({1, 2})


def test_node_is_reachable_from_itself() -> None:
    graph = Graph(nodes=[1])

    assert graph.is_reachable(1, 1) is True


def test_unreachable_nodes() -> None:
    graph = Graph(
        nodes=[1, 2, 3],
        edges=[(1, 2)],
    )

    assert graph.is_reachable(1, 3) is False


# ============================================================================
# Shortest Path
# ============================================================================


def test_shortest_path_chain() -> None:
    graph = Graph(
        edges=[
            (1, 2),
            (2, 3),
            (3, 4),
        ]
    )

    assert graph.shortest_path(1, 4) == (
        1,
        2,
        3,
        4,
    )


def test_shortest_path_prefers_fewer_edges() -> None:
    graph = Graph(
        edges=[
            (1, 2),
            (2, 3),
            (3, 4),
            (1, 4),
        ]
    )

    assert graph.shortest_path(1, 4) == (
        1,
        4,
    )


def test_shortest_path_same_node() -> None:
    graph = Graph(nodes=[1])

    assert graph.shortest_path(1, 1) == (1,)


def test_shortest_path_returns_none_when_disconnected() -> None:
    graph = Graph(
        nodes=[1, 2, 3],
        edges=[(1, 2)],
    )

    assert graph.shortest_path(1, 3) is None


# ============================================================================
# Connected Components
# ============================================================================


def test_connected_components() -> None:
    graph = Graph(
        nodes=[1, 2, 3, 4, 5],
        edges=[
            (1, 2),
            (2, 3),
            (4, 5),
        ],
    )

    components = set(
        graph.connected_components()
    )

    assert components == {
        frozenset({1, 2, 3}),
        frozenset({4, 5}),
    }


def test_isolated_node_is_component() -> None:
    graph = Graph(
        nodes=[1, 2, 3],
        edges=[(1, 2)],
    )

    components = set(
        graph.connected_components()
    )

    assert components == {
        frozenset({1, 2}),
        frozenset({3}),
    }


def test_component_count() -> None:
    graph = Graph(
        nodes=[1, 2, 3, 4],
        edges=[
            (1, 2),
            (3, 4),
        ],
    )

    assert graph.component_count == 2


# ============================================================================
# Connectivity
# ============================================================================


def test_single_node_graph_is_connected() -> None:
    graph = Graph(nodes=[1])

    assert graph.is_connected is True


def test_chain_is_connected() -> None:
    graph = Graph(
        edges=[
            (1, 2),
            (2, 3),
        ]
    )

    assert graph.is_connected is True


def test_disconnected_graph_is_not_connected() -> None:
    graph = Graph(
        nodes=[1, 2, 3],
        edges=[(1, 2)],
    )

    assert graph.is_connected is False


# ============================================================================
# Cycle Detection
# ============================================================================


def test_chain_has_no_cycle() -> None:
    graph = Graph(
        edges=[
            (1, 2),
            (2, 3),
            (3, 4),
        ]
    )

    assert graph.has_cycles is False
    assert graph.is_acyclic is True


def test_triangle_has_cycle() -> None:
    graph = Graph(
        edges=[
            (1, 2),
            (2, 3),
            (3, 1),
        ]
    )

    assert graph.has_cycles is True
    assert graph.is_acyclic is False


def test_square_has_cycle() -> None:
    graph = Graph(
        edges=[
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 1),
        ]
    )

    assert graph.has_cycles is True


def test_cycle_in_one_component_is_detected() -> None:
    graph = Graph(
        nodes=[1, 2, 3, 4, 5],
        edges=[
            (1, 2),
            (2, 3),
            (3, 1),
            (4, 5),
        ],
    )

    assert graph.has_cycles is True


def test_self_loop_is_cycle() -> None:
    graph: Graph[int] = Graph()

    graph.add_edge(1, 1)

    assert graph.edge_count == 1
    assert graph.has_cycles is True
    assert graph.is_acyclic is False


# ============================================================================
# Tree / Forest
# ============================================================================


def test_single_node_is_tree() -> None:
    graph = Graph(nodes=[1])

    assert graph.is_tree is True
    assert graph.is_forest is True


def test_chain_is_tree() -> None:
    graph = Graph(
        edges=[
            (1, 2),
            (2, 3),
            (3, 4),
        ]
    )

    assert graph.is_tree is True
    assert graph.is_forest is True


def test_cycle_is_not_tree_or_forest() -> None:
    graph = Graph(
        edges=[
            (1, 2),
            (2, 3),
            (3, 1),
        ]
    )

    assert graph.is_tree is False
    assert graph.is_forest is False


def test_disconnected_acyclic_graph_is_forest_not_tree() -> None:
    graph = Graph(
        edges=[
            (1, 2),
            (3, 4),
        ]
    )

    assert graph.is_connected is False
    assert graph.is_tree is False
    assert graph.is_forest is True


# ============================================================================
# Subgraphs
# ============================================================================


def test_induced_subgraph() -> None:
    graph = Graph(
        edges=[
            (1, 2),
            (2, 3),
            (3, 4),
            (1, 4),
        ]
    )

    subgraph = graph.subgraph(
        {1, 2, 3}
    )

    assert subgraph.nodes == frozenset(
        {1, 2, 3}
    )

    assert subgraph.edge_count == 2

    assert subgraph.has_edge(1, 2)
    assert subgraph.has_edge(2, 3)
    assert subgraph.has_edge(1, 3) is False


def test_subgraph_rejects_unknown_node() -> None:
    graph = Graph(nodes=[1, 2])

    with pytest.raises(KeyError):
        graph.subgraph({1, 99})


# ============================================================================
# Copy
# ============================================================================


def test_copy_is_independent() -> None:
    original = Graph(
        edges=[
            (1, 2),
            (2, 3),
        ]
    )

    copied = original.copy()

    copied.add_edge(3, 4)

    assert 4 not in original
    assert 4 in copied

    assert original.edge_count == 2
    assert copied.edge_count == 3


# ============================================================================
# Adjacency Snapshot
# ============================================================================


def test_adjacency_returns_snapshot() -> None:
    graph = Graph(
        edges=[
            (1, 2),
            (1, 3),
        ]
    )

    adjacency = graph.adjacency

    assert adjacency[1] == frozenset({2, 3})

    # Returned values are immutable snapshots.
    assert isinstance(
        adjacency[1],
        frozenset,
    )


# ============================================================================
# Generic Node Types
# ============================================================================


def test_graph_supports_string_nodes() -> None:
    graph = Graph(
        edges=[
            ("A", "B"),
            ("B", "C"),
        ]
    )

    assert graph.shortest_path(
        "A",
        "C",
    ) == (
        "A",
        "B",
        "C",
    )


def test_graph_does_not_require_orderable_nodes() -> None:
    class Node:
        pass

    a = Node()
    b = Node()
    c = Node()

    graph = Graph(
        edges=[
            (a, b),
            (b, c),
        ]
    )

    # Accessing edges must not require:
    #
    #     a < b
    #
    # Generic graph nodes need only be hashable.
    edges = graph.edges

    assert len(edges) == 2
    assert graph.is_tree is True