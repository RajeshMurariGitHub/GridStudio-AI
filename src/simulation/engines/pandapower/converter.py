"""
GridStudio AI

Module:
    converter.py

Description:
    Conversion layer between the canonical GridStudio electrical
    domain model and pandapower.

    The converter translates solver-independent GridStudio domain
    objects into a pandapower network without introducing
    pandapower-specific concepts into the domain layer.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from src.domain.bus import Bus
from src.domain.load import Load
from src.domain.injection import Injection
from src.domain.line import Line
from src.domain.generator import Generator
from src.domain.shunt import Shunt
from src.domain.transformer import Transformer
from src.domain.switch import Switch
from src.domain.solar import Solar
from src.domain.wind import Wind
from src.domain.battery import Battery
from src.domain.ev import EV
from src.domain.network.network import Network

from src.simulation.models.requests.reference_source import (
    ReferenceSource,
)
from .dependencies import import_pandapower


# ============================================================================
# Conversion Result
# ============================================================================
@dataclass(frozen=True, slots=True)
class PandapowerElementMapping:
    """
    Location of a converted GridStudio element in pandapower.

    Parameters
    ----------
    table
        pandapower element table containing the converted element.

    index
        Row index of the converted element within that table.
    """

    table: str
    index: int
    asset_type: str

@dataclass(slots=True)
class PandapowerConversion:
    """
    Result of converting a GridStudio Network to pandapower.

    Parameters
    ----------
    network
        Native pandapower network.

    bus_indices
        Mapping from GridStudio bus UUIDs to pandapower bus indices.

    element_indices
        Mapping from GridStudio element UUIDs to pandapower table
        indices.

    Notes
    -----
    pandapower uses integer DataFrame indices internally, whereas
    GridStudio uses stable UUID identifiers.

    The mappings retained here allow simulation results to be mapped
    back to the original GridStudio domain objects.
    """

    network: Any

    bus_indices: dict[UUID, int] = field(
        default_factory=dict
    )

    # Backward-compatible UUID -> row-index mapping.
    element_indices: dict[UUID, int] = field(
        default_factory=dict
    )

    # Unambiguous UUID -> pandapower table/index mapping.
    element_mappings: dict[
        UUID,
        PandapowerElementMapping,
    ] = field(
        default_factory=dict
    )


# ============================================================================
# Converter
# ============================================================================


class PandapowerConverter:
    """
    Convert a canonical GridStudio Network into pandapower.

    The converter is intentionally state-free. Each call to
    ``convert`` creates a new pandapower network and corresponding
    UUID-to-index mappings.

    Responsibilities
    ----------------
    The converter is responsible for:

    * creating the pandapower network,
    * converting GridStudio buses,
    * converting supported branches,
    * converting supported injections,
    * translating GridStudio sign conventions,
    * retaining UUID-to-pandapower index mappings.

    The converter is not responsible for:

    * running power flow,
    * choosing simulation algorithms,
    * interpreting solver convergence,
    * mapping solver results back to GridStudio result models.

    Those responsibilities belong to ``engine.py`` and
    ``result_mapper.py``.
    """

    # ------------------------------------------------------------------
    # Public Conversion API
    # ------------------------------------------------------------------

    @classmethod
    def convert(
        cls,
        network: Network,
        *,
        reference_sources: tuple[
            ReferenceSource,
            ...,
        ] = ()
    ) -> PandapowerConversion:
        """
        Convert a GridStudio network into pandapower.

        Parameters
        ----------
        network
            Canonical GridStudio electrical network.

        reference_sources
            Solver-independent electrical reference sources for the
            power-flow study.

            Each reference source is represented in pandapower using an
            ``ext_grid`` element.

        Returns
        -------
        PandapowerConversion
            Native pandapower network and UUID/index mappings.
        """

        pp = import_pandapower()

        pp_network = pp.create_empty_network(
            name=network.name,
            f_hz=network.base_frequency_hz,
        )

        conversion = PandapowerConversion(
            network=pp_network
        )

        cls._convert_buses(
            pp=pp,
            source=network,
            target=conversion,
        )

        cls._convert_reference_sources(
            pp=pp,
            reference_sources=reference_sources,
            target=conversion,
        )

        cls._convert_lines(
            pp=pp,
            source=network,
            target=conversion,
        )

        cls._convert_transformers(
            pp=pp,
            source=network,
            target=conversion,
        )   

        cls._convert_switches(
            pp=pp,
            source=network,
            target=conversion,
        )  

        cls._convert_loads(
            pp=pp,
            source=network,
            target=conversion,
        )    

        cls._convert_generators(
            pp=pp,
            source=network,
            target=conversion,
        )

        cls._convert_solar(
            pp=pp,
            source=network,
            target=conversion,
        )

        cls._convert_wind(
            pp=pp,
            source=network,
            target=conversion,
        )

        cls._convert_batteries(
            pp=pp,
            source=network,
            target=conversion,
        )       

        cls._convert_evs(
            pp=pp,
            source=network,
            target=conversion,
        )           

        cls._convert_shunts(
            pp=pp,
            source=network,
            target=conversion,
        )

        cls._convert_injections(
            pp=pp,
            source=network,
            target=conversion,
        )

        return conversion

    # ------------------------------------------------------------------
    # Bus Conversion
    # ------------------------------------------------------------------

    @classmethod
    def _convert_buses(
        cls,
        *,
        pp: Any,
        source: Network,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert all GridStudio buses.
        """

        for bus in source.buses:
            cls._convert_bus(
                pp=pp,
                bus=bus,
                target=target,
            )

    @staticmethod
    def _convert_bus(
        *,
        pp: Any,
        bus: Bus,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert one GridStudio Bus.
        """

        index = pp.create_bus(
            target.network,
            vn_kv=bus.nominal_voltage_kv,
            name=bus.name,
            in_service=bus.is_operational,
        )

        target.bus_indices[bus.id] = index

        PandapowerConverter._register_element_mapping(
            element_id=bus.id,
            table="bus",
            index=index,
            asset_type="bus",
            conversion=target,
        )

    # ------------------------------------------------------------------
    # Reference-Source Conversion
    # ------------------------------------------------------------------

    @classmethod
    def _convert_reference_sources(
        cls,
        *,
        pp: Any,
        reference_sources: tuple[
            ReferenceSource,
            ...,
        ],
        target: PandapowerConversion,
    ) -> None:
        """
        Convert electrical reference sources to pandapower.

        Reference sources are simulation configuration rather than
        physical GridStudio network elements.

        pandapower represents an electrical reference source using
        an ``ext_grid`` element.

        Each reference source fixes the voltage magnitude and phase
        angle at its associated bus for the power-flow study.
        """

        for reference_source in reference_sources:
            cls._convert_reference_source(
                pp=pp,
                reference_source=reference_source,
                target=target,
            )

    @classmethod
    def _convert_reference_source(
        cls,
        *,
        pp: Any,
        reference_source: ReferenceSource,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert one GridStudio reference source to pandapower.

        The referenced GridStudio bus must already have been
        converted so that its pandapower bus index can be resolved.

        Reference sources are not added to ``element_indices``
        because they are study configuration rather than physical
        GridStudio network elements.
        """

        bus_index = cls._require_bus_index(
            reference_source.bus_id,
            target,
        )

        pp.create_ext_grid(
            target.network,
            bus=bus_index,
            vm_pu=reference_source.voltage_magnitude_pu,
            va_degree=reference_source.voltage_angle_deg,
            name="GridStudio Reference Source",
            in_service=True,
        )

    # ------------------------------------------------------------------
    # Loads Conversion
    # ------------------------------------------------------------------

    @classmethod
    def _convert_loads(
        cls,
        *,
        pp: Any,
        source: Network,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert GridStudio loads to pandapower loads.
        """

        for load in source.loads:
            cls._convert_load(
                pp=pp,
                load=load,
                target=target,
            )


    @classmethod
    def _convert_load(
        cls,
        *,
        pp: Any,
        load: Load,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert one GridStudio Load to a pandapower load.

        GridStudio stores load powers in MW/Mvar, which matches
        pandapower's load power units directly.

        The GridStudio scaling factor is passed through without
        pre-scaling the power values.
        """

        bus_index = target.bus_indices.get(
            load.node_id
        )

        if bus_index is None:
            return

        load_index = pp.create_load(
            target.network,
            bus=bus_index,
            p_mw=-load.active_power_mw,
            q_mvar=-load.reactive_power_mvar,
            scaling=load.scaling,
            name=load.name,
            in_service=load.is_operational,
        )

        cls._register_element_mapping(
            element_id=load.id,
            table="load",
            index=load_index,
            asset_type="load",
            conversion=target,
        )


    # ------------------------------------------------------------------
    # Generator Conversion
    # ------------------------------------------------------------------

    @classmethod
    def _convert_generators(
        cls,
        *,
        pp: Any,
        source: Network,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert GridStudio base Generator elements.

        Specialized Generator subclasses such as Solar and Wind are excluded
        here because they have dedicated conversion paths.

        Non-voltage-controlled generators are represented using
        pandapower ``sgen``.

        Voltage-controlled generators are represented using
        pandapower ``gen``.
        """

        for generator in source.generators:

            # Specialized Generator subclasses also appear in the
            # Network generator collection through inheritance.
            # They have dedicated conversion paths and must not be
            # converted here.
            if isinstance(
                generator, 
                (Solar, Wind),
            ):
                continue

            cls._convert_generator(
                pp=pp,
                generator=generator,
                target=target,
            )

    @classmethod
    def _convert_generator(
        cls,
        *,
        pp: Any,
        generator: Generator,
        asset_type: str = "generator",
        target: PandapowerConversion,
    ) -> None:
        """
        Convert one GridStudio Generator.

        GridStudio and pandapower both use positive active power for
        generation, so no active-power sign conversion is required.

        The GridStudio scaling factor is passed through for static
        generators rather than pre-scaling the base power values.

        Voltage-controlled generators use pandapower ``gen`` because
        their terminal voltage magnitude is an explicit controlled
        quantity.
        """

        bus_index = cls._require_bus_index(
            generator.node_id,
            target,
        )

        if generator.is_voltage_controlled:
            index = cls._convert_voltage_controlled_generator(
                pp=pp,
                generator=generator,
                bus_index=bus_index,
                target=target,
            )
            table = "gen"
        else:
            index = cls._convert_static_generator(
                pp=pp,
                generator=generator,
                bus_index=bus_index,
                target=target,
            )
            table = "sgen"

        cls._register_element_mapping(
            element_id=generator.id,
            table=table,
            index=index,
            asset_type=asset_type,
            conversion=target,
        )

    @staticmethod
    def _convert_static_generator(
        *,
        pp: Any,
        generator: Generator,
        bus_index: int,
        target: PandapowerConversion,
    ) -> int:
        """
        Convert a non-voltage-controlled Generator to pandapower sgen.
        """

        kwargs: dict[str, Any] = {
            "net": target.network,
            "bus": bus_index,
            "p_mw": generator.active_power_mw,
            "q_mvar": generator.reactive_power_mvar,
            "scaling": generator.scaling,
            "name": generator.name,
            "in_service": generator.is_operational,
        }

        if generator.rated_power_mva is not None:
            kwargs["sn_mva"] = generator.rated_power_mva

        if generator.maximum_active_power_mw is not None:
            kwargs["max_p_mw"] = (
                generator.maximum_active_power_mw
            )

        kwargs["min_p_mw"] = (
            generator.minimum_active_power_mw
        )

        if generator.minimum_reactive_power_mvar is not None:
            kwargs["min_q_mvar"] = (
                generator.minimum_reactive_power_mvar
            )

        if generator.maximum_reactive_power_mvar is not None:
            kwargs["max_q_mvar"] = (
                generator.maximum_reactive_power_mvar
            )

        return pp.create_sgen(**kwargs)

    @staticmethod
    def _convert_voltage_controlled_generator(
        *,
        pp: Any,
        generator: Generator,
        bus_index: int,
        target: PandapowerConversion,
    ) -> int:
        """
        Convert a voltage-controlled Generator to pandapower gen.
        """

        if generator.voltage_setpoint_pu is None:
            raise ValueError(
                "Voltage-controlled generator requires "
                "voltage_setpoint_pu."
            )

        kwargs: dict[str, Any] = {
            "net": target.network,
            "bus": bus_index,
            "p_mw": generator.active_power_mw,
            "vm_pu": generator.voltage_setpoint_pu,
            "name": generator.name,
            "in_service": generator.is_operational,
        }

        if generator.rated_power_mva is not None:
            kwargs["sn_mva"] = generator.rated_power_mva

        if generator.maximum_active_power_mw is not None:
            kwargs["max_p_mw"] = (
                generator.maximum_active_power_mw
            )

        kwargs["min_p_mw"] = (
            generator.minimum_active_power_mw
        )

        if generator.minimum_reactive_power_mvar is not None:
            kwargs["min_q_mvar"] = (
                generator.minimum_reactive_power_mvar
            )

        if generator.maximum_reactive_power_mvar is not None:
            kwargs["max_q_mvar"] = (
                generator.maximum_reactive_power_mvar
            )

        return pp.create_gen(**kwargs)


    # ------------------------------------------------------------------
    # Solar Conversion
    # ------------------------------------------------------------------

    @classmethod
    def _convert_solar(
        cls,
        *,
        pp: Any,
        source: Network,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert the GridStudio Solar collection.

        Solar inherits Generator electrical semantics.

        Non-voltage-controlled PV resources are represented using
        pandapower ``sgen``.

        Voltage-controlled PV resources are represented using
        pandapower ``gen``.
        """

        for solar in source.solar:
            cls._convert_solar_element(
                pp=pp,
                solar=solar,
                target=target,
            )

    @classmethod
    def _convert_solar_element(
        cls,
        *,
        pp: Any,
        solar: Solar,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert one GridStudio Solar resource.

        Solar uses the Generator network-injection convention, so its
        configured P/Q setpoints can use the existing Generator
        conversion boundary directly.

        PV-specific resource properties such as DC capacity,
        available active power, and curtailment remain GridStudio
        domain information and are not mapped to unrelated pandapower
        fields.
        """

        cls._convert_generator(
            pp=pp,
            generator=solar,
            target=target,
            asset_type="solar",
        )


    # ------------------------------------------------------------------
    # Wind Conversion
    # ------------------------------------------------------------------

    @classmethod
    def _convert_wind(
        cls,
        *,
        pp: Any,
        source: Network,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert the GridStudio Wind collection.

        Wind inherits Generator electrical semantics.

        Non-voltage-controlled wind resources are represented using
        pandapower ``sgen``.

        Voltage-controlled wind resources are represented using
        pandapower ``gen``.
        """

        for wind in source.wind:
            cls._convert_wind_element(
                pp=pp,
                wind=wind,
                target=target,
            )

    @classmethod
    def _convert_wind_element(
        cls,
        *,
        pp: Any,
        wind: Wind,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert one GridStudio Wind resource.

        Wind uses the Generator network-injection convention, so its
        configured P/Q setpoints can use the existing Generator
        conversion boundary directly.

        Wind-specific resource properties such as installed active
        power, available active power, wind-speed characteristics,
        curtailment capability, and reactive-control capability remain
        GridStudio domain information and are not mapped to unrelated
        pandapower fields.
        """

        cls._convert_generator(
            pp=pp,
            generator=wind,
            target=target,
            asset_type="wind",
        )

    # ------------------------------------------------------------------
    # Battery Conversion
    # ------------------------------------------------------------------

    @classmethod
    def _convert_batteries(
        cls,
        *,
        pp: Any,
        source: Network,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert GridStudio batteries to pandapower storage elements.

        GridStudio Battery uses the canonical network-injection
        convention:

            positive P = battery discharge into the network
            negative P = battery charging from the network

        pandapower storage uses the consumer-reference convention:

            positive p_mw = charging
            negative p_mw = discharging

        Active-power signs are therefore reversed at the conversion
        boundary.
        """

        for battery in source.batteries:
            cls._convert_battery(
                pp=pp,
                battery=battery,
                target=target,
            )

    @classmethod
    def _convert_battery(
        cls,
        *,
        pp: Any,
        battery: Battery,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert one GridStudio Battery to pandapower storage.

        GridStudio stores SOC as a fraction from 0 to 1, whereas
        pandapower storage represents SOC as percent.

        GridStudio scaling is passed through without pre-scaling the
        configured active or reactive power.

        Battery charge/discharge efficiencies and sequential SOC
        evolution remain GridStudio domain/time-series concerns and
        are not embedded into the steady-state pandapower element.
        """

        bus_index = cls._require_bus_index(
            battery.node_id,
            target,
        )

        kwargs: dict[str, Any] = {
            "net": target.network,
            "bus": bus_index,

            # GridStudio:
            #   +P = discharge
            #   -P = charge
            #
            # pandapower storage:
            #   +P = charge
            #   -P = discharge
            "p_mw": -battery.active_power_mw,

            # GridStudio uses network-injection Q while pandapower
            # storage follows the consumer-reference convention.
            "q_mvar": -battery.reactive_power_mvar,

            "max_e_mwh": battery.energy_capacity_mwh,
            "soc_percent": (
                battery.state_of_charge * 100.0
            ),
            "scaling": battery.scaling,
            "name": battery.name,
            "in_service": battery.is_operational,

            # pandapower storage P limits use its own sign convention.
            #
            # Maximum discharge:
            # GridStudio +P -> pandapower negative P
            "min_p_mw": -battery.maximum_discharge_power_mw,

            # Maximum charge:
            # GridStudio -P -> pandapower positive P
            "max_p_mw": battery.maximum_charge_power_mw,
        }

        if battery.rated_power_mva is not None:
            kwargs["sn_mva"] = battery.rated_power_mva

        # Reactive-power limits cross the same sign boundary as the
        # configured reactive-power setpoint.
        #
        # GridStudio:
        #   +Q = injection
        #   -Q = absorption
        #
        # pandapower storage:
        #   +Q = absorption
        #   -Q = injection
        #
        # Therefore GridStudio [Qmin, Qmax] becomes
        # pandapower [-Qmax, -Qmin].

        if battery.maximum_reactive_power_mvar is not None:
            kwargs["min_q_mvar"] = (
                -battery.maximum_reactive_power_mvar
            )

        if battery.minimum_reactive_power_mvar is not None:
            kwargs["max_q_mvar"] = (
                -battery.minimum_reactive_power_mvar
            )

        index = pp.create_storage(
            **kwargs
        )

        cls._register_element_mapping(
            element_id=battery.id,
            table="storage",
            index=index,
            asset_type="battery",
            conversion=target,
        )


    # ------------------------------------------------------------------
    # EV Conversion
    # ------------------------------------------------------------------

    @classmethod
    def _convert_evs(
        cls,
        *,
        pp: Any,
        source: Network,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert GridStudio electric vehicles to pandapower storage.

        GridStudio EV uses the canonical network-injection convention:

            positive P = V2G discharge into the network
            negative P = charging from the network

        pandapower storage uses the consumer-reference convention:

            positive p_mw = charging
            negative p_mw = discharging

        Active- and reactive-power signs are therefore reversed at
        the conversion boundary.
        """

        for ev in source.evs:
            cls._convert_ev(
                pp=pp,
                ev=ev,
                target=target,
            )

    @classmethod
    def _convert_ev(
        cls,
        *,
        pp: Any,
        ev: EV,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert one GridStudio EV to pandapower storage.

        GridStudio stores SOC as a fraction from 0 to 1, whereas
        pandapower storage represents SOC as percent.

        EV charging/discharging efficiencies, mobility state, and
        sequential SOC evolution remain GridStudio domain/time-series
        concerns and are not embedded into the steady-state
        pandapower element.
        """

        bus_index = cls._require_bus_index(
            ev.node_id,
            target,
        )

        kwargs: dict[str, Any] = {
            "net": target.network,
            "bus": bus_index,

            # GridStudio:
            #   +P = V2G discharge
            #   -P = charging
            #
            # pandapower storage:
            #   +P = charging
            #   -P = discharging
            "p_mw": -ev.active_power_mw,

            # GridStudio:
            #   +Q = injection
            #   -Q = absorption
            #
            # pandapower storage uses the opposite convention.
            "q_mvar": -ev.reactive_power_mvar,

            "max_e_mwh": ev.battery_capacity_mwh,
            "soc_percent": (
                ev.state_of_charge * 100.0
            ),
            "scaling": ev.scaling,
            "name": ev.name,

            # A disconnected EV must not participate electrically,
            # even if the asset itself is otherwise operational.
            "in_service": (
                ev.is_operational
                and ev.is_connected
            ),

            # Maximum V2G discharge:
            # GridStudio +P -> pandapower negative P
            "min_p_mw": -ev.maximum_discharge_power_mw,

            # Maximum charging:
            # GridStudio -P -> pandapower positive P
            "max_p_mw": ev.maximum_charge_power_mw,
        }

        if ev.rated_power_mva is not None:
            kwargs["sn_mva"] = ev.rated_power_mva

        # GridStudio [Qmin, Qmax] becomes pandapower
        # [-Qmax, -Qmin].
        if ev.maximum_reactive_power_mvar is not None:
            kwargs["min_q_mvar"] = (
                -ev.maximum_reactive_power_mvar
            )

        if ev.minimum_reactive_power_mvar is not None:
            kwargs["max_q_mvar"] = (
                -ev.minimum_reactive_power_mvar
            )

        index = pp.create_storage(
            **kwargs
        )

        cls._register_element_mapping(
            element_id=ev.id,
            table="storage",
            index=index,
            asset_type="ev",
            conversion=target,
        )


    # ------------------------------------------------------------------
    # Shunt Conversion
    # ------------------------------------------------------------------

    @classmethod
    def _convert_shunts(
        cls,
        *,
        pp: Any,
        source: Network,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert GridStudio shunts to pandapower shunts.
        """

        for shunt in source.shunts:
            cls._convert_shunt(
                pp=pp,
                shunt=shunt,
                target=target,
            )

    @classmethod
    def _convert_shunt(
        cls,
        *,
        pp: Any,
        shunt: Shunt,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert one GridStudio Shunt to a pandapower shunt.

        Sign Convention
        ---------------
        GridStudio uses the network-injection convention:

            positive Q = reactive-power injection
            negative Q = reactive-power absorption

        pandapower shunts use the load-reference convention:

            negative q_mvar = capacitive injection
            positive q_mvar = inductive absorption

        The reactive-power sign is therefore reversed at the
        conversion boundary.

        Step Representation
        -------------------
        GridStudio stores the total bank rating together with the
        total and active step counts.

        pandapower stores shunt power per step and separately tracks
        the active step count and maximum number of steps.

        GridStudio scaling is incorporated into the per-step rating
        because pandapower shunts do not expose the same scaling
        mechanism used by pandapower load and sgen elements.
        """

        bus_index = cls._require_bus_index(
            shunt.node_id,
            target,
        )

        p_per_step_mw = (
            shunt.active_power_mw
            / shunt.step_count
            * shunt.scaling
        )

        q_per_step_mvar = (
            -shunt.reactive_power_per_step_mvar
            * shunt.scaling
        )

        kwargs: dict[str, Any] = {
            "net": target.network,
            "bus": bus_index,
            "q_mvar": q_per_step_mvar,
            "p_mw": p_per_step_mw,
            "step": shunt.active_steps,
            "max_step": shunt.step_count,
            "name": shunt.name,
            "in_service": shunt.is_operational,
        }

        if shunt.nominal_voltage_kv is not None:
            bus = target.network.bus.loc[bus_index]
            bus_nominal_voltage_kv = float(bus["vn_kv"])

            kwargs["vn_kv"] = shunt.nominal_voltage_kv

            if (
                abs(
                    shunt.nominal_voltage_kv
                    - bus_nominal_voltage_kv
                )
                > 1e-9
            ):
                raise ValueError(
                    f"Shunt {shunt.id} nominal voltage "
                    f"{shunt.nominal_voltage_kv} kV does not match "
                    f"connected bus nominal voltage "
                    f"{bus_nominal_voltage_kv} kV."
                )

        index = pp.create_shunt(
            **kwargs
        )

        cls._register_element_mapping(
            element_id=shunt.id,
            table="shunt",
            index=index,
            asset_type="shunt",
            conversion=target,
        )

    # ------------------------------------------------------------------
    # Line Conversion
    # ------------------------------------------------------------------

    @classmethod
    def _convert_lines(
        cls,
        *,
        pp: Any,
        source: Network,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert all GridStudio lines.
        """

        for line in source.lines:
            cls._convert_line(
                pp=pp,
                line=line,
                target=target,
            )

    @classmethod
    def _convert_line(
        cls,
        *,
        pp: Any,
        line: Line,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert one GridStudio Line.
        """

        from_bus = cls._require_bus_index(
            line.from_node_id,
            target,
        )

        to_bus = cls._require_bus_index(
            line.to_node_id,
            target,
        )

        parameters = line.parameters

        kwargs: dict[str, Any] = {
            "net": target.network,
            "from_bus": from_bus,
            "to_bus": to_bus,
            "length_km": line.length_km,
            "r_ohm_per_km": parameters.r1_ohm_per_km,
            "x_ohm_per_km": parameters.x1_ohm_per_km,
            "c_nf_per_km": parameters.c1_nf_per_km,
            "max_i_ka": (
                line.maximum_current_ka
                if line.maximum_current_ka is not None
                else 1.0
            ),
            "parallel": line.parallel_count,
            "name": line.name,
            "in_service": line.is_operational,
        }

        index = pp.create_line_from_parameters(
            **kwargs
        )

        cls._register_element_mapping(
            element_id=line.id,
            table="line",
            index=index,
            asset_type="line",
            conversion=target,
        )

    # ------------------------------------------------------------------
    # Transformer Conversion
    # ------------------------------------------------------------------

    @classmethod
    def _convert_transformers(
        cls,
        *,
        pp,
        source: Network,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert GridStudio transformers into pandapower transformers.
        """

        for transformer in source.transformers:
            cls._convert_transformer(
                pp=pp,
                transformer=transformer,
                target=target,
            ) 

    @classmethod
    def _convert_transformer(
        cls,
        *,
        pp: Any,
        transformer: Transformer,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert one GridStudio two-winding Transformer.

        GridStudio transformer terminal convention:

            from_node_id -> high-voltage winding
            to_node_id   -> low-voltage winding

        The transformer is represented using pandapower's explicit
        parameter-based two-winding transformer model.
        """

        hv_bus = cls._require_bus_index(
            bus_id=transformer.high_voltage_node_id,
            conversion=target,
        )

        lv_bus = cls._require_bus_index(
            bus_id=transformer.low_voltage_node_id,
            conversion=target,
        )

        kwargs: dict[str, Any] = {
            "net": target.network,
            "hv_bus": hv_bus,
            "lv_bus": lv_bus,
            "sn_mva": transformer.rated_power_mva,
            "vn_hv_kv": transformer.high_voltage_kv,
            "vn_lv_kv": transformer.low_voltage_kv,
            "vk_percent": transformer.impedance_percent,
            "vkr_percent": transformer.resistance_percent,
            "pfe_kw": transformer.no_load_loss_kw,
            "i0_percent": transformer.exciting_current_percent,
            "shift_degree": transformer.phase_shift_deg,
            "name": transformer.name,
            "in_service": transformer.is_operational,
        }

        if transformer.has_tap_changer:
            kwargs.update(
                {
                    "tap_side": (
                        "hv"
                        if transformer.tap_on_high_voltage_side
                        else "lv"
                    ),
                    "tap_neutral": 0,
                    "tap_pos": transformer.tap_position,
                    "tap_step_percent": transformer.tap_step_percent,
                }
            )

            if transformer.minimum_tap_position is not None:
                kwargs["tap_min"] = (
                    transformer.minimum_tap_position
                )

            if transformer.maximum_tap_position is not None:
                kwargs["tap_max"] = (
                    transformer.maximum_tap_position
                )

        transformer_index = (
            pp.create_transformer_from_parameters(
                **kwargs
            )
        )

        cls._register_element_mapping(
            element_id=transformer.id,
            table="trafo",
            index=transformer_index,
            asset_type="transformer",
            conversion=target,
        )


    # ------------------------------------------------------------------
    # Switch Conversion
    # ------------------------------------------------------------------

    @classmethod
    def _convert_switches(
        cls,
        *,
        pp: Any,
        source: Network,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert GridStudio switches to pandapower bus-bus switches.
        """

        for switch in source.switches:
            cls._convert_switch(
                pp=pp,
                switch=switch,
                target=target,
            )


    @classmethod
    def _convert_switch(
        cls,
        *,
        pp: Any,
        switch: Switch,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert one GridStudio Switch to a pandapower bus-bus switch.

        GridStudio switches connect two network nodes directly.

        Ideal switches are represented using pandapower's bus-bus
        switch model.

        Non-ideal switches with explicit resistance or reactance are
        rejected because converting them to an ideal pandapower switch
        would discard electrical impedance.
        """

        if not switch.is_ideal:
            raise ValueError(
                f"Switch {switch.id} cannot be converted to a "
                "pandapower ideal switch because it has non-zero "
                "closed-state impedance: "
                f"R={switch.resistance_ohm} ohm, "
                f"X={switch.reactance_ohm} ohm."
            )

        from_bus = cls._require_bus_index(
            switch.from_node_id,
            target,
        )

        to_bus = cls._require_bus_index(
            switch.to_node_id,
            target,
        )

        kwargs: dict[str, Any] = {
            "net": target.network,
            "bus": from_bus,
            "element": to_bus,
            "et": "b",
            "closed": (
                switch.is_closed
                and switch.is_operational
            ),
            "name": switch.name,
        }

        if switch.rated_current_ka is not None:
            kwargs["in_ka"] = switch.rated_current_ka

        index = pp.create_switch(
            **kwargs
        )

        cls._register_element_mapping(
            element_id=switch.id,
            table="switch",
            index=index,
            asset_type="switch",
            conversion=target,
        )

    # ------------------------------------------------------------------
    # Injections Conversion
    # ------------------------------------------------------------------

    @classmethod
    def _convert_injections(
        cls,
        *,
        pp: Any,
        source: Network,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert generic injections not yet handled by specialized
        pandapower converters.

        Notes
        -----
        GridStudio uses positive values for network injection.

        pandapower ``sgen`` also represents generation as positive
        active power. Negative values therefore naturally represent
        consumption when a generic injection is represented using
        ``sgen``.

        Specialized equipment such as Load, Generator, Solar,
        Battery, EV, and Shunt will receive dedicated conversion
        paths as the pandapower adapter is expanded.
        """

        specialized_ids = cls._specialized_injection_ids(
            source
        )

        for injection in source.injections:
            if injection.id in specialized_ids:
                continue

            cls._convert_generic_injection(
                pp=pp,
                injection=injection,
                target=target,
            )

    @staticmethod
    def _specialized_injection_ids(
        network: Network,
    ) -> set[UUID]:
        """
        Return injection identifiers reserved for specialized
        converters.
        """

        return {
            element.id
            for collection in (
                network.loads,
                network.generators,
                network.solar,
                network.wind,
                network.shunts,
                network.batteries,
                network.evs,
            )
            for element in collection
        }

    @classmethod
    def _convert_generic_injection(
        cls,
        *,
        pp: Any,
        injection: Injection,
        target: PandapowerConversion,
    ) -> None:
        """
        Convert a generic GridStudio Injection to pandapower sgen.
        """

        bus_index = cls._require_bus_index(
            injection.node_id,
            target,
        )

        index = pp.create_sgen(
            target.network,
            bus=bus_index,
            p_mw=injection.effective_active_power_mw,
            q_mvar=injection.effective_reactive_power_mvar,
            name=injection.name,
            in_service=injection.is_operational,
        )

        cls._register_element_mapping(
            element_id=injection.id,
            table="sgen",
            index=index,
            asset_type="injection",
            conversion=target,
        )

    # ------------------------------------------------------------------
    # Mapping Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _register_element_mapping(
        *,
        element_id: UUID,
        table: str,
        index: int,
        asset_type: str,
        conversion: PandapowerConversion,
    ) -> None:
        """
        Register the pandapower location of a GridStudio element.

        ``element_indices`` is retained for backward compatibility.

        ``element_mappings`` additionally records the pandapower
        table so result mapping can resolve the element
        unambiguously.
        """

        conversion.element_indices[element_id] = index

        conversion.element_mappings[element_id] = (
            PandapowerElementMapping(
                table=table,
                index=index,
                asset_type=asset_type,
            )
        )

    @staticmethod
    def _require_bus_index(
        bus_id: UUID,
        conversion: PandapowerConversion,
    ) -> int:
        """
        Return the pandapower index for a GridStudio bus UUID.

        Raises
        ------
        ValueError
            If the referenced bus has not been converted.
        """

        try:
            return conversion.bus_indices[bus_id]
        except KeyError as exc:
            raise ValueError(
                "Cannot convert element because referenced "
                f"bus {bus_id} does not exist in the converted "
                "network."
            ) from exc

    # ------------------------------------------------------------------
    # Electrical Conversion Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _susceptance_to_capacitance_nf_per_km(
        susceptance_siemens_per_km: float,
        frequency_hz: float,
    ) -> float:
        """
        Convert shunt susceptance to capacitance.

        pandapower's line parameter API accepts capacitance in
        nF/km, whereas GridStudio stores line charging
        susceptance in S/km.

        B = 2 * pi * f * C
        """

        if susceptance_siemens_per_km == 0.0:
            return 0.0

        import math

        capacitance_f_per_km = (
            susceptance_siemens_per_km
            / (
                2.0
                * math.pi
                * frequency_hz
            )
        )

        return capacitance_f_per_km * 1e9


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "PandapowerElementMapping",
    "PandapowerConversion",
    "PandapowerConverter",
]