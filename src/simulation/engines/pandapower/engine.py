"""
GridStudio AI

Module:
    engine.py

Description:
    Pandapower implementation of the GridStudio simulation engine.

    The engine coordinates the complete steady-state power-flow
    workflow:

        GridStudio Network
            ↓
        PandapowerConverter
            ↓
        pandapower.runpp()
            ↓
        PandapowerMappingResult()
            ↓
        PowerFlowResult

    The engine owns execution lifecycle, timing, solver invocation,
    metadata, and final result construction.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from datetime import UTC
from datetime import datetime
from time import perf_counter
from uuid import UUID
from uuid import uuid4

import pandapower as pp

from src.core.enums.simulation import (
    SimulationMode,
)
from src.core.enums.simulation import (
    StudyType,
)

from src.simulation.engines.base.capabilities import (
    EngineCapabilities,
)
from src.simulation.engines.base.engine import (
    SimulationEngine,
)

from src.simulation.models.requests.power_flow_request import (
    PowerFlowRequest,
)

from src.simulation.models.results.power_flow_result import (
    PowerFlowResult,
)

from .converter import (
    PandapowerConverter,
)
from .result_mapper import (
    PandapowerResultMapper,
)

from .mapping_results import (
    PandapowerMappingResult,
)

# ============================================================================
# Pandapower Engine
# ============================================================================


class PandapowerEngine(
    SimulationEngine,
):
    """
    GridStudio power-flow engine backed by pandapower.

    Responsibilities
    ----------------

    * validate simulation requests

    * convert GridStudio models to pandapower

    * execute numerical power flow

    * map solved results

    * construct the final PowerFlowResult

    The engine owns execution metadata and solver lifecycle.

    Numerical calculations remain entirely within pandapower.
    """

    #
    # ------------------------------------------------------------------
    # Engine Identity
    # ------------------------------------------------------------------
    #

    ENGINE_NAME = "pandapower"

        #
    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    #

    def __init__(
        self,
    ) -> None:
        """
        Create a new pandapower engine.
        """

        self._converter = (
            PandapowerConverter()
        )

        self._mapper = (
            PandapowerResultMapper()
        )


        #
    # ------------------------------------------------------------------
    # Engine Identity
    # ------------------------------------------------------------------
    #

    @property
    def name(
        self,
    ) -> str:
        """
        Return the canonical engine name.
        """

        return self.ENGINE_NAME

    @property
    def capabilities(
        self,
    ) -> EngineCapabilities:
        """
        Return the capabilities supported by
        this engine.
        """

        return EngineCapabilities(

            study_types=frozenset({

                StudyType.POWER_FLOW,

            }),

            simulation_modes=frozenset({

                SimulationMode.STEADY_STATE,

            }),
        )

        #
    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    #

    def _validate_request(
        self,
        request: PowerFlowRequest,
    ) -> None:
        """
        Validate a power-flow request before execution.
        """

        if not isinstance(
            request,
            PowerFlowRequest,
        ):
            raise TypeError(
                "Expected PowerFlowRequest."
            )

        #
        # PowerFlowRequest already guarantees
        # at least one reference source.
        #
        # Additional engineering validation
        # may be added here in future.
        #
    
        #
    # ------------------------------------------------------------------
    # Solver
    # ------------------------------------------------------------------
    #

    def _execute_power_flow(
        self,
        pp_net,
    ) -> None:
        """
        Execute the pandapower power-flow solver.
        """

        pp.runpp(
            pp_net,
        )

        #
    # ------------------------------------------------------------------
    # Execution Helpers
    # ------------------------------------------------------------------
    #

    @staticmethod
    def _current_timestamp(
    ) -> datetime:
        """
        Return the current UTC timestamp.
        """

        return datetime.now(UTC)


    @staticmethod
    def _execution_time(
        start_counter: float,
        end_counter: float,
    ) -> float:
        """
        Compute elapsed execution time.
        """

        return (
            end_counter
            - start_counter
        )


    #
    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------
    #

    def run(
        self,
        request: PowerFlowRequest,
    ) -> PowerFlowResult:
        """
        Execute a steady-state power-flow study.
        """

        #
        # Validate request
        #

        self._validate_request(
            request,
        )

        #
        # Begin execution lifecycle
        #

        simulation_id = uuid4()

        started_at = self._current_timestamp()

        start_counter = perf_counter()

        #
        # Convert GridStudio network
        #

        conversion = self._converter.convert(
            network=request.network,
            reference_sources=request.reference_sources,
        )

        #
        # Execute numerical solver
        #

        self._execute_power_flow(
            conversion.network,
        )

        #
        # Translate pandapower results
        #

        mapping_result = self._mapper.map(
            conversion.network,
            conversion,
        )

        #
        # Complete execution lifecycle
        #

        end_counter = perf_counter()

        completed_at = self._current_timestamp()

        execution_time_seconds = (
            self._execution_time(
                start_counter,
                end_counter,
            )
        )

        return self._build_result(
            simulation_id=simulation_id,
            request=request,
            mapping_result=mapping_result,
            started_at=started_at,
            completed_at=completed_at,
            execution_time_seconds=execution_time_seconds,
        )        
    

    #
    # ------------------------------------------------------------------
    # Result Assembly
    # ------------------------------------------------------------------
    #

    def _build_result(
        self,
        *,
        simulation_id: UUID,
        request: PowerFlowRequest,
        mapping_result: PandapowerMappingResult,
        started_at: datetime,
        completed_at: datetime,
        execution_time_seconds: float,
    ) -> PowerFlowResult:
        """
        Build the final immutable GridStudio power-flow result.
        """

        statistics = mapping_result.statistics

        return PowerFlowResult(

            #
            # ----------------------------------------------------------
            # BaseSimulationResult
            # ----------------------------------------------------------
            #

            simulation_id=simulation_id,

            simulation_name=(
                "Pandapower Power Flow"
            ),

            started_at=started_at,

            completed_at=completed_at,

            execution_time_seconds=execution_time_seconds,

            successful=(
                mapping_result.convergence.converged
            ),

            solver_name=self.name,

            solver_version=pp.__version__,

            notes="",

            warnings=[],

            errors=[],

            #
            # ----------------------------------------------------------
            # Solver diagnostics
            # ----------------------------------------------------------
            #

            convergence=mapping_result.convergence,

            iterations=[],

            #
            # ----------------------------------------------------------
            # Network metadata
            # ----------------------------------------------------------
            #

            network_name=request.network.name,

            #
            # TODO:
            #
            # Read these from the GridStudio
            # Network model once available.
            #
            base_power_mva=None,

            base_frequency_hz=50.0,

            #
            # ----------------------------------------------------------
            # Network states
            # ----------------------------------------------------------
            #

            bus_states=mapping_result.bus_states,

            branch_states=mapping_result.branch_states,

            transformer_states=(
                mapping_result.transformer_states
            ),

            #
            # ----------------------------------------------------------
            # Injection states
            # ----------------------------------------------------------
            #

            load_states=mapping_result.load_states,

            generator_states=(
                mapping_result.generator_states
            ),

            battery_states=(
                mapping_result.battery_states
            ),

            ev_states=(
                mapping_result.ev_states
            ),

            shunt_states=(
                mapping_result.shunt_states
            ),

            solar_states=(
                mapping_result.solar_states
            ),

            wind_states=(
                mapping_result.wind_states
            ),

            #
            # ----------------------------------------------------------
            # Aggregate statistics
            # ----------------------------------------------------------
            #

            total_active_generation_mw=(
                statistics[
                    "total_active_generation_mw"
                ]
            ),

            total_reactive_generation_mvar=(
                statistics[
                    "total_reactive_generation_mvar"
                ]
            ),

            total_active_load_mw=(
                statistics[
                    "total_active_load_mw"
                ]
            ),

            total_reactive_load_mvar=(
                statistics[
                    "total_reactive_load_mvar"
                ]
            ),

            total_active_loss_mw=(
                statistics[
                    "total_active_loss_mw"
                ]
            ),

            total_reactive_loss_mvar=(
                statistics[
                    "total_reactive_loss_mvar"
                ]
            ),

            minimum_bus_voltage_pu=(
                statistics[
                    "minimum_bus_voltage_pu"
                ]
            ),

            maximum_bus_voltage_pu=(
                statistics[
                    "maximum_bus_voltage_pu"
                ]
            ),

            average_bus_voltage_pu=(
                statistics[
                    "average_bus_voltage_pu"
                ]
            ),

            maximum_branch_loading_percent=(
                statistics[
                    "maximum_branch_loading_percent"
                ]
            ),

            system_power_factor=(
                statistics[
                    "system_power_factor"
                ]
            ),
        )

