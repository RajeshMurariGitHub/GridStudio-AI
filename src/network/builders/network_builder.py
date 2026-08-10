"""
GridStudio

Module:
    network_builder.py

Description:
    Fluent builder used to construct Network aggregate roots.

Author:
    Rajesh Murari

License:
    MIT

Python:
    >=3.12
"""

from __future__ import annotations

from src.domain.network.network import Network

from src.domain import (
    Battery,
    Bus,
    ElectricVehicle,
    Generator,
    Line,
    Load,
    Shunt,
    Solar,
    Switch,
    Transformer,
    Wind,
)


class NetworkBuilder:
    """
    Builder for Network aggregate roots.

    The builder incrementally assembles a Network and
    finally returns the completed immutable object.
    """

    def __init__(
        self,
        *,
        name: str,
        description: str | None = None,
        base_power_mva: float = 100.0,
        base_frequency_hz: float = 50.0,
    ) -> None:

        self._network = Network(
            name=name,
            description=description,
            base_power_mva=base_power_mva,
            base_frequency_hz=base_frequency_hz,
        )

        #

    # ---------------------------------------------------------
    # Buses
    # ---------------------------------------------------------
    #

    def add_bus(
        self,
        bus: Bus,
    ) -> "NetworkBuilder":

        self._network.add_bus(bus)

        return self

    #
    # ---------------------------------------------------------
    # Lines
    # ---------------------------------------------------------
    #

    def add_line(
        self,
        line: Line,
    ) -> "NetworkBuilder":

        self._network.add_line(line)

        return self

    #
    # ---------------------------------------------------------
    # Transformers
    # ---------------------------------------------------------
    #

    def add_transformer(
        self,
        transformer: Transformer,
    ) -> "NetworkBuilder":

        self._network.add_transformer(transformer)

        return self

    #
    # ---------------------------------------------------------
    # Switches
    # ---------------------------------------------------------
    #

    def add_switch(
        self,
        switch: Switch,
    ) -> "NetworkBuilder":

        self._network.add_switch(switch)

        return self

    #
    # ---------------------------------------------------------
    # Generators
    # ---------------------------------------------------------
    #

    def add_generator(
        self,
        generator: Generator,
    ) -> "NetworkBuilder":

        self._network.add_generator(generator)

        return self

    #
    # ---------------------------------------------------------
    # Loads
    # ---------------------------------------------------------
    #

    def add_load(
        self,
        load: Load,
    ) -> "NetworkBuilder":

        self._network.add_load(load)

        return self

    #
    # ---------------------------------------------------------
    # Batteries
    # ---------------------------------------------------------
    #

    def add_battery(
        self,
        battery: Battery,
    ) -> "NetworkBuilder":

        self._network.add_battery(battery)

        return self

    #
    # ---------------------------------------------------------
    # Solar
    # ---------------------------------------------------------
    #

    def add_solar(
        self,
        solar: Solar,
    ) -> "NetworkBuilder":

        self._network.add_solar(solar)

        return self

    #
    # ---------------------------------------------------------
    # Wind
    # ---------------------------------------------------------
    #
    def add_wind(
        self,
        wind: Wind,
    ) -> "NetworkBuilder":

        self._network.add_wind(wind)

        return self

    #
    # ---------------------------------------------------------
    # Electric Vehicles
    # ---------------------------------------------------------
    #

    def add_electric_vehicle(
        self,
        ev: ElectricVehicle,
    ) -> "NetworkBuilder":

        self._network.add_electric_vehicle(ev)

        return self

    #
    # ---------------------------------------------------------
    # Shunts
    # ---------------------------------------------------------
    #

    def add_shunt(
        self,
        shunt: Shunt,
    ) -> "NetworkBuilder":

        self._network.add_shunt(shunt)

        return self

    #
    # ---------------------------------------------------------
    # Finalization
    # ---------------------------------------------------------
    #

    def build(
        self,
    ) -> Network:
        """
        Return the completed network.
        """

        return self._network

    @property
    def network(self) -> Network:
        """
        Return the partially constructed network without
        finalizing the build.
        """
        return self._network
