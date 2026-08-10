"""
GridStudio AI

Module:
    base_builder.py

Description:
    Defines the reusable benchmark network builder.

    The benchmark builder converts immutable benchmark datasets
    into canonical GridStudio Network objects.

    It performs no electrical calculations.

    Numerical benchmark validation belongs to the simulation layer.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations
from types import MappingProxyType
from uuid import UUID

from src.domain.bus import Bus
from src.domain.generator import Generator
from src.domain.line import Line
from src.domain.load import Load

from src.domain.network.network import Network
from src.domain.electrical.line_parameters import (
    LineParameters,
)

from src.network.benchmarks.common.metadata import (
    BenchmarkMetadata,
)
from src.network.benchmarks.common.types import (
    BenchmarkDataset,
    BranchData,
    BusData,
    LoadData,
)
from src.network.benchmarks.common.validation import (
    BenchmarkValidator,
)

class BenchmarkBuilder:
    """
    Base class for IEEE benchmark network builders.

    Concrete benchmark builders provide immutable benchmark
    datasets while this class performs the construction of
    GridStudio domain models.
    """

    #
    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    #

    def __init__(
        self,
        *,
        dataset: BenchmarkDataset,
        metadata: BenchmarkMetadata,
    ) -> None:
        """
        Initialize the benchmark builder.
        """

        self._dataset = dataset

        self._metadata = metadata

        #
        # Benchmark bus number
        #
        #          ↓
        #
        #       Bus object
        #

        #
        # Benchmark number → GridStudio UUID lookups.
        #

        self._bus_objects: dict[int, Bus] = {}
        
        self._bus_lookup: dict[int, UUID] = {}

        self._branch_lookup: dict[int, UUID] = {}

        self._load_lookup: dict[int, UUID] = {}

        self._generator_lookup: dict[int, UUID] = {}

    #
    # ------------------------------------------------------------------
    # Public Properties
    # ------------------------------------------------------------------
    #

    @property
    def dataset(
        self,
    ) -> BenchmarkDataset:
        """
        Return the immutable benchmark dataset.
        """

        return self._dataset

    @property
    def metadata(
        self,
    ) -> BenchmarkMetadata:
        """
        Return benchmark metadata.
        """

        return self._metadata

    @property
    def bus_lookup(
        self,
    ) -> MappingProxyType:
        """
        Mapping from benchmark bus number
        to GridStudio bus UUID.
        """

        return MappingProxyType(
            self._bus_lookup
        )

    @property
    def branch_lookup(
        self,
    ) -> MappingProxyType:
        """
        Mapping from benchmark branch number
        to GridStudio branch UUID.
        """

        return MappingProxyType(
            self._branch_lookup
        )

    @property
    def load_lookup(
        self,
    ) -> MappingProxyType:
        """
        Mapping from benchmark load number
        to GridStudio load UUID.
        """

        return MappingProxyType(
            self._load_lookup
        )

    @property
    def generator_lookup(
        self,
    ) -> MappingProxyType:
        """
        Mapping from benchmark generator number
        to GridStudio generator UUID.
        """

        return MappingProxyType(
            self._generator_lookup
        )

    #
    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    #

    def build(
        self,
    ) -> Network:
        """
        Build and return the benchmark network.
        """

        #
        # Validate dataset before construction.
        #

        BenchmarkValidator.validate(
            self._dataset,
        )

        #
        # Create empty network.
        #

        network = Network(
            name=self._metadata.name,
            description=self._metadata.description,
            base_frequency_hz=self._metadata.base_frequency_hz,
        )

        #
        # Build network.
        #

        self._build_buses(
            network,
        )

        self._build_branches(
            network,
        )

        self._build_loads(
            network,
        )

        self._build_generators(
            network,
        )

        #
        # Verify all references.
        #

        network.validate_references()

        return network

    #
    # ------------------------------------------------------------------
    # Protected Helpers
    # ------------------------------------------------------------------
    #

    def _register_bus(
        self,
        *,
        bus_number: int,
        bus: Bus,
    ) -> None:
        """
        Register a benchmark bus.
        """
        self._bus_objects[
            bus_number
        ] = bus

        self._bus_lookup[
            bus_number
        ] = bus.id

    def _lookup_bus(
        self,
        bus_number: int,
    ) -> Bus:
        """
        Return the benchmark bus corresponding to the given
        benchmark bus number.
        """

        return self._bus_objects[
            bus_number
        ]

    def _bus_name(
        self,
        bus_data: BusData,
    ) -> str:
        """
        Return the benchmark bus name.
        """

        return (
            bus_data.name
            or f"Bus {bus_data.bus_number}"
        )

    def _build_line_parameters(
        self,
        branch_data: BranchData,
    ) -> LineParameters:
        """
        Create balanced line parameters from benchmark branch data.

        Benchmark branch impedances are stored as total branch
        impedances in Ohms. The builder translates them into
        GridStudio line parameters.
        """
        #
        # TODO:
        # IEEE benchmark datasets store total branch impedance.
        # If LineParameters later gains a factory such as
        # from_total_impedance(...), replace this translation.
        #
        return LineParameters.balanced(
            r1_ohm_per_km=branch_data.resistance_ohm,
            x1_ohm_per_km=branch_data.reactance_ohm,
            c1_nf_per_km=0.0,
        )

    def _active_power_mw(
        self,
        load_data: LoadData,
    ) -> float:
        """
        Convert benchmark active power to MW.
        """

        return load_data.active_power_kw / 1000.0

    def _reactive_power_mvar(
        self,
        load_data: LoadData,
    ) -> float:
        """
        Convert benchmark reactive power to MVAr.
        """

        return load_data.reactive_power_kvar / 1000.0


    #
    # ------------------------------------------------------------------
    # Protected Build Stages
    # ------------------------------------------------------------------
    #

    def _build_buses(
        self,
        network: Network,
    ) -> None:
        """
        Build benchmark buses.
        """

        for bus_data in self._dataset.buses:

            bus = Bus(

                name=(
                    bus_data.name
                    or f"Bus {bus_data.bus_number}"),

                nominal_voltage_kv=(
                    bus_data.base_voltage_kv
                ),

                bus_type=bus_data.bus_type,
            )

            network.add(
                bus,
            )

            self._register_bus(
                bus_number=bus_data.bus_number,
                bus=bus,
            )


    def _build_branches(
        self,
        network: Network,
    ) -> None:
        """
        Build benchmark branches.
        """

        for branch_data in self._dataset.branches:

            from_bus = self._lookup_bus(
                branch_data.from_bus_number,
            )

            to_bus = self._lookup_bus(
                branch_data.to_bus_number,
            )

            parameters = self._build_line_parameters(
                branch_data,
            )

            line = Line(

                name=f"Line {branch_data.branch_number}",

                from_node_id=from_bus.id,

                to_node_id=to_bus.id,

                length_km=1.0,

                parameters=parameters,
            )

            network.add(
                line,
            )

            self._branch_lookup[
                branch_data.branch_number
            ] = line.id

    def _build_loads(
        self,
        network: Network,
    ) -> None:
        """
        Build benchmark loads.
        """

        for load_data in self._dataset.loads:

            bus = self._lookup_bus(
                load_data.bus_number,
            )

            load = Load.consumption(

                name=f"Load {load_data.load_number}",

                node_id=bus.id,

                active_power_mw=self._active_power_mw(
                    load_data,
                ),

                reactive_power_mvar=self._reactive_power_mvar(
                    load_data,
                ),
            )

            network.add(
                load,
            )

            self._load_lookup[
                load_data.load_number   
            ] = load.id


    def _build_generators(
        self,
        network: Network,
    ) -> None:
        """
        Build benchmark generators.
        """

        for generator_data in self._dataset.generators:

            bus = self._lookup_bus(
                generator_data.bus_number,
            )

            generator = Generator.generation(

                name=(
                    f"Generator "
                    f"{generator_data.generator_number}"
                ),

                node_id=bus.id,

                active_power_mw=(
                    generator_data.active_power_mw
                ),

                reactive_power_mvar=(
                    generator_data.reactive_power_mvar
                ),

                rated_power_mva=(
                    generator_data.rated_power_mva
                ),

                voltage_setpoint_pu=(
                    generator_data.voltage_setpoint_pu
                ),
            )

            network.add(
                generator,
            )

            self._generator_lookup[
                generator_data.generator_number
            ] = generator.id 




