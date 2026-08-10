"""
GridStudio AI

Module:
    simulation.py

Description:
    Core enumerations describing solver-independent simulation
    and engineering-study concepts used throughout GridStudio AI.

    These enumerations define what type of engineering study is
    being performed, how the study is executed, and the high-level
    status of its execution.

    Numerical algorithms and solver-specific methods must not be
    represented in this module. Those concepts belong to the
    simulation engine layer.

Author:
    Rajesh Murari

License:
    MIT
"""

from __future__ import annotations

from enum import StrEnum


# ============================================================================
# Engineering Study Type
# ============================================================================


class StudyType(StrEnum):
    """
    Engineering study performed by GridStudio AI.

    POWER_FLOW
        Steady-state network power-flow analysis.

    OPTIMAL_POWER_FLOW
        Power-flow analysis with an optimization objective and
        operating constraints.

    SHORT_CIRCUIT
        Fault-current and short-circuit analysis.

    STATE_ESTIMATION
        Estimation of the electrical network state from available
        measurements and network information.

    CONTINGENCY
        Assessment of network performance following equipment
        outages or other contingency events.

    HOSTING_CAPACITY
        Assessment of the network's ability to accommodate
        additional DER, load, EV, storage, or other resources
        without violating defined operating constraints.

    RELIABILITY
        Assessment of network reliability and service continuity.

    PROTECTION
        Protection-system analysis and coordination studies.

    HARMONIC
        Harmonic and power-quality frequency-domain analysis.

    DYNAMIC
        Time-domain dynamic or transient network analysis.

    Notes
    -----
    StudyType identifies the engineering problem being solved.

    It does not identify the numerical algorithm or software
    engine used to perform the study.
    """

    POWER_FLOW = "power_flow"
    OPTIMAL_POWER_FLOW = "optimal_power_flow"
    SHORT_CIRCUIT = "short_circuit"
    STATE_ESTIMATION = "state_estimation"
    CONTINGENCY = "contingency"
    HOSTING_CAPACITY = "hosting_capacity"
    RELIABILITY = "reliability"
    PROTECTION = "protection"
    HARMONIC = "harmonic"
    DYNAMIC = "dynamic"


# ============================================================================
# Simulation Mode
# ============================================================================


class SimulationMode(StrEnum):
    """
    Execution mode of an engineering study.

    SNAPSHOT
        Study performed for one network operating condition.

    TIME_SERIES
        Study performed across an ordered sequence of timestamps
        or operating conditions.

    MONTE_CARLO
        Study performed repeatedly using sampled uncertain or
        stochastic inputs.

    SCENARIO
        Study performed across one or more explicitly defined
        operating or planning scenarios.

    Notes
    -----
    SimulationMode describes how a study is executed.

    For example:

        StudyType.POWER_FLOW + SimulationMode.SNAPSHOT

    represents a conventional snapshot power-flow study, while:

        StudyType.POWER_FLOW + SimulationMode.TIME_SERIES

    represents a time-series power-flow study.

    Contingency is intentionally represented as a StudyType rather
    than a SimulationMode because contingency analysis is an
    engineering study with its own inputs, outputs, and assessment
    logic.
    """

    SNAPSHOT = "snapshot"
    TIME_SERIES = "time_series"
    MONTE_CARLO = "monte_carlo"
    SCENARIO = "scenario"


# ============================================================================
# Simulation Status
# ============================================================================


class SimulationStatus(StrEnum):
    """
    Lifecycle status of a simulation or engineering study.

    PENDING
        Simulation has been created but execution has not started.

    RUNNING
        Simulation is currently executing.

    COMPLETED
        Simulation completed successfully.

    FAILED
        Simulation terminated because of an error.

    CANCELLED
        Simulation was cancelled before normal completion.
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ============================================================================
# Convergence Status
# ============================================================================


class ConvergenceStatus(StrEnum):
    """
    High-level numerical convergence status.

    NOT_RUN
        Numerical solution has not yet been attempted.

    CONVERGED
        Numerical solution satisfied the required convergence
        criteria.

    NOT_CONVERGED
        Numerical solution completed or terminated without
        satisfying the required convergence criteria.

    NOT_APPLICABLE
        Convergence is not meaningful for the corresponding study
        or operation.

    Notes
    -----
    Detailed convergence information such as iteration count,
    residuals, tolerances, and termination reasons belongs in
    simulation result models rather than this enumeration.
    """

    NOT_RUN = "not_run"
    CONVERGED = "converged"
    NOT_CONVERGED = "not_converged"
    NOT_APPLICABLE = "not_applicable"


# ============================================================================
# Result Status
# ============================================================================


class ResultStatus(StrEnum):
    """
    High-level validity status of a simulation result.

    VALID
        Result was successfully produced and passed required
        validation checks.

    PARTIAL
        Result contains useful information but is incomplete.

    INVALID
        Result was produced but failed required validation or
        consistency checks.

    UNAVAILABLE
        No usable result is available.

    Notes
    -----
    ResultStatus is distinct from SimulationStatus.

    A simulation may technically complete while producing an
    invalid or non-converged engineering result.
    """

    VALID = "valid"
    PARTIAL = "partial"
    INVALID = "invalid"
    UNAVAILABLE = "unavailable"


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "ConvergenceStatus",
    "ResultStatus",
    "SimulationMode",
    "SimulationStatus",
    "StudyType",
]