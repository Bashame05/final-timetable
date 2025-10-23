"""
Main timetable solver using OR-Tools CP-SAT
"""
from ortools.sat.python import cp_model
from typing import Dict, List, Tuple, Any, Optional
import logging

from .constraints import TimetableConstraints
from .utils import (
    generate_time_slots,
    is_slot_in_lunch_break,
    calculate_total_hours,
    check_feasibility,
    get_available_rooms_for_subject
)

logger = logging.getLogger(__name__)


class TimetableSolver:
    """
    Main solver for timetable generation using OR-Tools CP-SAT
    """

    def __init__(
        self,
        week_config: Dict[str, Any],
        rooms: List[Dict[str, Any]],
        subjects: List[Dict[str, Any]],
        special_sessions: Optional[Dict[str, Dict[str, Any]]] = None
    ):
        self.week_config = week_config
        self.rooms = rooms
        self.subjects = subjects
        self.special_sessions = special_sessions or {}

        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.variables = {}
        self.time_slots = []

    def generate_timetable(self) -> Tuple[bool, List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Main method to generate timetable
        
        Returns:
            (success: bool, timetable: list, conflicts: list)
        """
        logger.info("Starting timetable generation...")

        # Step 1: Generate time slots
        self._generate_time_slots()
        logger.info(f"Generated {len(self.time_slots)} time slots")

        # Step 2: Check feasibility
        feasible, message = self._check_feasibility()
        if not feasible:
            logger.warning(f"Problem not feasible: {message}")
            return False, [], [{"reason": message}]

        # Step 3: Create variables
        self._create_variables()
        logger.info(f"Created {len(self.variables)} variables")

        if len(self.variables) == 0:
            logger.error("No variables created")
            return False, [], [{"reason": "No valid variable combinations found"}]

        # Step 4: Add constraints
        self._add_constraints()
        logger.info("Constraints added")

        # Step 5: Solve
        success = self._solve()

        if success:
            timetable = self._extract_solution()
            logger.info(f"Generated timetable with {len(timetable)} slots")
            return True, timetable, []
        else:
            logger.warning("No feasible solution found")
            return False, [], [{"reason": "No feasible solution found"}]

    def _generate_time_slots(self) -> None:
        """
        Generate all time slots based on week configuration
        """
        self.time_slots = generate_time_slots(
            start_time=self.week_config["week_start_time"],
            end_time=self.week_config["week_end_time"],
            slot_duration=60,  # 1-hour slots
            lunch_start=self.week_config.get("lunch_start"),
            lunch_end=self.week_config.get("lunch_end"),
            working_days=self.week_config.get("working_days", ["Mon", "Tue", "Wed", "Thu", "Fri"])
        )

    def _check_feasibility(self) -> Tuple[bool, str]:
        """
        Check if the problem is feasible
        """
        total_hours = calculate_total_hours(self.subjects)
        available_slots = len(self.time_slots)
        working_days = len(self.week_config.get("working_days", []))

        return check_feasibility(total_hours, available_slots, working_days)

    def _create_variables(self) -> None:
        """
        Create CP-SAT variables for the problem
        """
        var_id = 0

        for subject in self.subjects:
            subject_name = subject["name"]
            subject_type = subject["type"]
            hours_per_week = subject["hours_per_week"]

            # Get available rooms for this subject
            available_rooms = get_available_rooms_for_subject(subject_type, self.rooms)

            for day, slot in self.time_slots:
                # Skip lunch break
                if is_slot_in_lunch_break(
                    slot,
                    self.week_config.get("lunch_start", "13:00"),
                    self.week_config.get("lunch_end", "14:00")
                ):
                    continue

                for room_name in available_rooms:
                    var_name = f"var_{var_id}"
                    var = self.model.NewBoolVar(var_name)

                    self.variables[var_name] = {
                        "var": var,
                        "subject": subject_name,
                        "subject_type": subject_type,
                        "room": room_name,
                        "day": day,
                        "slot": slot,
                        "hours": hours_per_week
                    }

                    var_id += 1

    def _add_constraints(self) -> None:
        """
        Add all constraints to the model
        """
        # Extract data for constraints
        rooms = [r["name"] for r in self.rooms]
        room_types = {r["name"]: r["type"] for r in self.rooms}
        subjects = {s["name"]: s["hours_per_week"] for s in self.subjects}
        subject_types = {s["name"]: s["type"] for s in self.subjects}
        days = list(set(day for day, _ in self.time_slots))
        slots = list(set(slot for _, slot in self.time_slots))

        # Add constraints
        TimetableConstraints.add_no_room_overlap(self.model, self.variables, rooms, slots)
        TimetableConstraints.add_subject_hours_constraint(self.model, self.variables, subjects)
        TimetableConstraints.add_room_type_constraint(
            self.model, self.variables, subject_types, room_types
        )
        TimetableConstraints.add_consecutive_hours_constraint(
            self.model, self.variables, slots, max_consecutive=2
        )

        # Add special session constraints if any
        if self.special_sessions:
            TimetableConstraints.add_special_session_constraint(
                self.model, self.variables, self.special_sessions
            )

    def _solve(self) -> bool:
        """
        Run the CP-SAT solver
        """
        logger.info("Running CP-SAT solver...")

        self.solver.parameters.max_time_in_seconds = 60.0
        self.solver.parameters.log_search_progress = False

        status = self.solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            logger.info("✅ Solution found!")
            return True
        else:
            logger.warning("❌ No feasible solution found")
            return False

    def _extract_solution(self) -> List[Dict[str, Any]]:
        """
        Extract the solution from the solver
        """
        timetable = []

        for var_name, var_data in self.variables.items():
            if self.solver.Value(var_data["var"]) == 1:
                timetable.append({
                    "day": var_data["day"],
                    "slot": var_data["slot"],
                    "subject": var_data["subject"],
                    "room": var_data["room"],
                    "type": var_data["subject_type"],
                    "teacher": None  # To be assigned by frontend or separate module
                })

        # Sort by day and slot
        day_order = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
        timetable.sort(key=lambda x: (day_order.get(x["day"], 7), x["slot"]))

        return timetable
