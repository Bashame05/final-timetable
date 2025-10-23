"""
Fixed custom timetable solver with proper hour constraints
"""
from ortools.sat.python import cp_model
from typing import List, Dict, Any, Optional
import logging
import random

logger = logging.getLogger(__name__)


class Subject:
    def __init__(self, name: str, subject_type: str, hours: int):
        self.name = name
        self.type = subject_type
        self.hours = hours


class Teacher:
    def __init__(self, name: str, subject: Subject):
        self.name = name
        self.subject = subject


class Room:
    def __init__(self, name: str, room_type: str):
        self.name = name
        self.type = room_type


class FixedTimetableSolver:
    """Fixed solver with strict hour enforcement"""

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
        self.slots = [1, 2, 3, 4, 5, 6, 7]
        self.time_mapping = {
            1: "09:00-10:00", 2: "10:00-11:00", 3: "11:00-12:00",
            4: "12:00-13:00", 5: "14:00-15:00", 6: "15:00-16:00", 7: "16:00-17:00"
        }

        self.rooms = [Room(r["name"], r["type"]) for r in rooms]
        self.classrooms = [r for r in self.rooms if r.type == "classroom"]
        self.labs = [r for r in self.rooms if r.type == "lab"]

        self.subjects = [Subject(s["name"], s["type"], s["hours_per_week"]) for s in subjects]
        self.teachers = [Teacher(f"Teacher_{s.name}", s) for s in self.subjects]

        self._subjects_order = list(self.subjects)
        self._teachers_order = list(self.teachers)
        self._rooms_order = list(self.rooms)
        self._rng.shuffle(self._subjects_order)
        self._rng.shuffle(self._teachers_order)
        self._rng.shuffle(self._rooms_order)

    def solve(self) -> Optional[List[Dict[str, Any]]]:
        """Solve with strict hour constraints"""
        logger.info("Starting fixed timetable solver...")

        model = cp_model.CpModel()

        # Create variables
        x = {}
        for day in self.days:
            x[day] = {}
            for slot in self.slots:
                x[day][slot] = {}
                for subject in self._subjects_order:
                    x[day][slot][subject.name] = {}
                    for teacher in self._teachers_order:
                        if teacher.subject.name == subject.name:
                            x[day][slot][subject.name][teacher.name] = {}
                            for room in self._rooms_order:
                                x[day][slot][subject.name][teacher.name][room.name] = model.NewBoolVar(
                                    f"x_{day}_{slot}_{subject.name}_{teacher.name}_{room.name}"
                                )

        # Constraint 1: Teacher no overlap
        for day in self.days:
            for slot in self.slots:
                for teacher in self.teachers:
                    teacher_assignments = []
                    for subject in self.subjects:
                        if subject.name in x[day][slot] and teacher.name in x[day][slot][subject.name]:
                            for room in self.rooms:
                                teacher_assignments.append(
                                    x[day][slot][subject.name][teacher.name][room.name]
                                )
                    if teacher_assignments:
                        model.Add(sum(teacher_assignments) <= 1)

        # Constraint 2: Room no overlap
        for day in self.days:
            for slot in self.slots:
                for room in self.rooms:
                    room_assignments = []
                    for subject in self.subjects:
                        if subject.name in x[day][slot]:
                            for teacher in self.teachers:
                                if teacher.name in x[day][slot][subject.name]:
                                    room_assignments.append(
                                        x[day][slot][subject.name][teacher.name][room.name]
                                    )
                    if room_assignments:
                        model.Add(sum(room_assignments) <= 1)

        # Constraint 3: Room type matching
        for day in self.days:
            for slot in self.slots:
                for subject in self.subjects:
                    if subject.name in x[day][slot]:
                        for teacher in self.teachers:
                            if teacher.name in x[day][slot][subject.name]:
                                if subject.type == "theory":
                                    for room in self.labs:
                                        model.Add(x[day][slot][subject.name][teacher.name][room.name] == 0)
                                elif subject.type == "practical":
                                    for room in self.classrooms:
                                        model.Add(x[day][slot][subject.name][teacher.name][room.name] == 0)

        # Constraint 4: STRICT hour constraints per subject
        for subject in self.subjects:
            all_slots = []

            for day in self.days:
                for slot in self.slots:
                    if subject.name in x[day][slot]:
                        for teacher in self.teachers:
                            if teacher.name in x[day][slot][subject.name]:
                                for room in self.rooms:
                                    all_slots.append(x[day][slot][subject.name][teacher.name][room.name])

            if all_slots:
                if subject.type == "theory":
                    model.Add(sum(all_slots) == subject.hours)
                elif subject.type == "practical":
                    model.Add(sum(all_slots) == subject.hours)
                elif subject.type == "both":
                    theory_hours = max(1, subject.hours // 2)
                    practical_hours = subject.hours - theory_hours

                    theory_slots = []
                    practical_slots = []

                    for day in self.days:
                        for slot in self.slots:
                            if subject.name in x[day][slot]:
                                for teacher in self.teachers:
                                    if teacher.name in x[day][slot][subject.name]:
                                        for room in self.classrooms:
                                            theory_slots.append(x[day][slot][subject.name][teacher.name][room.name])
                                        for room in self.labs:
                                            practical_slots.append(x[day][slot][subject.name][teacher.name][room.name])

                    if theory_slots:
                        model.Add(sum(theory_slots) == theory_hours)
                    if practical_slots:
                        model.Add(sum(practical_slots) == practical_hours)

        # Constraint 5: Practical days
        y = {}
        for subject in self.subjects:
            if subject.type == "both" or subject.type == "practical":
                y[subject.name] = {}
                for day in self.days:
                    y[subject.name][day] = model.NewBoolVar(f"y_{subject.name}_{day}")
                    day_practical_terms = []

                    for slot in self.slots:
                        if subject.name in x[day][slot]:
                            for teacher in self.teachers:
                                if teacher.name in x[day][slot][subject.name]:
                                    for room in self.labs:
                                        day_practical_terms.append(x[day][slot][subject.name][teacher.name][room.name])

                    if day_practical_terms:
                        practical_hours = subject.hours if subject.type == "practical" else (subject.hours - max(1, subject.hours // 2))
                        model.Add(sum(day_practical_terms) == practical_hours).OnlyEnforceIf(y[subject.name][day])
                        model.Add(sum(day_practical_terms) == 0).OnlyEnforceIf(y[subject.name][day].Not())

                if subject.type == "both" or subject.type == "practical":
                    model.Add(sum(y[subject.name][d] for d in self.days) == 1)

        # Constraint 6: Mix rule
        day_has_theory = {day: model.NewBoolVar(f"day_has_theory_{day}") for day in self.days}
        day_has_practical = {day: model.NewBoolVar(f"day_has_practical_{day}") for day in self.days}

        for day in self.days:
            theory_presence = []
            practical_presence = []

            for subject in self.subjects:
                for slot in self.slots:
                    if subject.name in x[day][slot]:
                        for teacher in self.teachers:
                            if teacher.name in x[day][slot][subject.name]:
                                for room in self.classrooms:
                                    theory_presence.append(x[day][slot][subject.name][teacher.name][room.name])
                                for room in self.labs:
                                    practical_presence.append(x[day][slot][subject.name][teacher.name][room.name])

            if theory_presence:
                model.Add(sum(theory_presence) >= 1).OnlyEnforceIf(day_has_theory[day])
                model.Add(sum(theory_presence) == 0).OnlyEnforceIf(day_has_theory[day].Not())
            else:
                model.Add(day_has_theory[day] == 0)

            if practical_presence:
                model.Add(sum(practical_presence) >= 1).OnlyEnforceIf(day_has_practical[day])
                model.Add(sum(practical_presence) == 0).OnlyEnforceIf(day_has_practical[day].Not())
            else:
                model.Add(day_has_practical[day] == 0)

            model.Add(day_has_practical[day] <= day_has_theory[day])

        # Constraint 7: Max 2 practical subjects per day
        for day in self.days:
            chosen_for_day = []
            for subject in self.subjects:
                if subject.name in y:
                    chosen_for_day.append(y[subject.name][day])
            if chosen_for_day:
                model.Add(sum(chosen_for_day) <= 2)

        # Objective
        objective_terms = []
        for day in self.days:
            for slot in self.slots:
                for subject in self.subjects:
                    if subject.name in x[day][slot]:
                        for teacher in self.teachers:
                            if teacher.name in x[day][slot][subject.name]:
                                for room in self.classrooms:
                                    w = 20 + self._rng.randint(0, 3)
                                    objective_terms.append(w * x[day][slot][subject.name][teacher.name][room.name])
                                for room in self.labs:
                                    w = 10 + self._rng.randint(0, 3)
                                    objective_terms.append(w * x[day][slot][subject.name][teacher.name][room.name])

        for day in self.days:
            objective_terms.append(20 * day_has_practical[day])
            objective_terms.append(20 * day_has_theory[day])

        if objective_terms:
            model.Maximize(sum(objective_terms))

        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.random_seed = self._rng.randint(1, 1_000_000)
        try:
            solver.parameters.num_search_workers = 8
        except Exception:
            pass

        status = solver.Solve(model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            logger.info("✅ Solution found!")
            return self._extract_solution(solver, x)
        else:
            logger.warning("❌ No feasible solution found")
            return None

    def _extract_solution(self, solver, x) -> List[Dict[str, Any]]:
        """Extract solution"""
        solution = []

        for day in self.days:
            for slot in self.slots:
                for subject in self.subjects:
                    if subject.name in x[day][slot]:
                        for teacher in self.teachers:
                            if teacher.name in x[day][slot][subject.name]:
                                for room in self.rooms:
                                    if solver.Value(x[day][slot][subject.name][teacher.name][room.name]) == 1:
                                        session_type = "theory"
                                        if subject.type == "both":
                                            session_type = "practical" if room.type == "lab" else "theory"
                                        elif subject.type == "practical":
                                            session_type = "practical"

                                        solution.append({
                                            "day": day,
                                            "slot": self.time_mapping[slot],
                                            "subject": subject.name,
                                            "room": room.name,
                                            "type": session_type,
                                            "teacher": None
                                        })

        return solution
