"""
Improved timetable solver with better optimization
"""
from ortools.sat.python import cp_model
from typing import Dict, List, Tuple, Any, Optional
import logging

from .utils import (
    generate_time_slots,
    is_slot_in_lunch_break,
    calculate_total_hours,
    check_feasibility,
    get_available_rooms_for_subject
)

logger = logging.getLogger(__name__)


class TimetableSolverV2:
    """
    Improved solver with optimization objectives for better timetable quality
    """

    def __init__(
        self,
        week_config: Dict[str, Any],
        rooms: List[Dict[str, Any]],
        subjects: List[Dict[str, Any]],
        special_sessions: Optional[Dict[str, Dict[str, Any]]] = None,
        num_batches: int = 3
    ):
        self.week_config = week_config
        self.rooms = rooms
        self.subjects = subjects
        self.special_sessions = special_sessions or {}
        self.num_batches = num_batches

        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.variables = {}
        self.time_slots = []

    def generate_timetable(self) -> Tuple[bool, List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Generate optimized timetable
        """
        logger.info("Starting improved timetable generation...")

        # Step 1: Generate time slots
        self._generate_time_slots()
        logger.info(f"Generated {len(self.time_slots)} time slots")

        # Step 2: Check feasibility
        feasible, message = self._check_feasibility()
        if not feasible:
            logger.warning(f"Problem not feasible: {message}")
            return False, [], [{"reason": message}]

        # Step 3: Create variables with batch distribution
        self._create_variables()
        logger.info(f"Created {len(self.variables)} variables")

        if len(self.variables) == 0:
            logger.error("No variables created")
            return False, [], [{"reason": "No valid variable combinations found"}]

        # Step 4: Add constraints
        self._add_constraints()
        logger.info("Constraints added")

        # Step 5: Add optimization objectives
        self._add_optimization_objectives()
        logger.info("Optimization objectives added")

        # Step 6: Solve
        success = self._solve()

        if success:
            timetable = self._extract_solution()
            logger.info(f"Generated optimized timetable with {len(timetable)} slots")
            return True, timetable, []
        else:
            logger.warning("No feasible solution found")
            return False, [], [{"reason": "No feasible solution found"}]

    def _generate_time_slots(self) -> None:
        """Generate all time slots"""
        self.time_slots = generate_time_slots(
            start_time=self.week_config["week_start_time"],
            end_time=self.week_config["week_end_time"],
            slot_duration=60,
            lunch_start=self.week_config.get("lunch_start"),
            lunch_end=self.week_config.get("lunch_end"),
            working_days=self.week_config.get("working_days", ["Mon", "Tue", "Wed", "Thu", "Fri"])
        )

    def _check_feasibility(self) -> Tuple[bool, str]:
        """Check if problem is feasible"""
        total_hours = calculate_total_hours(self.subjects)
        available_slots = len(self.time_slots) * self.num_batches
        working_days = len(self.week_config.get("working_days", []))

        return check_feasibility(total_hours, available_slots, working_days)

    def _create_variables(self) -> None:
        """Create variables with batch distribution"""
        var_id = 0

        for subject in self.subjects:
            subject_name = subject["name"]
            subject_type = subject["type"]
            hours_per_week = subject["hours_per_week"]

            available_rooms = get_available_rooms_for_subject(subject_type, self.rooms)

            # Distribute across batches
            for batch_id in range(1, self.num_batches + 1):
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
                            "batch": batch_id,
                            "hours": hours_per_week
                        }

                        var_id += 1

    def _add_constraints(self) -> None:
        """Add all constraints"""
        rooms = [r["name"] for r in self.rooms]
        room_types = {r["name"]: r["type"] for r in self.rooms}
        subjects = {s["name"]: s["hours_per_week"] for s in self.subjects}
        subject_types = {s["name"]: s["type"] for s in self.subjects}
        days = list(set(day for day, _ in self.time_slots))
        slots = list(set(slot for _, slot in self.time_slots))

        # No room overlap
        for room in rooms:
            for slot in slots:
                for day in days:
                    room_slot_vars = [
                        var_data["var"]
                        for var_name, var_data in self.variables.items()
                        if var_data.get("room") == room 
                        and var_data.get("slot") == slot
                        and var_data.get("day") == day
                    ]
                    if room_slot_vars:
                        self.model.Add(sum(room_slot_vars) <= 1)

        # No batch overlap
        for batch_id in range(1, self.num_batches + 1):
            for slot in slots:
                for day in days:
                    batch_slot_vars = [
                        var_data["var"]
                        for var_name, var_data in self.variables.items()
                        if var_data.get("batch") == batch_id
                        and var_data.get("slot") == slot
                        and var_data.get("day") == day
                    ]
                    if batch_slot_vars:
                        self.model.Add(sum(batch_slot_vars) <= 1)

        # Subject hours constraint
        for subject_name, hours in subjects.items():
            subject_vars = [
                var_data["var"]
                for var_name, var_data in self.variables.items()
                if var_data.get("subject") == subject_name
            ]
            if subject_vars:
                self.model.Add(sum(subject_vars) == hours)

        # Room type constraint
        for subject_name, subject_type in subject_types.items():
            for var_name, var_data in self.variables.items():
                if var_data.get("subject") == subject_name:
                    room_name = var_data.get("room")
                    room_type = room_types.get(room_name, "classroom")
                    
                    # Check if room type matches subject type
                    if subject_type == "theory" and room_type != "classroom":
                        self.model.Add(var_data["var"] == 0)
                    elif subject_type == "lab" and room_type != "lab":
                        self.model.Add(var_data["var"] == 0)

    def _add_optimization_objectives(self) -> None:
        """Add optimization objectives for better timetable quality"""
        # Objective 1: Spread classes across the week (minimize consecutive days)
        day_order = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
        
        # Prefer earlier slots in the day
        slot_order = {
            "09:00-10:00": 0, "10:00-11:00": 1, "11:00-12:00": 2,
            "14:00-15:00": 3, "15:00-16:00": 4
        }

        penalties = []
        for var_name, var_data in self.variables.items():
            day_penalty = day_order.get(var_data.get("day", "Mon"), 5)
            slot_penalty = slot_order.get(var_data.get("slot", "09:00-10:00"), 5)
            
            # Prefer morning slots and earlier days
            penalty = day_penalty * 10 + slot_penalty
            penalties.append(var_data["var"] * penalty)

        if penalties:
            self.model.Minimize(sum(penalties))

    def _solve(self) -> bool:
        """Run the solver with optimization"""
        logger.info("Running optimized CP-SAT solver...")

        self.solver.parameters.max_time_in_seconds = 120.0
        self.solver.parameters.log_search_progress = False
        self.solver.parameters.num_workers = 4  # Use multiple workers

        status = self.solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            logger.info("✅ Optimized solution found!")
            return True
        else:
            logger.warning("❌ No feasible solution found")
            return False

    def _extract_solution(self) -> List[Dict[str, Any]]:
        """Extract and format solution"""
        timetable = []

        for var_name, var_data in self.variables.items():
            if self.solver.Value(var_data["var"]) == 1:
                timetable.append({
                    "day": var_data["day"],
                    "slot": var_data["slot"],
                    "subject": var_data["subject"],
                    "room": var_data["room"],
                    "type": var_data["subject_type"],
                    "batch": var_data["batch"],
                    "teacher": None
                })

        # Sort by day, slot, and batch
        day_order = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
        timetable.sort(key=lambda x: (
            day_order.get(x["day"], 7),
            x["slot"],
            x["batch"]
        ))

        return timetable
