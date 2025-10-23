"""
Advanced timetable solver with refined constraints
- Splits theory+lab into separate sessions
- Consecutive practical slots within same day
- Batch compactness (max 2 consecutive theory slots)
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


class TimetableSolverV3:
    """
    Advanced solver with refined constraints for better timetable quality
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
        self.expanded_subjects = []  # Subjects split into theory/lab

    def generate_timetable(self) -> Tuple[bool, List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Generate advanced optimized timetable"""
        logger.info("Starting advanced timetable generation (V3)...")

        # Step 1: Generate time slots
        self._generate_time_slots()
        logger.info(f"Generated {len(self.time_slots)} time slots")

        # Step 2: Expand subjects (split theory+lab)
        self._expand_subjects()
        logger.info(f"Expanded subjects: {len(self.expanded_subjects)} sessions")

        # Step 3: Check feasibility
        feasible, message = self._check_feasibility()
        if not feasible:
            logger.warning(f"Problem not feasible: {message}")
            return False, [], [{"reason": message}]

        # Step 4: Create variables
        self._create_variables()
        logger.info(f"Created {len(self.variables)} variables")

        if len(self.variables) == 0:
            logger.error("No variables created")
            return False, [], [{"reason": "No valid variable combinations found"}]

        # Step 5: Add constraints
        self._add_constraints()
        logger.info("Constraints added")

        # Step 6: Add optimization objectives
        self._add_optimization_objectives()
        logger.info("Optimization objectives added")

        # Step 7: Solve
        success = self._solve()

        if success:
            timetable = self._extract_solution()
            logger.info(f"Generated advanced timetable with {len(timetable)} slots")
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

    def _expand_subjects(self) -> None:
        """
        Split theory+lab subjects into separate theory and lab sessions
        """
        for subject in self.subjects:
            subject_name = subject["name"]
            hours_per_week = subject["hours_per_week"]
            subject_type = subject["type"]

            if subject_type == "theory":
                # Theory only
                self.expanded_subjects.append({
                    "original_name": subject_name,
                    "name": f"{subject_name} (Theory)",
                    "type": "theory",
                    "hours": hours_per_week,
                    "is_practical": False,
                    "requires_consecutive": False
                })
            elif subject_type == "lab":
                # Lab only
                self.expanded_subjects.append({
                    "original_name": subject_name,
                    "name": f"{subject_name} (Lab)",
                    "type": "lab",
                    "hours": hours_per_week,
                    "is_practical": True,
                    "requires_consecutive": True
                })
            elif subject_type == "theory+lab":
                # Split into theory and lab
                theory_hours = max(1, hours_per_week // 2)
                lab_hours = hours_per_week - theory_hours

                self.expanded_subjects.append({
                    "original_name": subject_name,
                    "name": f"{subject_name} (Theory)",
                    "type": "theory",
                    "hours": theory_hours,
                    "is_practical": False,
                    "requires_consecutive": False
                })

                self.expanded_subjects.append({
                    "original_name": subject_name,
                    "name": f"{subject_name} (Lab)",
                    "type": "lab",
                    "hours": lab_hours,
                    "is_practical": True,
                    "requires_consecutive": True
                })

    def _check_feasibility(self) -> Tuple[bool, str]:
        """Check if problem is feasible"""
        total_hours = sum(s["hours"] for s in self.expanded_subjects)
        available_slots = len(self.time_slots) * self.num_batches
        working_days = len(self.week_config.get("working_days", []))

        return check_feasibility(total_hours, available_slots, working_days)

    def _create_variables(self) -> None:
        """Create variables with batch distribution"""
        var_id = 0

        for subject in self.expanded_subjects:
            subject_name = subject["name"]
            subject_type = subject["type"]
            hours_per_week = subject["hours"]
            is_practical = subject["is_practical"]

            # Get available rooms
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
                            "original_subject": subject["original_name"],
                            "subject_type": subject_type,
                            "room": room_name,
                            "day": day,
                            "slot": slot,
                            "batch": batch_id,
                            "hours": hours_per_week,
                            "is_practical": is_practical,
                            "requires_consecutive": subject["requires_consecutive"]
                        }

                        var_id += 1

    def _add_constraints(self) -> None:
        """Add all constraints"""
        rooms = [r["name"] for r in self.rooms]
        room_types = {r["name"]: r["type"] for r in self.rooms}
        days = list(set(day for day, _ in self.time_slots))
        slots = list(set(slot for _, slot in self.time_slots))

        # 1. No room overlap per day
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

        # 2. No batch overlap per day
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

        # 3. Subject hours constraint
        for subject_name in set(s["name"] for s in self.expanded_subjects):
            subject_vars = [
                var_data["var"]
                for var_name, var_data in self.variables.items()
                if var_data.get("subject") == subject_name
            ]
            hours = next(
                (s["hours"] for s in self.expanded_subjects if s["name"] == subject_name),
                0
            )
            if subject_vars:
                self.model.Add(sum(subject_vars) == hours)

        # 4. Room type constraint (theory→classroom, lab→lab)
        for var_name, var_data in self.variables.items():
            room_name = var_data.get("room")
            room_type = room_types.get(room_name, "classroom")
            subject_type = var_data.get("subject_type")

            if subject_type == "theory" and room_type != "classroom":
                self.model.Add(var_data["var"] == 0)
            elif subject_type == "lab" and room_type != "lab":
                self.model.Add(var_data["var"] == 0)

        # 5. Consecutive practical slots within same day
        self._add_consecutive_practical_constraint(days, slots)

        # 6. Batch compactness (max 2 consecutive theory slots)
        self._add_batch_compactness_constraint(days, slots)

    def _add_consecutive_practical_constraint(self, days: List[str], slots: List[str]) -> None:
        """
        Practical sessions must be consecutive within the same day
        """
        # Get slot order
        slot_order = self._get_slot_order()

        for batch_id in range(1, self.num_batches + 1):
            for day in days:
                for subject_name in set(s["name"] for s in self.expanded_subjects if s["is_practical"]):
                    # Get all practical slots for this batch/day/subject
                    practical_vars = [
                        (var_name, var_data)
                        for var_name, var_data in self.variables.items()
                        if var_data.get("batch") == batch_id
                        and var_data.get("day") == day
                        and var_data.get("subject") == subject_name
                        and var_data.get("is_practical")
                    ]

                    if len(practical_vars) > 1:
                        # Sort by slot order
                        practical_vars.sort(
                            key=lambda x: slot_order.get(x[1].get("slot"), 999)
                        )

                        # Enforce consecutiveness
                        for i in range(len(practical_vars) - 1):
                            curr_var = practical_vars[i][1]["var"]
                            next_var = practical_vars[i + 1][1]["var"]
                            curr_slot = practical_vars[i][1].get("slot")
                            next_slot = practical_vars[i + 1][1].get("slot")

                            # If current slot is selected, next must also be selected
                            # (if they are consecutive)
                            if self._are_consecutive_slots(curr_slot, next_slot):
                                self.model.Add(curr_var <= next_var)

    def _add_batch_compactness_constraint(self, days: List[str], slots: List[str]) -> None:
        """
        Avoid more than 2 consecutive theory slots per batch per day
        """
        slot_order = self._get_slot_order()

        for batch_id in range(1, self.num_batches + 1):
            for day in days:
                sorted_slots = sorted(slots, key=lambda s: slot_order.get(s, 999))

                # Check every 3-slot window
                for i in range(len(sorted_slots) - 2):
                    slot1, slot2, slot3 = sorted_slots[i], sorted_slots[i + 1], sorted_slots[i + 2]

                    # Get theory variables for these slots
                    theory_vars = []
                    for slot in [slot1, slot2, slot3]:
                        slot_vars = [
                            var_data["var"]
                            for var_name, var_data in self.variables.items()
                            if var_data.get("batch") == batch_id
                            and var_data.get("day") == day
                            and var_data.get("slot") == slot
                            and not var_data.get("is_practical")
                        ]
                        theory_vars.append(slot_vars)

                    # At most 2 of the 3 consecutive slots can have theory
                    if all(theory_vars):
                        self.model.Add(
                            sum(sum(v) for v in theory_vars) <= 2
                        )

    def _get_slot_order(self) -> Dict[str, int]:
        """Get ordering of time slots"""
        return {
            "09:00-10:00": 0, "10:00-11:00": 1, "11:00-12:00": 2,
            "14:00-15:00": 3, "15:00-16:00": 4
        }

    def _are_consecutive_slots(self, slot1: str, slot2: str) -> bool:
        """Check if two slots are consecutive"""
        slot_order = self._get_slot_order()
        order1 = slot_order.get(slot1, -1)
        order2 = slot_order.get(slot2, -1)
        return order2 == order1 + 1

    def _add_optimization_objectives(self) -> None:
        """Add optimization objectives"""
        day_order = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
        slot_order = self._get_slot_order()

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
        """Run the solver"""
        logger.info("Running advanced CP-SAT solver (V3)...")

        self.solver.parameters.max_time_in_seconds = 180.0
        self.solver.parameters.log_search_progress = False
        self.solver.parameters.num_workers = 4

        status = self.solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            logger.info("✅ Advanced solution found!")
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
                    "subject": var_data["original_subject"],
                    "room": var_data["room"],
                    "type": var_data["subject_type"],
                    "batch": var_data["batch"],
                    "session_type": "Practical" if var_data["is_practical"] else "Theory",
                    "teacher": None
                })

        # Sort by day, slot, and batch
        day_order = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
        slot_order = self._get_slot_order()

        timetable.sort(key=lambda x: (
            day_order.get(x["day"], 7),
            slot_order.get(x["slot"], 999),
            x["batch"]
        ))

        return timetable
