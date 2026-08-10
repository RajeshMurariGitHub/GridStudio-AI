"""
GridStudio

Module:
    constants.py

Description:
    Centralized application constants.

Author:
    Rajesh Murari

License:
    MIT

Python:
    >=3.12
"""

from __future__ import annotations

# Configuration File Extensions
CONFIG_FILE_EXTENSION = ".yaml"

PROJECT_CONFIG_FILE = "project.yaml"

NETWORK_CONFIG_FILE = "network.yaml"

SIMULATION_CONFIG_FILE = "simulation.yaml"

LOGGING_CONFIG_FILE = "logging.yaml"

# File Extensions

CSV_EXTENSION = ".csv"

JSON_EXTENSION = ".json"

PARQUET_EXTENSION = ".parquet"

XLSX_EXTENSION = ".xlsx"

PKL_EXTENSION = ".pkl"

LOG_EXTENSION = ".log"

# Default Directory Names
CONFIG_DIRECTORY_NAME = "configs"

DATA_DIRECTORY_NAME = "data"

MODELS_DIRECTORY_NAME = "models"

RESULTS_DIRECTORY_NAME = "results"

LOGS_DIRECTORY_NAME = "logs"

# Default Tolerance and Numerical Constants
DEFAULT_TOLERANCE = 1e-8

EPSILON = 1e-12

# Electrical System Constants
DEFAULT_BASE_MVA = 100.0

DEFAULT_FREQUENCY_HZ = 50.0

SECONDS_PER_MINUTE = 60

MINUTES_PER_HOUR = 60

HOURS_PER_DAY = 24

# Default Simulation Parameters
DEFAULT_MAX_ITERATIONS = 20

DEFAULT_RANDOM_SEED = 42

# Default Logging Parameters
DEFAULT_LOG_FILENAME = "gridstudio.log"

DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

# Public API
__all__ = [
    "CONFIG_FILE_EXTENSION",
    "PROJECT_CONFIG_FILE",
    "NETWORK_CONFIG_FILE",
    "SIMULATION_CONFIG_FILE",
    "LOGGING_CONFIG_FILE",
    "CSV_EXTENSION",
    "JSON_EXTENSION",
    "PARQUET_EXTENSION",
    "XLSX_EXTENSION",
    "PKL_EXTENSION",
    "LOG_EXTENSION",
    "CONFIG_DIRECTORY_NAME",
    "DATA_DIRECTORY_NAME",
    "MODELS_DIRECTORY_NAME",
    "RESULTS_DIRECTORY_NAME",
    "LOGS_DIRECTORY_NAME",
    "DEFAULT_TOLERANCE",
    "EPSILON",
    "DEFAULT_BASE_MVA",
    "DEFAULT_FREQUENCY_HZ",
    "SECONDS_PER_MINUTE",
    "MINUTES_PER_HOUR",
    "HOURS_PER_DAY",
    "DEFAULT_MAX_ITERATIONS",
    "DEFAULT_RANDOM_SEED",
    "DEFAULT_LOG_FILENAME",
    "DEFAULT_LOG_FORMAT",
]
