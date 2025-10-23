"""
Modular Timetable Solver Package

Provides clean, modular OR-Tools CP-SAT solver for academic timetable generation.
"""

from .solver_modular import (
    ModularTimetableSolver,
    generate_timetable,
    generate_time_slots,
    check_feasibility
)

__all__ = [
    "ModularTimetableSolver",
    "generate_timetable",
    "generate_time_slots",
    "check_feasibility"
]
