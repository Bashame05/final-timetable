"""
Simplified timetable solver - focus on getting hours RIGHT
"""
from ortools.sat.python import cp_model
from typing import List, Dict, Any, Optional
import logging
import random

logger = logging.getLogger(__name__)


class SimpleTimetableSolver:
    """Simplified solver focused on hour enforcement"""

    def __init__(
        self,
        week_config: Dict[str, Any],
        rooms: List[Dict[str, Any]],
        subjects: List[Dict[str, Any]],
        seed: Optional[int] = None
    ):
        self.week_config = week_config
        self.seed = seed if seed is not None else random.randint(1, 10_000_000)
        self._rng = random.Random(self.seed)

        self.days = week_config.get("working_days", ["Mon", "Tue", "Wed", "Thu", "Fri"])
        self.time_mapping = {
            1: "09:00-10:00", 2: "10:00-11:00", 3: "11:00-12:00",
            4: "12:00-13:00", 5: "14:00-15:00", 6: "15:00-16:00", 7: "16:00-17:00"
        }

        self.rooms = rooms
        self.classrooms = [r for r in rooms if r["type"] == "classroom"]
        self.labs = [r for r in rooms if r["type"] == "lab"]

        # Parse subjects - STRICT hour reading
        self.subjects = []
        for s in subjects:
            hours = int(s.get("hours_per_week", 0))
            self.subjects.append({
                "name": s["name"],
                "type": s["type"],
                "hours": hours
            })
            logger.info(f"Subject: {s['name']}, Type: {s['type']}, Hours: {hours}")

        logger.info(f"Total subjects: {len(self.subjects)}")
        logger.info(f"Total rooms: {len(self.rooms)}")
        logger.info(f"Days: {self.days}")

    def solve(self) -> Optional[List[Dict[str, Any]]]:
        """Solve with SIMPLE, DIRECT hour constraints"""
        logger.info("\n" + "=" * 60)
        logger.info("STARTING SIMPLE TIMETABLE SOLVER")
        logger.info("=" * 60)

        model = cp_model.CpModel()

        # Create simple variables: (day, slot, subject, room) -> bool
        # This is much simpler than the nested structure
        variables = {}
        var_list = []

        for day in self.days:
            for slot_num in range(1, 8):
                for subject in self.subjects:
                    for room in self.rooms:
                        # Check room type matches subject type
                        subject_type = subject["type"]
                        room_type = room["type"]
                        
                        # Normalize subject types
                        if subject_type == "theory+lab":
                            subject_type = "both"
                        if subject_type == "practical":
                            subject_type = "lab"
                        
                        # Check compatibility
                        if subject_type == "theory" and room_type != "classroom":
                            continue
                        if subject_type == "lab" and room_type != "lab":
                            continue
                        if subject_type == "both":
                            # Both can go in either
                            pass

                        var_name = f"{day}_{slot_num}_{subject['name']}_{room['name']}"
                        var = model.NewBoolVar(var_name)
                        variables[var_name] = {
                            "var": var,
                            "day": day,
                            "slot": slot_num,
                            "subject": subject["name"],
                            "room": room["name"],
                            "subject_type": subject["type"],
                            "room_type": room["type"]
                        }
                        var_list.append(var)

        logger.info(f"Created {len(variables)} variables")

        # Constraint 1: No room overlap (only one session per room per slot)
        for day in self.days:
            for slot_num in range(1, 8):
                for room in self.rooms:
                    room_vars = [
                        variables[var_name]["var"]
                        for var_name in variables
                        if variables[var_name]["day"] == day
                        and variables[var_name]["slot"] == slot_num
                        and variables[var_name]["room"] == room["name"]
                    ]
                    if room_vars:
                        model.Add(sum(room_vars) <= 1)

        logger.info("Room overlap constraint added")

        # Constraint 2: STRICT HOUR CONSTRAINT - THIS IS THE KEY
        logger.info("\n" + "=" * 60)
        logger.info("ADDING HOUR CONSTRAINTS")
        logger.info("=" * 60)

        for subject in self.subjects:
            required_hours = subject["hours"]
            logger.info(f"\nSubject: {subject['name']}")
            logger.info(f"  Required hours: {required_hours}")
            logger.info(f"  Type: {subject['type']}")

            # Get all variables for this subject
            subject_vars = [
                variables[var_name]["var"]
                for var_name in variables
                if variables[var_name]["subject"] == subject["name"]
            ]

            logger.info(f"  Available slots: {len(subject_vars)}")

            if subject_vars:
                # ADD THE CONSTRAINT: sum must equal required hours
                model.Add(sum(subject_vars) == required_hours)
                logger.info(f"  ✓ Constraint added: sum == {required_hours}")
            else:
                logger.warning(f"  ✗ NO VARIABLES FOUND for {subject['name']}")

        logger.info("\n" + "=" * 60)
        logger.info("SOLVING...")
        logger.info("=" * 60)

        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.random_seed = self._rng.randint(1, 1_000_000)
        try:
            solver.parameters.num_search_workers = 8
        except Exception:
            pass

        status = solver.Solve(model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            logger.info("✅ SOLUTION FOUND!")
            return self._extract_solution(solver, variables)
        else:
            logger.warning("❌ NO FEASIBLE SOLUTION")
            return None

    def _extract_solution(self, solver, variables) -> List[Dict[str, Any]]:
        """Extract solution"""
        solution = []
        hours_count = {s["name"]: 0 for s in self.subjects}

        for var_name in variables:
            var_data = variables[var_name]
            if solver.Value(var_data["var"]) == 1:
                slot_num = var_data["slot"]
                time_slot = self.time_mapping.get(slot_num, "UNKNOWN")

                # Determine session type
                session_type = var_data["subject_type"]
                if var_data["subject_type"] in ["both", "theory+lab"]:
                    session_type = "practical" if var_data["room_type"] == "lab" else "theory"
                elif var_data["subject_type"] == "practical":
                    session_type = "practical"
                else:
                    session_type = "theory"

                solution.append({
                    "day": var_data["day"],
                    "slot": time_slot,
                    "subject": var_data["subject"],
                    "room": var_data["room"],
                    "type": session_type,
                    "teacher": None
                })

                hours_count[var_data["subject"]] += 1

        # Verify hours
        logger.info("\n" + "=" * 60)
        logger.info("HOUR VERIFICATION")
        logger.info("=" * 60)
        all_correct = True
        for subject in self.subjects:
            expected = subject["hours"]
            actual = hours_count[subject["name"]]
            match = "✓" if actual == expected else "✗"
            if actual != expected:
                all_correct = False
            logger.info(f"{match} {subject['name']}: Expected {expected}h, Got {actual}h")

        if all_correct:
            logger.info("\n✅ ALL HOURS CORRECT!")
        else:
            logger.warning("\n❌ SOME HOURS INCORRECT!")

        logger.info("=" * 60)

        return solution
