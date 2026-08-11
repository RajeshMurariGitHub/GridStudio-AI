"""
GridStudio AI

Module:
    result_mapper.py

Description:
    Maps solved pandapower simulation results into
    GridStudio simulation state models.

    The result mapper is responsible for translating
    solved pandapower result tables into immutable
    GridStudio simulation result models.

    Numerical calculations are performed by pandapower.

    This module performs only data translation.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

import math
from typing import Any
from uuid import UUID

import pandas as pd

from pandas import DataFrame

from src.simulation.models.convergence import (
    ConvergenceInfo,
)

from .mapping_results import (
    PandapowerMappingResult,
)

from src.simulation.states.branch_state import (
    BranchState,
)
from src.simulation.states.bus_state import (
    BusState,
)
from src.simulation.states.load_state import (
    LoadState,
)
from src.simulation.states.generator_state import (
    GeneratorState,
)
from src.simulation.states.transformer_state import (
    TransformerState,
)
from src.simulation.states.battery_state import (
    BatteryState,
)
from src.simulation.states.ev_state import (
    EVState,
)
from src.simulation.states.shunt_state import (
    ShuntState,
)
from src.simulation.states.solar_state import (
    SolarState,
)
from src.simulation.states.wind_state import (
    WindState,
)

from .converter import (
    PandapowerConversion,
)

# ============================================================================
# Pandapower Result Mapper
# ============================================================================


class PandapowerResultMapper:
    """
    Translate solved pandapower networks into
    GridStudio simulation results.

    Notes
    -----
    The mapper owns no electrical calculations.

    It simply converts solved numerical quantities into
    immutable GridStudio simulation state objects.
    """

    #
    # ------------------------------------------------------------------
    # Engineering Defaults
    # ------------------------------------------------------------------
    #

    DEFAULT_MIN_VOLTAGE_PU = 0.95

    DEFAULT_MAX_VOLTAGE_PU = 1.05

    #
    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    #

    def __init__(
        self,
    ) -> None:
        """
        Create a new result mapper.
        """

        self._pp_net = None

        self._conversion = None

        #
        # (table_name, row_index)
        #     ->
        # GridStudio UUID
        #

        self._reverse_lookup: dict[
            tuple[str, int],
            UUID,
        ] = {}

        #
        # UUID
        #   ->
        # canonical asset type
        #

        self._asset_types: dict[
            UUID,
            str,
        ] = {}

    #
    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------
    #

    def _initialize(
        self,
        pp_net,
        conversion: PandapowerConversion,
    ) -> None:
        """
        Prepare the mapper for a new mapping operation.
        """

        self._pp_net = pp_net

        self._conversion = conversion

        self._reverse_lookup.clear()

        self._asset_types.clear()

        self._build_reverse_lookup()

    #
    # ------------------------------------------------------------------
    # Reverse Lookup
    # ------------------------------------------------------------------
    #

    def _build_reverse_lookup(
        self,
    ) -> None:
        """
        Build reverse lookup dictionaries.

        The converter stores mappings from

            UUID
                ->
            pandapower table/index

        The mapper requires the inverse lookup.

        This method computes it once per mapping
        operation.
        """

        for (
            asset_id,
            mapping,
        ) in self._conversion.element_mappings.items():

            self._reverse_lookup[
                (
                    mapping.table,
                    mapping.index,
                )
            ] = asset_id

            #
            # asset_type requires the
            # enhanced PandapowerElementMapping.
            #

            self._asset_types[
                asset_id
            ] = mapping.asset_type

    #
    # ------------------------------------------------------------------
    # Lookup Helpers
    # ------------------------------------------------------------------
    #

    def _asset_id(
        self,
        table: str,
        index: int,
    ) -> UUID:
        """
        Return the GridStudio UUID corresponding to
        a pandapower table row.
        """

        return self._reverse_lookup[
            (
                table,
                index,
            )
        ]

    def _asset_type(
        self,
        asset_id: UUID,
    ) -> str:
        """
        Return the GridStudio asset category.

        Returns
        -------
        str

        Examples
        --------
        "battery"

        "ev"

        "generator"

        "solar"

        "wind"
        """

        return self._asset_types.get(
            asset_id,
            "",
        )

    #
    # ------------------------------------------------------------------
    # Pandapower Table Helpers
    # ------------------------------------------------------------------
    #

    def _has_table(
        self,
        table_name: str,
    ) -> bool:
        """
        Return True when a pandapower table exists.
        """

        return hasattr(
            self._pp_net,
            table_name,
        )

    def _table(
        self,
        table_name: str,
    ) -> DataFrame:
        """
        Return a pandapower table.

        Raises
        ------
        AttributeError
            If the requested table is unavailable.
        """

        return getattr(
            self._pp_net,
            table_name,
        )

    #
    # ------------------------------------------------------------------
    # Numerical Helpers
    # ------------------------------------------------------------------
    #

    @staticmethod
    def _float(
        value: Any,
    ) -> float:
        """
        Safely convert numerical values.

        None and NaN are converted to 0.0.
        """

        if value is None:
            return 0.0

        value = float(value)

        if math.isnan(value):
            return 0.0

        return value

    @classmethod
    def _voltage_violation(
        cls,
        voltage_pu: float,
    ) -> bool:
        """
        Return True when voltage violates the
        default engineering limits.
        """

        return (
            voltage_pu < cls.DEFAULT_MIN_VOLTAGE_PU
            or
            voltage_pu > cls.DEFAULT_MAX_VOLTAGE_PU
        )

    @staticmethod
    def _complex_voltage(
        magnitude_pu: float,
        angle_deg: float,
    ) -> complex:
        """
        Construct the complex voltage phasor.
        """

        angle_rad = math.radians(
            angle_deg,
        )

        return complex(
            magnitude_pu * math.cos(angle_rad),
            magnitude_pu * math.sin(angle_rad),
        )

    #
    # ------------------------------------------------------------------
    # Bus Mapping
    # ------------------------------------------------------------------
    #

    def _map_bus_results(
        self,
    ) -> dict[UUID, BusState]:
        """
        Map solved pandapower bus results.
        """

        bus_states: dict[
            UUID,
            BusState,
        ] = {}

        if not self._has_table("res_bus"):
            return bus_states

        table = self._table("res_bus")

        if table.empty:
            return bus_states

        for bus_index, row in table.iterrows():

            try:
                asset_id = self._asset_id(
                    "bus",
                    bus_index,
                )

            except KeyError:
                continue

            bus_states[
                asset_id
            ] = self._create_bus_state(
                asset_id,
                row,
            )

        return bus_states

    def _create_bus_state(
        self,
        asset_id: UUID,
        row,
    ) -> BusState:
        """
        Construct a BusState.
        """

        vm = self._float(
            row.vm_pu,
        )

        va = self._float(
            row.va_degree,
        )

        p = self._float(
            row.p_mw,
        )

        q = self._float(
            row.q_mvar,
        )

        voltage_complex = self._complex_voltage(
            vm,
            va,
        )

        voltage_violation = self._voltage_violation(
            vm,
        )

        return BusState(
            asset_id=asset_id,
            voltage_magnitude_pu=vm,
            voltage_angle_deg=va,
            voltage_complex=voltage_complex,
            net_active_power_mw=p,
            net_reactive_power_mvar=q,
            voltage_violation=voltage_violation,
        )

    #
    # ------------------------------------------------------------------
    # Branch Mapping
    # ------------------------------------------------------------------
    #

    def _map_branch_results(
        self,
    ) -> dict[
        UUID,
        BranchState,
    ]:
        """
        Map solved pandapower line results.
        """

        branch_states: dict[
            UUID,
            BranchState,
        ] = {}

        if not self._has_table("res_line"):
            return branch_states

        table = self._table(
            "res_line",
        )

        if table.empty:
            return branch_states

        for line_index, row in table.iterrows():

            try:
                asset_id = self._asset_id(
                    "line",
                    line_index,
                )

            except KeyError:
                continue

            branch_states[
                asset_id
            ] = self._create_branch_state(
                asset_id,
                row,
            )

        return branch_states

    def _create_branch_state(
        self,
        asset_id: UUID,
        row,
    ) -> BranchState:
        #
        # pandapower reports line current in kA.
        # GridStudio stores current in amperes.
        #

        current_ampere = (
            self._float(row.i_ka)
            * 1000.0
        )

        p_from = self._float(
            row.p_from_mw,
        )

        q_from = self._float(
            row.q_from_mvar,
        )

        p_to = self._float(
            row.p_to_mw,
        )

        q_to = self._float(
            row.q_to_mvar,
        )

        p_loss = self._float(
            row.pl_mw,
        )

        q_loss = self._float(
            row.ql_mvar,
        )

        loading = self._float(
            row.loading_percent,
        )

        return BranchState(
            asset_id=asset_id,
            current_ampere=current_ampere,
            active_power_from_mw=p_from,
            reactive_power_from_mvar=q_from,
            active_power_to_mw=p_to,
            reactive_power_to_mvar=q_to,
            active_loss_mw=p_loss,
            reactive_loss_mvar=q_loss,
            loading_percent=loading,
        )

    #
    # ------------------------------------------------------------------
    # Transformer Mapping
    # ------------------------------------------------------------------
    #

    def _map_transformer_results(
        self,
    ) -> dict[
        UUID,
        TransformerState,
    ]:
        """
        Map solved transformer results.
        """

        transformer_states: dict[
            UUID,
            TransformerState,
        ] = {}

        if not self._has_table(
            "res_trafo",
        ):
            return transformer_states

        result_table = self._table(
            "res_trafo",
        )

        if result_table.empty:
            return transformer_states

        has_tap = (
            self._has_table(
                "trafo",
            )
            and
            "tap_pos"
            in self._table(
                "trafo",
            ).columns
        )

        for trafo_index, row in result_table.iterrows():

            try:
                asset_id = self._asset_id(
                    "trafo",
                    trafo_index,
                )

            except KeyError:
                continue

            transformer_states[
                asset_id
            ] = self._create_transformer_state(
                asset_id,
                trafo_index,
                row,
                has_tap,
            )

        return transformer_states

    def _create_transformer_state(
        self,
        asset_id: UUID,
        trafo_index: int,
        row,
        has_tap: bool,
    ) -> TransformerState:
        """
        Construct a TransformerState.
        """
        tap_position = 0

        if has_tap:

            trafo_table = self._table(
                "trafo",
            )

            tap_value = trafo_table.loc[
                trafo_index,
                "tap_pos",
            ]

            if pd.isna(tap_value):
                tap_position = 0
            else:
                tap_position = int(tap_value)

        loading = self._float(
            row.loading_percent,
        )

        return TransformerState(

            asset_id=asset_id,

            loading_percent=loading,

            tap_position=tap_position,
        )

    #
    # ------------------------------------------------------------------
    # Load Mapping
    # ------------------------------------------------------------------
    #

    def _map_load_results(
        self,
    ) -> dict[UUID, LoadState]:
        """
        Map solved pandapower load results.
        """

        load_states: dict[
            UUID,
            LoadState,
        ] = {}

        if not self._has_table("res_load"):
            return load_states

        table = self._table("res_load")

        if table.empty:
            return load_states

        for load_index, row in table.iterrows():

            try:
                asset_id = self._asset_id(
                    "load",
                    load_index,
                )

            except KeyError:
                continue

            load_states[
                asset_id
            ] = self._create_load_state(
                asset_id,
                row,
            )

        return load_states

    def _create_load_state(
        self,
        asset_id: UUID,
        row,
    ) -> LoadState:
        """
        Construct a LoadState.
        """

        p = self._float(
            row.p_mw,
        )

        q = self._float(
            row.q_mvar,
        )

        #
        # Pandapower reports solved load powers
        # directly from the res_load table.
        #
        return LoadState(
            asset_id=asset_id,
            active_power_mw=p,
            reactive_power_mvar=q,
            online=True,
        )

    #
    # ------------------------------------------------------------------
    # Generator Mapping
    # ------------------------------------------------------------------
    #

    def _create_generator_state(
        self,
        asset_id: UUID,
        row,
    ) -> GeneratorState:
        """
        Construct a GeneratorState from either a pandapower
        `res_gen` or `res_sgen` result row.
        """

        p = self._float(
            row.p_mw,
        )

        q = self._float(
            row.q_mvar,
        )

        vm = (
            self._float(row.vm_pu)
            if "vm_pu" in row.index
            else 1.0
        )

        return GeneratorState(
            asset_id=asset_id,
            active_power_mw=p,
            reactive_power_mvar=q,
            voltage_setpoint_pu=vm,
            online=True,
        )

    def _map_generator_results(
        self,
    ) -> dict[UUID, GeneratorState,]:
        """
        Map solved pandapower generator results.

        GridStudio generators may be represented in pandapower as either

            * gen
            * sgen

        depending on whether they are voltage-controlled.

        Both result tables are merged into one canonical
        GeneratorState dictionary.

        Solar and Wind assets are intentionally skipped here.
        They will receive dedicated state collections later.
        """

        generator_states: dict[UUID, GeneratorState,] = {}

        #
        # Voltage-controlled generators
        #

        self._map_der_table(
            table_name="res_gen",
            mapping_table="gen",
            asset_type="generator",
            target=generator_states,
            state_factory=self._create_generator_state,
        )

        #
        # Static generators
        #

        self._map_der_table(
            table_name="res_sgen",
            mapping_table="sgen",
            asset_type="generator",
            target=generator_states,
            state_factory=self._create_generator_state,
        )

        return generator_states

    def _map_der_table(
        self,
        *,
        table_name: str,
        mapping_table: str,
        asset_type: str,
        target: dict[UUID, Any],
        state_factory,
    ) -> None:
        """
        Map one pandapower DER result table.
        """

        if not self._has_table(table_name):
            return

        table = self._table(table_name)

        if table.empty:
            return

        for index, row in table.iterrows():

            try:
                asset_id = self._asset_id(
                    mapping_table,
                    index,
                )
            except KeyError:
                continue

            if self._asset_type(asset_id) != asset_type:
                continue

            target[asset_id] = state_factory(
                asset_id,
                row,
            )


    def _map_solar_results(
        self,
    ) -> dict[UUID, SolarState]:
        """
        Map solar generators from pandapower.

        Solar assets may be represented by pandapower
        either as voltage-controlled ``gen`` elements
        or as ``sgen`` elements.
        """

        states: dict[UUID, SolarState] = {}

        self._map_der_table(
            table_name="res_gen",
            mapping_table="gen",
            asset_type="solar",
            target=states,
            state_factory=self._create_solar_state,
        )

        self._map_der_table(
            table_name="res_sgen",
            mapping_table="sgen",
            asset_type="solar",
            target=states,
            state_factory=self._create_solar_state,
        )

        return states


    #
    # ------------------------------------------------------------------
    # Solar Mapping
    # ------------------------------------------------------------------
    #

    def _create_solar_state(
        self,
        asset_id: UUID,
        row,
    ) -> SolarState:
        """
        Build a SolarState from one res_sgen row.
        """

        return SolarState(
            asset_id=asset_id,
            active_power_mw=self._float(row.p_mw),
            reactive_power_mvar=self._float(row.q_mvar),
            online=True,
        )

    #
    # ------------------------------------------------------------------
    # Wind Mapping
    # ------------------------------------------------------------------
    #
    def _map_wind_results(
        self,
    ) -> dict[UUID, WindState]:
        """
        Map wind generators from pandapower.

        Wind assets may be represented by pandapower
        either as voltage-controlled ``gen`` elements
        or as ``sgen`` elements.
        """

        states: dict[UUID, WindState] = {}

        self._map_der_table(
            table_name="res_gen",
            mapping_table="gen",
            asset_type="wind",
            target=states,
            state_factory=self._create_wind_state,
        )

        self._map_der_table(
            table_name="res_sgen",
            mapping_table="sgen",
            asset_type="wind",
            target=states,
            state_factory=self._create_wind_state,
        )

        return states
    
    def _create_wind_state(
        self,
        asset_id: UUID,
        row,
    ) -> WindState:
        """
        Build a WindState from one res_sgen row.
        """

        return WindState(
            asset_id=asset_id,
            active_power_mw=self._float(row.p_mw),
            reactive_power_mvar=self._float(row.q_mvar),
            online=True,
        )
    #
    # ------------------------------------------------------------------
    # Storage Mapping
    # ------------------------------------------------------------------
    #

    def _map_storage_results(
        self,
    ) -> tuple[
        dict[UUID, BatteryState],
        dict[UUID, EVState],
    ]:
        """
        Map solved storage results.

        Batteries and EVs share the pandapower
        storage table and are separated using the
        asset_type recorded during conversion.
        """

        battery_states: dict[
            UUID,
            BatteryState,
        ] = {}

        ev_states: dict[
            UUID,
            EVState,
        ] = {}

        if not self._has_table("res_storage"):
            return (
                battery_states,
                ev_states,
            )

        table = self._table(
            "res_storage",
        )

        if table.empty:
            return (
                battery_states,
                ev_states,
            )

        for storage_index, row in table.iterrows():

            try:
                asset_id = self._asset_id(
                    "storage",
                    storage_index,
                )

            except KeyError:
                continue

            asset_type = self._asset_type(
                asset_id,
            )

            if asset_type == "battery":

                battery_states[
                    asset_id
                ] = self._create_battery_state(
                    asset_id,
                    row,
                )

            elif asset_type == "ev":

                ev_states[
                    asset_id
                ] = self._create_ev_state(
                    asset_id,
                    row,
                )

        return (
            battery_states,
            ev_states,
        )

    def _create_battery_state(
        self,
        asset_id: UUID,
        row,
    ) -> BatteryState:
        """
        Construct BatteryState.
        """

        p = self._float(
            row.p_mw,
        )

        q = self._float(
            row.q_mvar,
        )

        return BatteryState(

            asset_id=asset_id,

            active_power_mw=p,

            reactive_power_mvar=q,

            online=True,
        )

    def _create_ev_state(
        self,
        asset_id: UUID,
        row,
    ) -> EVState:
        """
        Construct EVState.
        """

        p = self._float(
            row.p_mw,
        )

        q = self._float(
            row.q_mvar,
        )

        return EVState(

            asset_id=asset_id,

            active_power_mw=p,

            reactive_power_mvar=q,

            online=True,
        )

    #
    # ------------------------------------------------------------------
    # Shunt Mapping
    # ------------------------------------------------------------------
    #

    def _map_shunt_results(
        self,
    ) -> dict[
        UUID,
        ShuntState,
    ]:
        """
        Map solved shunt results.
        """

        shunt_states: dict[
            UUID,
            ShuntState,
        ] = {}

        if not self._has_table("res_shunt"):
            return shunt_states

        table = self._table(
            "res_shunt",
        )

        if table.empty:
            return shunt_states

        for shunt_index, row in table.iterrows():

            try:
                asset_id = self._asset_id(
                    "shunt",
                    shunt_index,
                )

            except KeyError:
                continue

            shunt_states[
                asset_id
            ] = self._create_shunt_state(
                asset_id,
                row,
            )

        return shunt_states

    def _create_shunt_state(
        self,
        asset_id: UUID,
        row,
    ) -> ShuntState:
        """
        Construct ShuntState.
        """

        #
        # Pandapower reports solved shunt injections
        # directly from the res_shunt table.
        #
        p = self._float(
            row.p_mw,
        )

        q = self._float(
            row.q_mvar,
        )

        return ShuntState(

            asset_id=asset_id,

            active_power_mw=p,

            reactive_power_mvar=q,

            online=True,
        )

    # ------------------------------------------------------------------
    # Convergence
    # ------------------------------------------------------------------
    #

    def _map_convergence(
        self,
    ) -> ConvergenceInfo:
        """
        Map Pandapower convergence information.

        Pandapower stores the solver iteration count in the
        internal power-flow case and the configured convergence
        tolerance in the solver options.
        """

        return ConvergenceInfo(
            converged=bool(
                self._pp_net.converged,
            ),
            iterations=int(
                self._pp_net._ppc["iterations"],
            ),
            tolerance=float(
                self._pp_net._options["tolerance_mva"],
            ),
            message=None,
        )

    #
    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    #

    def _compute_generation_statistics(
        self,
    ) -> dict[str, float]:
        """
        Compute aggregate generation statistics.
        """

        active_generation = 0.0
        reactive_generation = 0.0

        if self._has_table("res_gen"):

            table = self._table("res_gen")

            active_generation += self._float(
                table.p_mw.sum(),
            )

            reactive_generation += self._float(
                table.q_mvar.sum(),
            )

        if self._has_table("res_sgen"):

            table = self._table("res_sgen")

            active_generation += self._float(
                table.p_mw.sum(),
            )

            reactive_generation += self._float(
                table.q_mvar.sum(),
            )

        if self._has_table("res_ext_grid"):

            table = self._table("res_ext_grid")

            active_generation += self._float(
                table.p_mw.sum(),
            )

            reactive_generation += self._float(
                table.q_mvar.sum(),
            )

        return {
            "total_active_generation_mw": active_generation,
            "total_reactive_generation_mvar": reactive_generation,
        }


    def _compute_load_statistics(
        self,
    ) -> dict[str, float]:
        """
        Compute aggregate load statistics.
        """

        active_load = 0.0
        reactive_load = 0.0

        if self._has_table("res_load"):

            table = self._table("res_load")

            active_load = self._float(
                table.p_mw.sum(),
            )

            reactive_load = self._float(
                table.q_mvar.sum(),
            )

        return {
            "total_active_load_mw": active_load,
            "total_reactive_load_mvar": reactive_load,
        }

    def _compute_loss_statistics(
        self,
    ) -> dict[str, float]:
        """
        Compute aggregate branch loss statistics.
        """

        active_loss = 0.0
        reactive_loss = 0.0

        if self._has_table("res_line"):

            table = self._table("res_line")

            active_loss = self._float(
                table.pl_mw.sum(),
            )

            reactive_loss = self._float(
                table.ql_mvar.sum(),
            )

        return {
            "total_active_loss_mw": active_loss,
            "total_reactive_loss_mvar": reactive_loss,
        }

    def _compute_voltage_statistics(
        self,
    ) -> dict[str, float]:
        """
        Compute bus voltage statistics.
        """

        minimum_voltage = 0.0
        maximum_voltage = 0.0
        average_voltage = 0.0

        if self._has_table("res_bus"):

            table = self._table("res_bus")

            if not table.empty:

                minimum_voltage = self._float(
                    table.vm_pu.min(),
                )

                maximum_voltage = self._float(
                    table.vm_pu.max(),
                )

                average_voltage = self._float(
                    table.vm_pu.mean(),
                )

        return {
            "minimum_bus_voltage_pu": minimum_voltage,
            "maximum_bus_voltage_pu": maximum_voltage,
            "average_bus_voltage_pu": average_voltage,
        }

    def _compute_branch_statistics(
        self,
    ) -> dict[str, float]:
        """
        Compute aggregate branch loading statistics.
        """

        maximum_loading = 0.0

        if self._has_table("res_line"):

            table = self._table("res_line")

            if not table.empty:

                maximum_loading = self._float(
                    table.loading_percent.max(),
                )

        return {
            "maximum_branch_loading_percent": maximum_loading,
        }

    def _compute_power_factor(
        self,
        statistics: dict[str, float],
    ) -> dict[str, float]:
        """
        Compute overall system power factor.
        """

        active_power = statistics[
            "total_active_generation_mw"
        ]

        reactive_power = statistics[
            "total_reactive_generation_mvar"
        ]

        apparent_power = math.sqrt(
            active_power * active_power
            + reactive_power * reactive_power
        )

        if apparent_power <= 0.0:

            power_factor = 1.0

        else:

            power_factor = (
                active_power
                / apparent_power
            )

        return {
            "system_power_factor": power_factor,
        }

    def _build_statistics(
        self,
    ) -> dict[str, float]:
        """
        Compute aggregate network statistics.
        """

        statistics: dict[
            str,
            float,
        ] = {}

        statistics.update(
            self._compute_generation_statistics(),
        )

        statistics.update(
            self._compute_load_statistics(),
        )

        statistics.update(
            self._compute_loss_statistics(),
        )

        statistics.update(
            self._compute_voltage_statistics(),
        )

        statistics.update(
            self._compute_branch_statistics(),
        )

        statistics.update(
            self._compute_power_factor(
                statistics,
            ),
        )

        return statistics


    #
    # ------------------------------------------------------------------
    # PowerFlowResult Construction
    # ------------------------------------------------------------------
    #

    def _build_map_result(
        self,
        *,
        bus_states: dict[UUID, BusState],
        branch_states: dict[UUID, BranchState],
        transformer_states: dict[UUID, TransformerState],
        load_states: dict[UUID, LoadState],
        generator_states: dict[UUID, GeneratorState],
        solar_states: dict[UUID, SolarState],
        wind_states: dict[UUID, WindState],
        battery_states: dict[UUID, BatteryState],
        ev_states: dict[UUID, EVState],
        shunt_states: dict[UUID, ShuntState],
        convergence: ConvergenceInfo,
        statistics: dict[str, float],
    ) -> PandapowerMappingResult:
        """
        Assemble the immutable PowerFlowResult.
        """

        return PandapowerMappingResult(
 
            #
            # Convergence
            #
            convergence=convergence,
            statistics=statistics,

            #
            # State dictionaries
            #
            bus_states=bus_states,
            branch_states=branch_states,
            transformer_states=transformer_states,
            load_states=load_states,
            generator_states=generator_states,
            solar_states=solar_states,
            wind_states=wind_states,
            battery_states=battery_states,
            ev_states=ev_states,
            shunt_states=shunt_states,
           
        )

    #
    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    #

    def map(
        self,
        pp_net,
        conversion: PandapowerConversion,
    ) -> PandapowerMappingResult:
        """
        Convert solved pandapower results into
        GridStudio simulation models.
        """

        self._initialize(
            pp_net,
            conversion,
        )

        #
        # Network states
        #

        bus_states = self._map_bus_results()
        branch_states = self._map_branch_results()
        transformer_states = self._map_transformer_results()

        #
        # Injection states
        #

        load_states = self._map_load_results()
        generator_states = self._map_generator_results()
        solar_states = self._map_solar_results()
        wind_states = self._map_wind_results()
        shunt_states = self._map_shunt_results()

        battery_states, ev_states = self._map_storage_results()


        #
        # Diagnostics
        #

        convergence = self._map_convergence()
        statistics = self._build_statistics()

        #
        # Final immutable result
        #

        return self._build_map_result(
            bus_states=bus_states,
            branch_states=branch_states,
            transformer_states=transformer_states,
            load_states=load_states,
            generator_states=generator_states,
            solar_states=solar_states,
            wind_states=wind_states,
            battery_states=battery_states,
            ev_states=ev_states,
            shunt_states=shunt_states,
            convergence=convergence,
            statistics=statistics,
        )


__all__ = [
    "PandapowerResultMapper",
]

