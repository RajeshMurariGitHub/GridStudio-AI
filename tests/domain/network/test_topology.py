"""
GridStudio AI

Tests:
    test_topology.py

Description:
    Integration and regression tests for the canonical GridStudio
    electrical topology architecture.

    The architecture under test is:

        Network -> Topology -> Graph

    Responsibilities
    ----------------
    Network
        Owns the canonical physical electrical equipment registry.

    Topology
        Interprets the current electrical connectivity of the
        canonical Network.

    Graph
        Provides generic graph algorithms such as connectivity,
        reachability, shortest paths, connected components,
        cycle detection, and tree/forest classification.

    Important domain semantics
    --------------------------
    Physical membership and electrical connectivity are intentionally
    different concepts.

    A branch may physically exist in Network while not participating
    in the current electrical topology.

    A branch participates electrically only when it is operational.

    A Switch has the additional requirement that it must be closed.

    Domain objects are immutable. Operational changes are represented
    by replacing the canonical Network element with another immutable
    instance having the same identity.

License:
    MIT
"""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

import pytest

from src.core.enums import (
    AssetStatus,
    AvailabilityState,
)

from src.domain.bus import Bus
from src.domain.line import Line
from src.domain.switch import Switch

from src.domain.electrical.line_parameters import LineParameters

from src.domain.network import (
    ElementNotFoundError,
    Network,
    NoPathError,
    Topology,
)


# ============================================================================
# Helpers
# ============================================================================


def make_bus(
    name: str,
    *,
    nominal_voltage_kv: float = 11.0,
) -> Bus:
    """
    Construct a minimal valid Bus for topology tests.
    """

    return Bus(
        id=uuid4(),
        name=name,
        nominal_voltage_kv=nominal_voltage_kv,
    )


def make_switch(
    name: str,
    from_bus: Bus,
    to_bus: Bus,
    *,
    is_closed: bool = True,
    enabled: bool = True,
    status: AssetStatus = AssetStatus.IN_SERVICE,
    availability: AvailabilityState = AvailabilityState.AVAILABLE,
) -> Switch:
    """
    Construct a valid Switch between two buses.
    """

    return Switch(
        id=uuid4(),
        name=name,
        from_node_id=from_bus.id,
        to_node_id=to_bus.id,
        enabled=enabled,
        status=status,
        availability=availability,
        is_closed=is_closed,
    )


def make_line(
    name: str,
    from_bus: Bus,
    to_bus: Bus,
    *,
    enabled: bool = True,
    status: AssetStatus = AssetStatus.IN_SERVICE,
    availability: AvailabilityState = AvailabilityState.AVAILABLE,
    length_km: float = 1.0,
) -> Line:
    """
    Construct a minimal valid Line for topology tests.

    The electrical values are deliberately simple because these tests
    verify connectivity semantics rather than power-flow calculations.
    """

    parameters = LineParameters(
        r1_ohm_per_km=0.1,
        x1_ohm_per_km=0.2,
    )

    return Line(
        id=uuid4(),
        name=name,
        from_node_id=from_bus.id,
        to_node_id=to_bus.id,
        enabled=enabled,
        status=status,
        availability=availability,
        length_km=length_km,
        parameters=parameters,
    )


def add_all(
    network: Network,
    *elements: Any,
) -> None:
    """
    Add multiple canonical domain elements to a Network.
    """

    for element in elements:
        network.add(element)


def replace_element(
    network: Network,
    old_element: Any,
    new_element: Any,
) -> None:
    """
    Replace an immutable canonical Network element.

    The replacement normally preserves the same UUID so that the
    physical identity remains stable while operational state changes.
    """

    assert old_element.id == new_element.id

    network.remove(
        old_element.id
    )

    network.add(
        new_element
    )


def component_set(
    components: tuple[
        frozenset[UUID],
        ...,
    ],
) -> set[frozenset[UUID]]:
    """
    Convert connected components to an order-independent representation.
    """

    return set(
        components
    )


def build_chain_network(
    *,
    middle_switch_closed: bool = True,
) -> tuple[
    Network,
    Topology,
    Bus,
    Bus,
    Bus,
    Bus,
    Switch,
    Switch,
    Switch,
]:
    """
    Construct the canonical four-bus test network.

        Bus 1 -- S12 -- Bus 2 -- S23 -- Bus 3 -- S34 -- Bus 4

    Opening S23 splits the system into two islands:

        {Bus 1, Bus 2}

        {Bus 3, Bus 4}
    """

    network = Network(
        name="Four Bus Test Network"
    )

    bus_1 = make_bus("Bus 1")
    bus_2 = make_bus("Bus 2")
    bus_3 = make_bus("Bus 3")
    bus_4 = make_bus("Bus 4")

    switch_12 = make_switch(
        "Switch 1-2",
        bus_1,
        bus_2,
    )

    switch_23 = make_switch(
        "Switch 2-3",
        bus_2,
        bus_3,
        is_closed=middle_switch_closed,
    )

    switch_34 = make_switch(
        "Switch 3-4",
        bus_3,
        bus_4,
    )

    add_all(
        network,
        bus_1,
        bus_2,
        bus_3,
        bus_4,
        switch_12,
        switch_23,
        switch_34,
    )

    topology = Topology(
        network
    )

    return (
        network,
        topology,
        bus_1,
        bus_2,
        bus_3,
        bus_4,
        switch_12,
        switch_23,
        switch_34,
    )


# ============================================================================
# Empty Network
# ============================================================================


def test_empty_network_topology() -> None:
    network = Network(
        name="Empty Network"
    )

    topology = Topology(
        network
    )

    graph = topology.graph()

    assert graph.node_count == 0
    assert graph.edge_count == 0

    assert topology.island_count == 0
    assert topology.is_connected is False

    assert topology.has_cycles is False
    assert topology.is_acyclic is True

    assert topology.is_radial is False
    assert topology.is_forest is True
    assert topology.is_meshed is False

    assert topology.isolated_bus_ids == frozenset()


# ============================================================================
# Canonical Network Reference
# ============================================================================


def test_topology_references_canonical_network() -> None:
    network = Network(
        name="Test Network"
    )

    topology = Topology(
        network
    )

    assert topology.network is network


# ============================================================================
# Graph Construction
# ============================================================================


def test_graph_contains_all_network_buses() -> None:
    (
        network,
        topology,
        bus_1,
        bus_2,
        bus_3,
        bus_4,
        _,
        _,
        _,
    ) = build_chain_network()

    graph = topology.graph()

    assert graph.nodes == frozenset(
        {
            bus_1.id,
            bus_2.id,
            bus_3.id,
            bus_4.id,
        }
    )

    assert graph.node_count == network.bus_count


def test_closed_switches_create_electrical_edges() -> None:
    (
        _,
        topology,
        bus_1,
        bus_2,
        bus_3,
        bus_4,
        _,
        _,
        _,
    ) = build_chain_network()

    graph = topology.graph()

    assert graph.has_edge(
        bus_1.id,
        bus_2.id,
    )

    assert graph.has_edge(
        bus_2.id,
        bus_3.id,
    )

    assert graph.has_edge(
        bus_3.id,
        bus_4.id,
    )

    assert topology.electrical_edge_count == 3


def test_open_switch_does_not_create_electrical_edge() -> None:
    (
        _,
        topology,
        bus_1,
        bus_2,
        bus_3,
        bus_4,
        _,
        _,
        _,
    ) = build_chain_network(
        middle_switch_closed=False
    )

    graph = topology.graph()

    assert graph.has_edge(
        bus_1.id,
        bus_2.id,
    )

    assert graph.has_edge(
        bus_2.id,
        bus_3.id,
    ) is False

    assert graph.has_edge(
        bus_3.id,
        bus_4.id,
    )

    assert topology.electrical_edge_count == 2


# ============================================================================
# Physical Network vs Electrical Topology
# ============================================================================


def test_open_switch_remains_in_physical_network() -> None:
    (
        network,
        topology,
        _,
        _,
        _,
        _,
        _,
        switch_23,
        _,
    ) = build_chain_network(
        middle_switch_closed=False
    )

    assert network.branch_count == 3
    assert len(network.switches) == 3

    assert switch_23 in network.switches

    assert switch_23 in topology.disconnected_switches
    assert switch_23 not in topology.connected_branches


def test_closed_switch_is_connected_branch() -> None:
    (
        _,
        topology,
        _,
        _,
        _,
        _,
        _,
        switch_23,
        _,
    ) = build_chain_network()

    assert switch_23 in topology.connected_branches
    assert switch_23 not in topology.disconnected_switches


def test_network_branches_at_includes_open_switch() -> None:
    (
        network,
        topology,
        _,
        bus_2,
        _,
        _,
        _,
        switch_23,
        _,
    ) = build_chain_network(
        middle_switch_closed=False
    )

    # Physical query includes the branch.
    assert switch_23 in network.branches_at(
        bus_2.id
    )

    # Electrical query excludes the open branch.
    assert switch_23 not in topology.connected_branches_at(
        bus_2.id
    )


def test_connected_branches_at_closed_bus() -> None:
    (
        _,
        topology,
        _,
        bus_2,
        _,
        _,
        switch_12,
        switch_23,
        _,
    ) = build_chain_network()

    connected = topology.connected_branches_at(
        bus_2.id
    )

    assert len(connected) == 2

    assert switch_12 in connected
    assert switch_23 in connected


# ============================================================================
# Dynamic Topology From Immutable Element Replacement
# ============================================================================


def test_topology_reflects_network_switch_replacement_without_recreation() -> None:
    (
        network,
        topology,
        bus_1,
        _,
        _,
        bus_4,
        _,
        switch_23,
        _,
    ) = build_chain_network()

    assert topology.network is network

    assert topology.is_connected is True

    assert topology.is_reachable(
        bus_1.id,
        bus_4.id,
    ) is True

    # Domain models are immutable. Replace the canonical switch
    # rather than mutating it in place.
    open_switch_23 = switch_23.model_copy(
        update={
            "is_closed": False,
        }
    )

    replace_element(
        network,
        switch_23,
        open_switch_23,
    )

    # The existing Topology object must see the changed Network.
    assert topology.network is network

    assert topology.is_connected is False

    assert topology.is_reachable(
        bus_1.id,
        bus_4.id,
    ) is False

    closed_switch_23 = open_switch_23.model_copy(
        update={
            "is_closed": True,
        }
    )

    replace_element(
        network,
        open_switch_23,
        closed_switch_23,
    )

    assert topology.is_connected is True

    assert topology.is_reachable(
        bus_1.id,
        bus_4.id,
    ) is True

# ============================================================================
# Neighborhood
# ============================================================================


def test_neighbors_in_closed_chain() -> None:
    (
        _,
        topology,
        bus_1,
        bus_2,
        bus_3,
        bus_4,
        _,
        _,
        _,
    ) = build_chain_network()

    assert topology.neighbors(
        bus_1.id
    ) == frozenset(
        {
            bus_2.id,
        }
    )

    assert topology.neighbors(
        bus_2.id
    ) == frozenset(
        {
            bus_1.id,
            bus_3.id,
        }
    )

    assert topology.neighbors(
        bus_3.id
    ) == frozenset(
        {
            bus_2.id,
            bus_4.id,
        }
    )

    assert topology.neighbors(
        bus_4.id
    ) == frozenset(
        {
            bus_3.id,
        }
    )


def test_degree_in_closed_chain() -> None:
    (
        _,
        topology,
        bus_1,
        bus_2,
        bus_3,
        bus_4,
        _,
        _,
        _,
    ) = build_chain_network()

    assert topology.degree(
        bus_1.id
    ) == 1

    assert topology.degree(
        bus_2.id
    ) == 2

    assert topology.degree(
        bus_3.id
    ) == 2

    assert topology.degree(
        bus_4.id
    ) == 1


def test_open_switch_changes_neighbor_relationship() -> None:
    (
        _,
        topology,
        _,
        bus_2,
        bus_3,
        _,
        _,
        _,
        _,
    ) = build_chain_network(
        middle_switch_closed=False
    )

    assert bus_3.id not in topology.neighbors(
        bus_2.id
    )

    assert bus_2.id not in topology.neighbors(
        bus_3.id
    )

    assert topology.degree(
        bus_2.id
    ) == 1

    assert topology.degree(
        bus_3.id
    ) == 1


# ============================================================================
# Reachability
# ============================================================================


def test_reachable_bus_ids_in_connected_chain() -> None:
    (
        _,
        topology,
        bus_1,
        bus_2,
        bus_3,
        bus_4,
        _,
        _,
        _,
    ) = build_chain_network()

    assert topology.reachable_bus_ids(
        bus_1.id
    ) == frozenset(
        {
            bus_1.id,
            bus_2.id,
            bus_3.id,
            bus_4.id,
        }
    )


def test_reachability_does_not_cross_open_switch() -> None:
    (
        _,
        topology,
        bus_1,
        bus_2,
        bus_3,
        bus_4,
        _,
        _,
        _,
    ) = build_chain_network(
        middle_switch_closed=False
    )

    assert topology.reachable_bus_ids(
        bus_1.id
    ) == frozenset(
        {
            bus_1.id,
            bus_2.id,
        }
    )

    assert topology.reachable_bus_ids(
        bus_3.id
    ) == frozenset(
        {
            bus_3.id,
            bus_4.id,
        }
    )

    assert topology.is_reachable(
        bus_1.id,
        bus_4.id,
    ) is False


# ============================================================================
# Shortest Paths
# ============================================================================


def test_shortest_path_in_closed_chain() -> None:
    (
        _,
        topology,
        bus_1,
        bus_2,
        bus_3,
        bus_4,
        _,
        _,
        _,
    ) = build_chain_network()

    assert topology.shortest_path(
        bus_1.id,
        bus_4.id,
    ) == (
        bus_1.id,
        bus_2.id,
        bus_3.id,
        bus_4.id,
    )


def test_shortest_path_returns_none_across_open_switch() -> None:
    (
        _,
        topology,
        bus_1,
        _,
        _,
        bus_4,
        _,
        _,
        _,
    ) = build_chain_network(
        middle_switch_closed=False
    )

    assert topology.shortest_path(
        bus_1.id,
        bus_4.id,
    ) is None


def test_require_path_returns_existing_path() -> None:
    (
        _,
        topology,
        bus_1,
        bus_2,
        bus_3,
        bus_4,
        _,
        _,
        _,
    ) = build_chain_network()

    assert topology.require_path(
        bus_1.id,
        bus_4.id,
    ) == (
        bus_1.id,
        bus_2.id,
        bus_3.id,
        bus_4.id,
    )


def test_require_path_raises_when_disconnected() -> None:
    (
        _,
        topology,
        bus_1,
        _,
        _,
        bus_4,
        _,
        _,
        _,
    ) = build_chain_network(
        middle_switch_closed=False
    )

    with pytest.raises(
        NoPathError
    ):
        topology.require_path(
            bus_1.id,
            bus_4.id,
        )


# ============================================================================
# Islands
# ============================================================================


def test_closed_chain_has_one_island() -> None:
    (
        _,
        topology,
        bus_1,
        bus_2,
        bus_3,
        bus_4,
        _,
        _,
        _,
    ) = build_chain_network()

    assert topology.island_count == 1

    assert component_set(
        topology.islands
    ) == {
        frozenset(
            {
                bus_1.id,
                bus_2.id,
                bus_3.id,
                bus_4.id,
            }
        )
    }


def test_open_switch_splits_network_into_two_islands() -> None:
    (
        _,
        topology,
        bus_1,
        bus_2,
        bus_3,
        bus_4,
        _,
        _,
        _,
    ) = build_chain_network(
        middle_switch_closed=False
    )

    assert topology.island_count == 2

    assert component_set(
        topology.islands
    ) == {
        frozenset(
            {
                bus_1.id,
                bus_2.id,
            }
        ),
        frozenset(
            {
                bus_3.id,
                bus_4.id,
            }
        ),
    }


def test_island_of_bus() -> None:
    (
        _,
        topology,
        bus_1,
        bus_2,
        _,
        _,
        _,
        _,
        _,
    ) = build_chain_network(
        middle_switch_closed=False
    )

    assert topology.island_of(
        bus_1.id
    ) == frozenset(
        {
            bus_1.id,
            bus_2.id,
        }
    )


# ============================================================================
# Connectivity
# ============================================================================


def test_closed_chain_is_connected() -> None:
    (
        _,
        topology,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = build_chain_network()

    assert topology.is_connected is True


def test_open_switch_disconnects_complete_network() -> None:
    (
        _,
        topology,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = build_chain_network(
        middle_switch_closed=False
    )

    assert topology.is_connected is False


# ============================================================================
# Radiality
# ============================================================================


def test_closed_chain_is_radial() -> None:
    (
        _,
        topology,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = build_chain_network()

    assert topology.has_cycles is False
    assert topology.is_acyclic is True

    assert topology.is_connected is True
    assert topology.is_radial is True

    assert topology.is_forest is True
    assert topology.is_meshed is False


def test_disconnected_radial_islands_form_forest_not_tree() -> None:
    (
        _,
        topology,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = build_chain_network(
        middle_switch_closed=False
    )

    assert topology.has_cycles is False
    assert topology.is_acyclic is True

    assert topology.is_connected is False
    assert topology.is_radial is False

    assert topology.is_forest is True
    assert topology.is_meshed is False


# ============================================================================
# Meshed Network
# ============================================================================


def test_triangle_is_meshed() -> None:
    network = Network(
        name="Meshed Three Bus Network"
    )

    bus_1 = make_bus("Bus 1")
    bus_2 = make_bus("Bus 2")
    bus_3 = make_bus("Bus 3")

    switch_12 = make_switch(
        "Switch 1-2",
        bus_1,
        bus_2,
    )

    switch_23 = make_switch(
        "Switch 2-3",
        bus_2,
        bus_3,
    )

    switch_31 = make_switch(
        "Switch 3-1",
        bus_3,
        bus_1,
    )

    add_all(
        network,
        bus_1,
        bus_2,
        bus_3,
        switch_12,
        switch_23,
        switch_31,
    )

    topology = Topology(
        network
    )

    assert topology.is_connected is True

    assert topology.has_cycles is True
    assert topology.is_acyclic is False

    assert topology.is_radial is False
    assert topology.is_forest is False
    assert topology.is_meshed is True

    assert topology.electrical_edge_count == 3


# ============================================================================
# Isolated Buses
# ============================================================================


def test_isolated_bus_is_detected() -> None:
    network = Network(
        name="Network With Isolated Bus"
    )

    bus_1 = make_bus("Bus 1")
    bus_2 = make_bus("Bus 2")
    bus_3 = make_bus("Bus 3")

    switch_12 = make_switch(
        "Switch 1-2",
        bus_1,
        bus_2,
    )

    add_all(
        network,
        bus_1,
        bus_2,
        bus_3,
        switch_12,
    )

    topology = Topology(
        network
    )

    assert topology.isolated_bus_ids == frozenset(
        {
            bus_3.id,
        }
    )

    assert topology.has_isolated_buses is True

    assert topology.degree(
        bus_3.id
    ) == 0

    assert topology.island_count == 2
    assert topology.is_connected is False
    assert topology.is_forest is True


def test_network_without_isolated_bus_reports_none() -> None:
    (
        _,
        topology,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = build_chain_network()

    assert topology.isolated_bus_ids == frozenset()
    assert topology.has_isolated_buses is False

# ============================================================================
# Source Reachability
# ============================================================================


def test_buses_reachable_from_single_source() -> None:
    (
        _,
        topology,
        bus_1,
        bus_2,
        bus_3,
        bus_4,
        _,
        _,
        _,
    ) = build_chain_network(
        middle_switch_closed=False
    )

    assert topology.buses_reachable_from(
        [
            bus_1.id,
        ]
    ) == frozenset(
        {
            bus_1.id,
            bus_2.id,
        }
    )

    assert topology.unreachable_from(
        [
            bus_1.id,
        ]
    ) == frozenset(
        {
            bus_3.id,
            bus_4.id,
        }
    )


def test_multiple_sources_cover_multiple_islands() -> None:
    (
        _,
        topology,
        bus_1,
        bus_2,
        bus_3,
        bus_4,
        _,
        _,
        _,
    ) = build_chain_network(
        middle_switch_closed=False
    )

    assert topology.buses_reachable_from(
        [
            bus_1.id,
            bus_3.id,
        ]
    ) == frozenset(
        {
            bus_1.id,
            bus_2.id,
            bus_3.id,
            bus_4.id,
        }
    )

    assert topology.unreachable_from(
        [
            bus_1.id,
            bus_3.id,
        ]
    ) == frozenset()


# ============================================================================
# Component-Level Queries
# ============================================================================


def test_component_edge_count() -> None:
    (
        _,
        topology,
        bus_1,
        bus_2,
        bus_3,
        bus_4,
        _,
        _,
        _,
    ) = build_chain_network()

    assert topology.component_edge_count(
        {
            bus_1.id,
            bus_2.id,
            bus_3.id,
        }
    ) == 2

    assert topology.component_edge_count(
        {
            bus_1.id,
            bus_2.id,
            bus_3.id,
            bus_4.id,
        }
    ) == 3


def test_component_is_radial() -> None:
    (
        _,
        topology,
        bus_1,
        bus_2,
        bus_3,
        bus_4,
        _,
        _,
        _,
    ) = build_chain_network()

    assert topology.component_is_radial(
        {
            bus_1.id,
            bus_2.id,
            bus_3.id,
            bus_4.id,
        }
    ) is True


def test_empty_component_is_not_radial() -> None:
    (
        _,
        topology,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = build_chain_network()

    assert topology.component_is_radial(
        set()
    ) is False


# ============================================================================
# Parallel Physical Branches
# ============================================================================


def test_parallel_physical_branches_collapse_to_one_graph_edge() -> None:
    network = Network(
        name="Parallel Branch Network"
    )

    bus_1 = make_bus("Bus 1")
    bus_2 = make_bus("Bus 2")

    switch_a = make_switch(
        "Switch A",
        bus_1,
        bus_2,
    )

    switch_b = make_switch(
        "Switch B",
        bus_1,
        bus_2,
    )

    add_all(
        network,
        bus_1,
        bus_2,
        switch_a,
        switch_b,
    )

    topology = Topology(
        network
    )

    # Physical Network preserves branch multiplicity.
    assert network.branch_count == 2

    # Topology preserves both connected physical branches.
    assert len(
        topology.connected_branches
    ) == 2

    # Graph represents connectivity rather than branch multiplicity.
    assert topology.electrical_edge_count == 1

    assert topology.degree(
        bus_1.id
    ) == 1

    assert topology.degree(
        bus_2.id
    ) == 1

    assert topology.is_radial is True


# ============================================================================
# Invalid Physical References
# ============================================================================


def test_invalid_branch_reference_does_not_create_phantom_bus() -> None:
    """
    Preserve the current defensive Topology policy.

    A physical branch may temporarily reference a missing bus in the
    canonical Network, but Topology must never invent a graph node for
    that missing endpoint.

    If Network-level referential integrity is strengthened later,
    this test should move to Network validation instead.
    """

    network = Network(
        name="Invalid Reference Network"
    )

    bus_1 = make_bus("Bus 1")
    missing_bus_id = uuid4()

    switch = Switch(
        id=uuid4(),
        name="Invalid Switch",
        from_node_id=bus_1.id,
        to_node_id=missing_bus_id,
        is_closed=True,
    )

    add_all(
        network,
        bus_1,
        switch,
    )

    topology = Topology(
        network
    )

    graph = topology.graph()

    assert graph.nodes == frozenset(
        {
            bus_1.id,
        }
    )

    assert missing_bus_id not in graph
    assert graph.edge_count == 0

    assert topology.isolated_bus_ids == frozenset(
        {
            bus_1.id,
        }
    )


# ============================================================================
# Unknown Bus Handling
# ============================================================================


def test_neighbors_rejects_unknown_bus() -> None:
    (
        _,
        topology,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = build_chain_network()

    with pytest.raises(
        ElementNotFoundError
    ):
        topology.neighbors(
            uuid4()
        )


def test_reachability_rejects_unknown_bus() -> None:
    (
        _,
        topology,
        bus_1,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = build_chain_network()

    with pytest.raises(
        ElementNotFoundError
    ):
        topology.is_reachable(
            bus_1.id,
            uuid4(),
        )


def test_source_reachability_rejects_unknown_source() -> None:
    (
        _,
        topology,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = build_chain_network()

    with pytest.raises(
        ElementNotFoundError
    ):
        topology.buses_reachable_from(
            [
                uuid4(),
            ]
        )

# ============================================================================
# Asset Operational-State Semantics
# ============================================================================


@pytest.mark.parametrize(
    (
        "enabled",
        "status",
        "availability",
        "expected_operational",
    ),
    [
        (
            True,
            AssetStatus.IN_SERVICE,
            AvailabilityState.AVAILABLE,
            True,
        ),
        (
            False,
            AssetStatus.IN_SERVICE,
            AvailabilityState.AVAILABLE,
            False,
        ),
        (
            True,
            AssetStatus.OUT_OF_SERVICE,
            AvailabilityState.AVAILABLE,
            False,
        ),
        (
            True,
            AssetStatus.MAINTENANCE,
            AvailabilityState.AVAILABLE,
            False,
        ),
        (
            True,
            AssetStatus.PLANNED,
            AvailabilityState.AVAILABLE,
            False,
        ),
        (
            True,
            AssetStatus.DECOMMISSIONED,
            AvailabilityState.AVAILABLE,
            False,
        ),
        (
            True,
            AssetStatus.FAULTED,
            AvailabilityState.AVAILABLE,
            False,
        ),
        (
            True,
            AssetStatus.IN_SERVICE,
            AvailabilityState.UNAVAILABLE,
            False,
        ),
        (
            True,
            AssetStatus.IN_SERVICE,
            AvailabilityState.LIMITED,
            True,
        ),
        (
            True,
            AssetStatus.IN_SERVICE,
            AvailabilityState.UNKNOWN,
            True,
        ),
    ],
)
def test_switch_operational_state_semantics(
    enabled: bool,
    status: AssetStatus,
    availability: AvailabilityState,
    expected_operational: bool,
) -> None:
    """
    Prove the Asset.is_operational contract independently of Topology.

    LIMITED remains operational.

    UNKNOWN also remains operational under the current DomainArchitecture
    policy because only UNAVAILABLE explicitly removes availability.
    """

    bus_1 = make_bus("Bus 1")
    bus_2 = make_bus("Bus 2")

    switch = make_switch(
        "Operational State Switch",
        bus_1,
        bus_2,
        enabled=enabled,
        status=status,
        availability=availability,
    )

    assert switch.is_operational is expected_operational


# ============================================================================
# Switch Electrical-Connectivity Semantics
# ============================================================================


@pytest.mark.parametrize(
    (
        "enabled",
        "is_closed",
        "expected_connected",
    ),
    [
        (
            True,
            True,
            True,
        ),
        (
            True,
            False,
            False,
        ),
        (
            False,
            True,
            False,
        ),
        (
            False,
            False,
            False,
        ),
    ],
)
def test_switch_connectivity_requires_operational_and_closed(
    enabled: bool,
    is_closed: bool,
    expected_connected: bool,
) -> None:
    """
    A Switch establishes electrical connectivity only when it is both
    operational and closed.
    """

    network = Network(
        name="Switch Connectivity Test"
    )

    bus_1 = make_bus("Bus 1")
    bus_2 = make_bus("Bus 2")

    switch = make_switch(
        "Switch 1-2",
        bus_1,
        bus_2,
        enabled=enabled,
        is_closed=is_closed,
    )

    add_all(
        network,
        bus_1,
        bus_2,
        switch,
    )

    topology = Topology(
        network
    )

    assert topology.branch_is_connected(
        switch
    ) is expected_connected


@pytest.mark.parametrize(
    "status",
    [
        AssetStatus.OUT_OF_SERVICE,
        AssetStatus.MAINTENANCE,
        AssetStatus.PLANNED,
        AssetStatus.DECOMMISSIONED,
        AssetStatus.FAULTED,
    ],
)
def test_non_service_closed_switch_is_disconnected(
    status: AssetStatus,
) -> None:
    """
    Closed state alone is insufficient.

    Every non-IN_SERVICE status removes the Switch from the electrical
    topology.
    """

    network = Network(
        name="Switch Status Test"
    )

    bus_1 = make_bus("Bus 1")
    bus_2 = make_bus("Bus 2")

    switch = make_switch(
        "Switch 1-2",
        bus_1,
        bus_2,
        status=status,
        is_closed=True,
    )

    add_all(
        network,
        bus_1,
        bus_2,
        switch,
    )

    topology = Topology(
        network
    )

    assert switch.is_closed is True
    assert switch.is_operational is False

    assert topology.branch_is_connected(
        switch
    ) is False

    assert topology.electrical_edge_count == 0
    assert topology.is_connected is False


def test_unavailable_closed_switch_is_disconnected() -> None:
    network = Network(
        name="Unavailable Switch Test"
    )

    bus_1 = make_bus("Bus 1")
    bus_2 = make_bus("Bus 2")

    switch = make_switch(
        "Switch 1-2",
        bus_1,
        bus_2,
        availability=AvailabilityState.UNAVAILABLE,
        is_closed=True,
    )

    add_all(
        network,
        bus_1,
        bus_2,
        switch,
    )

    topology = Topology(
        network
    )

    assert switch.is_closed is True
    assert switch.is_operational is False

    assert topology.branch_is_connected(
        switch
    ) is False

    assert topology.electrical_edge_count == 0


@pytest.mark.parametrize(
    "availability",
    [
        AvailabilityState.AVAILABLE,
        AvailabilityState.LIMITED,
        AvailabilityState.UNKNOWN,
    ],
)
def test_operational_availability_states_allow_closed_switch(
    availability: AvailabilityState,
) -> None:
    """
    AVAILABLE, LIMITED, and UNKNOWN remain operational under the
    current Asset.is_operational policy.
    """

    network = Network(
        name="Switch Availability Test"
    )

    bus_1 = make_bus("Bus 1")
    bus_2 = make_bus("Bus 2")

    switch = make_switch(
        "Switch 1-2",
        bus_1,
        bus_2,
        availability=availability,
        is_closed=True,
    )

    add_all(
        network,
        bus_1,
        bus_2,
        switch,
    )

    topology = Topology(
        network
    )

    assert switch.is_operational is True

    assert topology.branch_is_connected(
        switch
    ) is True

    assert topology.electrical_edge_count == 1
    assert topology.is_connected is True


# ============================================================================
# Non-Operational Physical Membership
# ============================================================================


def test_non_operational_switch_remains_physical_asset() -> None:
    (
        network,
        topology,
        _,
        bus_2,
        _,
        _,
        _,
        switch_23,
        _,
    ) = build_chain_network()

    disabled_switch = switch_23.model_copy(
        update={
            "enabled": False,
        }
    )

    replace_element(
        network,
        switch_23,
        disabled_switch,
    )

    # Physical identity is preserved.
    assert disabled_switch.id == switch_23.id

    # The asset remains physically present.
    assert network.get(
        disabled_switch.id
    ) is disabled_switch

    assert disabled_switch in network.switches

    assert disabled_switch in network.branches_at(
        bus_2.id
    )

    # But it no longer participates electrically.
    assert disabled_switch not in topology.connected_branches

    assert disabled_switch in topology.disconnected_switches

    assert disabled_switch not in topology.connected_branches_at(
        bus_2.id
    )


# ============================================================================
# Operational-State Replacement and Recovery
# ============================================================================


def test_topology_reflects_operational_state_replacement_and_recovery() -> None:
    (
        network,
        topology,
        bus_1,
        _,
        _,
        bus_4,
        _,
        switch_23,
        _,
    ) = build_chain_network()

    assert topology.is_connected is True

    assert topology.is_reachable(
        bus_1.id,
        bus_4.id,
    ) is True

    unavailable_switch = switch_23.model_copy(
        update={
            "availability": AvailabilityState.UNAVAILABLE,
        }
    )

    replace_element(
        network,
        switch_23,
        unavailable_switch,
    )

    assert unavailable_switch.id == switch_23.id
    assert unavailable_switch.is_operational is False

    assert topology.is_connected is False

    assert topology.is_reachable(
        bus_1.id,
        bus_4.id,
    ) is False

    restored_switch = unavailable_switch.model_copy(
        update={
            "availability": AvailabilityState.AVAILABLE,
        }
    )

    replace_element(
        network,
        unavailable_switch,
        restored_switch,
    )

    assert restored_switch.id == switch_23.id
    assert restored_switch.is_operational is True

    assert topology.is_connected is True

    assert topology.is_reachable(
        bus_1.id,
        bus_4.id,
    ) is True


# ============================================================================
# Real Line Branch Semantics
# ============================================================================


def test_operational_line_creates_electrical_edge() -> None:
    """
    Prove that Topology operates on the generic Branch abstraction,
    not only on Switch.
    """

    network = Network(
        name="Operational Line Test"
    )

    bus_1 = make_bus("Bus 1")
    bus_2 = make_bus("Bus 2")

    line = make_line(
        "Line 1-2",
        bus_1,
        bus_2,
    )

    add_all(
        network,
        bus_1,
        bus_2,
        line,
    )

    topology = Topology(
        network
    )

    assert line.is_operational is True

    assert topology.branch_is_connected(
        line
    ) is True

    assert line in network.branches
    assert line in topology.connected_branches

    assert topology.electrical_edge_count == 1

    assert topology.is_reachable(
        bus_1.id,
        bus_2.id,
    ) is True

    assert topology.is_connected is True


def test_disabled_line_remains_physical_but_not_electrical() -> None:
    network = Network(
        name="Disabled Line Test"
    )

    bus_1 = make_bus("Bus 1")
    bus_2 = make_bus("Bus 2")

    line = make_line(
        "Line 1-2",
        bus_1,
        bus_2,
        enabled=False,
    )

    add_all(
        network,
        bus_1,
        bus_2,
        line,
    )

    topology = Topology(
        network
    )

    assert line.is_operational is False

    # Physical Network membership remains.
    assert line in network.branches
    assert line in network.lines

    # Electrical participation is removed.
    assert topology.branch_is_connected(
        line
    ) is False

    assert line not in topology.connected_branches

    assert topology.electrical_edge_count == 0

    assert topology.is_reachable(
        bus_1.id,
        bus_2.id,
    ) is False

    assert topology.is_connected is False


def test_out_of_service_line_is_not_electrically_connected() -> None:
    network = Network(
        name="Out Of Service Line Test"
    )

    bus_1 = make_bus("Bus 1")
    bus_2 = make_bus("Bus 2")

    line = make_line(
        "Line 1-2",
        bus_1,
        bus_2,
        status=AssetStatus.OUT_OF_SERVICE,
    )

    add_all(
        network,
        bus_1,
        bus_2,
        line,
    )

    topology = Topology(
        network
    )

    assert line.is_operational is False

    assert topology.branch_is_connected(
        line
    ) is False

    assert topology.electrical_edge_count == 0


def test_unavailable_line_is_not_electrically_connected() -> None:
    network = Network(
        name="Unavailable Line Test"
    )

    bus_1 = make_bus("Bus 1")
    bus_2 = make_bus("Bus 2")

    line = make_line(
        "Line 1-2",
        bus_1,
        bus_2,
        availability=AvailabilityState.UNAVAILABLE,
    )

    add_all(
        network,
        bus_1,
        bus_2,
        line,
    )

    topology = Topology(
        network
    )

    assert line.is_operational is False

    assert topology.branch_is_connected(
        line
    ) is False

    assert topology.electrical_edge_count == 0


@pytest.mark.parametrize(
    "availability",
    [
        AvailabilityState.AVAILABLE,
        AvailabilityState.LIMITED,
        AvailabilityState.UNKNOWN,
    ],
)
def test_operational_line_availability_states_remain_connected(
    availability: AvailabilityState,
) -> None:
    network = Network(
        name="Line Availability Test"
    )

    bus_1 = make_bus("Bus 1")
    bus_2 = make_bus("Bus 2")

    line = make_line(
        "Line 1-2",
        bus_1,
        bus_2,
        availability=availability,
    )

    add_all(
        network,
        bus_1,
        bus_2,
        line,
    )

    topology = Topology(
        network
    )

    assert line.is_operational is True

    assert topology.branch_is_connected(
        line
    ) is True

    assert topology.electrical_edge_count == 1

    assert topology.is_connected is True

