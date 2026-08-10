"""
GridStudio AI

Module:
    validation.py

Description:
    Validates benchmark datasets before they are
    converted into GridStudio network models.

    The validator performs structural validation only.

    No electrical calculations are performed.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from collections.abc import Iterable

from .types import (
    BenchmarkDataset,
)


class BenchmarkValidationError(ValueError):
    """
    Raised when a benchmark dataset is invalid.
    """


class BenchmarkValidator:
    """
    Validates benchmark datasets.
    """

    @staticmethod
    def validate(
        dataset: BenchmarkDataset,
    ) -> None:
        """
        Validate a benchmark dataset.

        Raises
        ------
        BenchmarkValidationError
            If the dataset is invalid.
        """

        BenchmarkValidator._validate_unique_bus_numbers(
            dataset,
        )

        BenchmarkValidator._validate_unique_branch_numbers(
            dataset,
        )

        BenchmarkValidator._validate_branch_endpoints(
            dataset,
        )

        BenchmarkValidator._validate_load_buses(
            dataset,
        )

        BenchmarkValidator._validate_generator_buses(
            dataset,
        )

    #
    # -------------------------------------------------------------
    # Internal validation methods
    # -------------------------------------------------------------
    #

    @staticmethod
    def _validate_unique_bus_numbers(
        dataset: BenchmarkDataset,
    ) -> None:

        BenchmarkValidator._validate_unique(
            (
                bus.bus_number
                for bus in dataset.buses
            ),
            "Duplicate bus numbers found.",
        )

    @staticmethod
    def _validate_unique_branch_numbers(
        dataset: BenchmarkDataset,
    ) -> None:

        BenchmarkValidator._validate_unique(
            (
                branch.branch_number
                for branch in dataset.branches
            ),
            "Duplicate branch numbers found.",
        )

    @staticmethod
    def _validate_branch_endpoints(
        dataset: BenchmarkDataset,
    ) -> None:

        bus_numbers = {
            bus.bus_number
            for bus in dataset.buses
        }

        for branch in dataset.branches:

            if branch.from_bus_number not in bus_numbers:

                raise BenchmarkValidationError(
                    f"Branch {branch.branch_number} "
                    f"references unknown "
                    f"from-bus "
                    f"{branch.from_bus_number}."
                )

            if branch.to_bus_number not in bus_numbers:

                raise BenchmarkValidationError(
                    f"Branch {branch.branch_number} "
                    f"references unknown "
                    f"to-bus "
                    f"{branch.to_bus_number}."
                )

    @staticmethod
    def _validate_load_buses(
        dataset: BenchmarkDataset,
    ) -> None:

        bus_numbers = {
            bus.bus_number
            for bus in dataset.buses
        }

        for load in dataset.loads:

            if load.bus_number not in bus_numbers:

                raise BenchmarkValidationError(
                    f"Load {load.load_number} "
                    f"references unknown "
                    f"bus {load.bus_number}."
                )

    @staticmethod
    def _validate_generator_buses(
        dataset: BenchmarkDataset,
    ) -> None:

        bus_numbers = {
            bus.bus_number
            for bus in dataset.buses
        }

        for generator in dataset.generators:

            if generator.bus_number not in bus_numbers:

                raise BenchmarkValidationError(
                    f"Generator "
                    f"{generator.generator_number} "
                    f"references unknown "
                    f"bus {generator.bus_number}."
                )

    @staticmethod
    def _validate_unique(
        values: Iterable[int],
        message: str,
    ) -> None:

        values = list(values)

        if len(values) != len(set(values)):

            raise BenchmarkValidationError(
                message,
            )