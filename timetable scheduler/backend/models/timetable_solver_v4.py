"""
Timetable solver V4 - with theory/lab separation constraint
"""
from ortools.sat.python import cp_model
from typing import List, Dict, Any, Optional
import logging
import random

logger = logging.getLogger(__name__)


class TimetableSolverV4:
    """Solver with theory/lab separation constraint"""

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
        """Solve with theory/lab separation"""
        logger.info("\n" + "=" * 60)
        logger.info("STARTING TIMETABLE SOLVER V4")
        logger.info("=" * 60)

        model = cp_model.CpModel()

        variables = {}
        var_list = []

        for day in self.days:
            for slot_num in range(1, 8):
                for subject in self.subjects:
                    for room in self.rooms:
                        subject_type = subject["type"]
                        room_type = room["type"]
                        
                        if subject_type == "theory+lab":
                            subject_type = "both"
                        if subject_type == "practical":
                            subject_type = "lab"
                        
                        if subject_type == "theory" and room_type != "classroom":
                            continue
                        if subject_type == "lab" and room_type != "lab":
                            continue
                        if subject_type == "both":
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

        # Constraint 1: No room overlap
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

        # Constraint 2: Hour constraints
        logger.info("\n" + "=" * 60)
        logger.info("ADDING HOUR CONSTRAINTS")
        logger.info("=" * 60)

        for subject in self.subjects:
            required_hours = subject["hours"]
            logger.info(f"\nSubject: {subject['name']}")
            logger.info(f"  Required hours: {required_hours}")
            logger.info(f"  Type: {subject['type']}")

            subject_vars = [
                variables[var_name]["var"]
                for var_name in variables
                if variables[var_name]["subject"] == subject["name"]
            ]

            logger.info(f"  Available slots: {len(subject_vars)}")

            if subject_vars:
                model.Add(sum(subject_vars) == required_hours)
                logger.info(f"  ✓ Constraint added: sum == {required_hours}")
            else:
                logger.warning(f"  ✗ NO VARIABLES FOUND for {subject['name']}")

        # Constraint 3: Theory and lab cannot be in same slot for same subject
        logger.info("\n" + "=" * 60)
        logger.info("ADDING THEORY/LAB SEPARATION CONSTRAINT")
        logger.info("=" * 60)

        for subject in self.subjects:
            if subject["type"] not in ["theory+lab", "both"]:
                continue

            logger.info(f"\nSubject: {subject['name']} (theory+lab)")

            for day in self.days:
                for slot_num in range(1, 8):
                    # Get theory slots for this subject/day/slot
                    theory_vars = [
                        variables[var_name]["var"]
                        for var_name in variables
                        if variables[var_name]["subject"] == subject["name"]
                        and variables[var_name]["day"] == day
                        and variables[var_name]["slot"] == slot_num
                        and variables[var_name]["room_type"] == "classroom"
                    ]

                    # Get lab slots for this subject/day/slot
                    lab_vars = [
                        variables[var_name]["var"]
                        for var_name in variables
                        if variables[var_name]["subject"] == subject["name"]
                        and variables[var_name]["day"] == day
                        and variables[var_name]["slot"] == slot_num
                        and variables[var_name]["room_type"] == "lab"
                    ]

                    # If both exist, they cannot both be selected
                    if theory_vars and lab_vars:
                        model.Add(sum(theory_vars) + sum(lab_vars) <= 1)

            logger.info(f"  ✓ Separation constraint added")

        logger.info("\n" + "=" * 60)
        logger.info("SOLVING...")
        logger.info("=" * 60)

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
