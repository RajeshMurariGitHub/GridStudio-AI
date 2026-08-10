"""
GridStudio AI

Module:
    io.py

Description:
    Core enumerations describing solver-independent input, output,
    serialization, and electrical-network data formats used
    throughout GridStudio AI.

    These enumerations describe how network and study data are
    represented externally. They do not describe the electrical
    representation of a network or the simulation engine used to
    solve it.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from enum import StrEnum


# ============================================================================
# Network Data Format
# ============================================================================


class NetworkFormat(StrEnum):
    """
    External electrical-network data format.

    GRIDSTUDIO
        Native GridStudio AI network representation.

    PANDAPOWER
        pandapower network representation.

    OPENDSS
        OpenDSS network representation.

    MATPOWER
        MATPOWER case representation.

    CIM
        IEC Common Information Model representation.

    JSON
        Generic JSON-based network representation.

    CSV
        Tabular CSV-based network representation.

    Notes
    -----
    NetworkFormat describes the external representation from which
    a network is imported or to which it is exported.

    It does not determine whether the electrical network is balanced
    or unbalanced. That distinction is represented independently by
    NetworkRepresentation.

    It also does not select the simulation engine.

    For example:

        NetworkFormat.OPENDSS

    describes an OpenDSS-formatted network, while:

        NetworkRepresentation.UNBALANCED

    describes the electrical representation of that network.
    """

    GRIDSTUDIO = "gridstudio"
    PANDAPOWER = "pandapower"
    OPENDSS = "opendss"
    MATPOWER = "matpower"
    CIM = "cim"
    JSON = "json"
    CSV = "csv"


# ============================================================================
# Generic File Format
# ============================================================================


class FileFormat(StrEnum):
    """
    Generic file or serialization format.

    JSON
        JavaScript Object Notation.

    CSV
        Comma-separated values.

    EXCEL
        Microsoft Excel workbook.

    PARQUET
        Apache Parquet columnar data format.

    YAML
        YAML structured-data format.

    XML
        Extensible Markup Language.

    TEXT
        Plain-text representation.

    Notes
    -----
    FileFormat describes the physical or serialization format of
    general GridStudio AI data.

    It is intentionally separate from NetworkFormat.

    For example, time-series measurements may be stored as CSV or
    Parquet without representing an electrical network.
    """

    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    PARQUET = "parquet"
    YAML = "yaml"
    XML = "xml"
    TEXT = "text"


# ============================================================================
# Data Encoding
# ============================================================================


class DataEncoding(StrEnum):
    """
    Character encoding used for text-based external data.

    UTF8
        UTF-8 character encoding.

    UTF16
        UTF-16 character encoding.

    ASCII
        ASCII character encoding.

    Notes
    -----
    UTF-8 should normally be the default for GridStudio AI
    text-based files.
    """

    UTF8 = "utf-8"
    UTF16 = "utf-16"
    ASCII = "ascii"


# ============================================================================
# Import Behavior
# ============================================================================


class ImportMode(StrEnum):
    """
    High-level behavior when importing data.

    CREATE
        Create a new GridStudio representation from imported data.

    MERGE
        Merge imported information with an existing representation.

    UPDATE
        Update matching existing objects using imported information.

    Notes
    -----
    Detailed conflict-resolution and identity-matching policies
    should be implemented by importer configuration rather than
    continually expanding this enumeration.
    """

    CREATE = "create"
    MERGE = "merge"
    UPDATE = "update"


# ============================================================================
# Export Behavior
# ============================================================================


class ExportMode(StrEnum):
    """
    High-level behavior when exporting data.

    OVERWRITE
        Replace an existing destination when permitted.

    FAIL_IF_EXISTS
        Refuse export when the destination already exists.

    Notes
    -----
    Append behavior is intentionally not defined here because
    appending is not meaningful or safe for every supported
    GridStudio AI data representation.
    """

    OVERWRITE = "overwrite"
    FAIL_IF_EXISTS = "fail_if_exists"


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "DataEncoding",
    "ExportMode",
    "FileFormat",
    "ImportMode",
    "NetworkFormat",
]