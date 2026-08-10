"""
GridStudio AI

Module:
    equipment.py

Description:
    Core enumerations describing electrical equipment and
    distributed energy resource classifications used throughout
    GridStudio AI.

    These enumerations describe physical or functional equipment
    categories and remain independent of simulation engines,
    optimization algorithms, and external software platforms.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from enum import StrEnum


# ============================================================================
# Generator Classification
# ============================================================================


class GeneratorType(StrEnum):
    """
    Generator technology classification.

    SYNCHRONOUS
        Conventional synchronous electrical generator.

    ASYNCHRONOUS
        Induction or asynchronous generator.

    INVERTER_BASED
        Generic inverter-interfaced generation where a more
        specific technology classification is unavailable.

    OTHER
        Generator technology not represented by the currently
        defined categories.

    Notes
    -----
    Solar and wind technologies have dedicated domain models and
    classifications. INVERTER_BASED is retained for generic
    inverter-connected generation that does not belong to those
    dedicated models.
    """

    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    INVERTER_BASED = "inverter_based"
    OTHER = "other"


# ============================================================================
# Load Classification
# ============================================================================


class LoadType(StrEnum):
    """
    Electrical load classification.

    RESIDENTIAL
        Residential or domestic demand.

    COMMERCIAL
        Commercial demand.

    INDUSTRIAL
        Industrial demand.

    AGRICULTURAL
        Agricultural demand such as irrigation and pumping loads.

    MUNICIPAL
        Municipal or public-service demand.

    MIXED
        Aggregated load containing multiple customer classes.

    OTHER
        Load that does not belong to another defined category.

    Notes
    -----
    This classification describes the customer or usage category,
    not the mathematical load model.

    Constant-power, constant-current, constant-impedance, ZIP, and
    other mathematical load representations should be modeled
    separately.
    """

    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    AGRICULTURAL = "agricultural"
    MUNICIPAL = "municipal"
    MIXED = "mixed"
    OTHER = "other"


class LoadModel(StrEnum):
    """
    Electrical behavior model used to represent a load.

    CONSTANT_POWER
        Constant complex-power (PQ) load.

    CONSTANT_CURRENT
        Load whose current magnitude remains approximately constant
        as terminal voltage varies.

    CONSTANT_IMPEDANCE
        Load represented by constant impedance.

    ZIP
        Composite load model combining constant-impedance,
        constant-current, and constant-power components.

    Notes
    -----
    LoadModel describes the mathematical/electrical behavior of a
    load.

    It is intentionally separate from LoadType, which describes the
    customer or usage classification such as residential,
    commercial, or industrial.
    """

    CONSTANT_POWER = "constant_power"
    CONSTANT_CURRENT = "constant_current"
    CONSTANT_IMPEDANCE = "constant_impedance"
    ZIP = "zip"

# ============================================================================
# Transformer Classification
# ============================================================================


class TransformerType(StrEnum):
    """
    Functional transformer classification.

    POWER
        Transformer primarily used for bulk power transfer.

    DISTRIBUTION
        Transformer primarily used in distribution networks.

    AUTOTRANSFORMER
        Transformer with electrically connected windings.

    REGULATING
        Transformer primarily used for voltage regulation.

    ISOLATION
        Transformer primarily used for electrical isolation.

    GROUNDING
        Transformer primarily used to establish or modify
        grounding characteristics.

    OTHER
        Transformer not represented by another defined category.

    Notes
    -----
    This enumeration describes transformer function.

    Winding connections, vector groups, tap configuration,
    grounding, ratings, and electrical parameters belong in the
    Transformer domain model.
    """

    POWER = "power"
    DISTRIBUTION = "distribution"
    AUTOTRANSFORMER = "autotransformer"
    REGULATING = "regulating"
    ISOLATION = "isolation"
    GROUNDING = "grounding"
    OTHER = "other"


# ============================================================================
# Switch Classification
# ============================================================================


class SwitchType(StrEnum):
    """
    Electrical switching-device classification.

    SWITCH
        Generic switching device.

    BREAKER
        Circuit breaker capable of interrupting fault current.

    DISCONNECTOR
        Isolation device normally operated without significant
        load current.

    LOAD_BREAK_SWITCH
        Switching device capable of interrupting normal load
        current.

    FUSE
        Protective switching device using a fusible element.

    RECLOSER
        Automatic reclosing protective switching device.

    SECTIONALIZER
        Device used to isolate faulted distribution sections.

    CONTACTOR
        Electrically controlled switching device.

    OTHER
        Switching device not represented by another category.
    """

    SWITCH = "switch"
    BREAKER = "breaker"
    DISCONNECTOR = "disconnector"
    LOAD_BREAK_SWITCH = "load_break_switch"
    FUSE = "fuse"
    RECLOSER = "recloser"
    SECTIONALIZER = "sectionalizer"
    CONTACTOR = "contactor"
    OTHER = "other"


# ============================================================================
# Shunt Classification
# ============================================================================


class ShuntType(StrEnum):
    """
    Shunt-device classification.

    CAPACITOR
        Capacitive shunt compensation.

    REACTOR
        Inductive shunt compensation.

    STATIC_VAR_COMPENSATOR
        Static VAR compensator.

    STATCOM
        Static synchronous compensator.

    OTHER
        Shunt-connected equipment not represented by another
        defined category.

    Notes
    -----
    DSTATCOM can be represented by STATCOM together with network
    context rather than introducing solver-specific or duplicate
    electrical-device concepts.
    """

    CAPACITOR = "capacitor"
    REACTOR = "reactor"
    STATIC_VAR_COMPENSATOR = "static_var_compensator"
    STATCOM = "statcom"
    OTHER = "other"


# ============================================================================
# Solar Technology
# ============================================================================


class SolarTechnology(StrEnum):
    """
    Solar photovoltaic technology classification.

    MONOCRYSTALLINE
        Monocrystalline silicon photovoltaic technology.

    POLYCRYSTALLINE
        Polycrystalline silicon photovoltaic technology.

    THIN_FILM
        Thin-film photovoltaic technology.

    BIFACIAL
        Bifacial photovoltaic technology.

    OTHER
        Solar technology not represented by another category.
    """

    MONOCRYSTALLINE = "monocrystalline"
    POLYCRYSTALLINE = "polycrystalline"
    THIN_FILM = "thin_film"
    BIFACIAL = "bifacial"
    OTHER = "other"


# ============================================================================
# Wind Technology
# ============================================================================


class WindTechnology(StrEnum):
    """
    Wind-generation technology classification.

    FIXED_SPEED
        Fixed-speed wind turbine.

    VARIABLE_SPEED
        Variable-speed wind turbine.

    DFIG
        Doubly-fed induction generator based turbine.

    FULL_CONVERTER
        Wind turbine using a full-scale power electronic
        converter.

    OTHER
        Wind technology not represented by another category.
    """

    FIXED_SPEED = "fixed_speed"
    VARIABLE_SPEED = "variable_speed"
    DFIG = "dfig"
    FULL_CONVERTER = "full_converter"
    OTHER = "other"


# ============================================================================
# Battery Technology
# ============================================================================


class BatteryTechnology(StrEnum):
    """
    Battery energy-storage technology classification.

    LITHIUM_ION
        Lithium-ion battery technology.

    LEAD_ACID
        Lead-acid battery technology.

    FLOW
        Flow-battery technology.

    SODIUM_SULFUR
        Sodium-sulfur battery technology.

    SOLID_STATE
        Solid-state battery technology.

    OTHER
        Battery technology not represented by another category.
    """

    LITHIUM_ION = "lithium_ion"
    LEAD_ACID = "lead_acid"
    FLOW = "flow"
    SODIUM_SULFUR = "sodium_sulfur"
    SOLID_STATE = "solid_state"
    OTHER = "other"


# ============================================================================
# Electric Vehicle Classification
# ============================================================================


class EVType(StrEnum):
    """
    Electric-vehicle classification.

    BEV
        Battery electric vehicle.

    PHEV
        Plug-in hybrid electric vehicle.

    ELECTRIC_BUS
        Battery-powered electric bus.

    ELECTRIC_TRUCK
        Battery-powered electric truck.

    OTHER
        Electric vehicle not represented by another category.
    """

    BEV = "bev"
    PHEV = "phev"
    ELECTRIC_BUS = "electric_bus"
    ELECTRIC_TRUCK = "electric_truck"
    OTHER = "other"


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "BatteryTechnology",
    "EVType",
    "GeneratorType",
    "LoadModel",
    "LoadType",
    "ShuntType",
    "SolarTechnology",
    "SwitchType",
    "TransformerType",
    "WindTechnology",
]