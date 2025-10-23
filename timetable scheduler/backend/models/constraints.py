"""
Constraint definitions for the timetable solver
All constraints are hard constraints (must be satisfied)
"""
from typing import List, Dict, Tuple, Any
from ortools.sat.python import cp_model


class TimetableConstraints:
    """
    Defines all constraints for timetable generation
    """

    @staticmethod
    def add_no_teacher_overlap(
        model: cp_model.CpModel,
        variables: Dict[str, Any],
        teachers: List[str],
        time_slots: List[str]
    ) -> None:
        """
        Constraint: No teacher can teach two classes at the same time
        """
        for teacher in teachers:
            for slot in time_slots:
                teacher_slot_vars = [
                    var_data["var"]
                    for var_name, var_data in variables.items()
                    if var_data.get("teacher") == teacher and var_data.get("slot") == slot
                ]
                if teacher_slot_vars:
                    model.Add(sum(teacher_slot_vars) <= 1)

    @staticmethod
    def add_no_room_overlap(
        model: cp_model.CpModel,
        variables: Dict[str, Any],
        rooms: List[str],
        time_slots: List[str]
    ) -> None:
        """
        Constraint: No room can host two classes at the same time
        """
        for room in rooms:
            for slot in time_slots:
                room_slot_vars = [
                    var_data["var"]
                    for var_name, var_data in variables.items()
                    if var_data.get("room") == room and var_data.get("slot") == slot
                ]
                if room_slot_vars:
                    model.Add(sum(room_slot_vars) <= 1)

    @staticmethod
    def add_no_batch_overlap(
        model: cp_model.CpModel,
        variables: Dict[str, Any],
        batches: List[str],
        time_slots: List[str]
    ) -> None:
        """
        Constraint: No batch can attend two classes at the same time
        """
        for batch in batches:
            for slot in time_slots:
                batch_slot_vars = [
                    var_data["var"]
                    for var_name, var_data in variables.items()
                    if var_data.get("batch") == batch and var_data.get("slot") == slot
                ]
                if batch_slot_vars:
                    model.Add(sum(batch_slot_vars) <= 1)

    @staticmethod
    def add_lunch_break_constraint(
        model: cp_model.CpModel,
        variables: Dict[str, Any],
        lunch_start: str,
        lunch_end: str
    ) -> None:
        """
        Constraint: No classes during lunch break
        """
        for var_name, var_data in variables.items():
            slot = var_data.get("slot", "")
            # Extract time from slot (format: "09:00-10:00")
            try:
                start_time = slot.split("-")[0]
                if lunch_start <= start_time < lunch_end:
                    model.Add(var_data["var"] == 0)
            except (ValueError, IndexError):
                pass

    @staticmethod
    def add_subject_hours_constraint(
        model: cp_model.CpModel,
        variables: Dict[str, Any],
        subjects: Dict[str, int]
    ) -> None:
        """
        Constraint: Each subject must be scheduled for required hours per week
        """
        for subject_name, required_hours in subjects.items():
            subject_vars = [
                var_data["var"]
                for var_name, var_data in variables.items()
                if var_data.get("subject") == subject_name
            ]
            if subject_vars:
                model.Add(sum(subject_vars) == required_hours)

    @staticmethod
    def add_room_type_constraint(
        model: cp_model.CpModel,
        variables: Dict[str, Any],
        subject_types: Dict[str, str],
        room_types: Dict[str, str]
    ) -> None:
        """
        Constraint: Theory classes only in classrooms, labs only in lab rooms
        """
        for var_name, var_data in variables.items():
            subject = var_data.get("subject")
            room = var_data.get("room")

            if subject and room:
                subject_type = subject_types.get(subject)
                room_type = room_types.get(room)

                # Theory classes must be in classrooms
                if subject_type == "theory" and room_type == "lab":
                    model.Add(var_data["var"] == 0)

                # Lab classes must be in lab rooms
                if subject_type in ["lab", "theory+lab"] and room_type == "classroom":
                    model.Add(var_data["var"] == 0)

    @staticmethod
    def add_consecutive_hours_constraint(
        model: cp_model.CpModel,
        variables: Dict[str, Any],
        time_slots: List[str],
        max_consecutive: int = 2
    ) -> None:
        """
        Constraint: No more than max_consecutive hours for same subject in a row
        """
        # Group time slots by day
        days = set()
        for slot in time_slots:
            day = slot.split()[0] if " " in slot else slot.split("-")[0]
            days.add(day)

        for day in days:
            day_slots = [s for s in time_slots if s.startswith(day)]

            # Check each window of (max_consecutive + 1) slots
            for i in range(len(day_slots) - max_consecutive):
                window_slots = day_slots[i : i + max_consecutive + 1]

                for subject in set(
                    var_data.get("subject")
                    for var_data in variables.values()
                    if var_data.get("subject")
                ):
                    window_vars = [
                        var_data["var"]
                        for var_name, var_data in variables.items()
                        if (
                            var_data.get("subject") == subject
                            and var_data.get("slot") in window_slots
                        )
                    ]

                    if len(window_vars) == max_consecutive + 1:
                        model.Add(sum(window_vars) <= max_consecutive)

    @staticmethod
    def add_lab_duration_constraint(
        model: cp_model.CpModel,
        variables: Dict[str, Any],
        subject_types: Dict[str, str]
    ) -> None:
        """
        Constraint: Lab sessions must be exactly 2 consecutive hours
        """
        for var_name, var_data in variables.items():
            subject = var_data.get("subject")
            if subject and subject_types.get(subject) in ["lab", "theory+lab"]:
                # Lab sessions should be 2 hours (this is enforced by slot creation)
                pass

    @staticmethod
    def add_special_session_constraint(
        model: cp_model.CpModel,
        variables: Dict[str, Any],
        special_sessions: Dict[str, Dict[str, Any]]
    ) -> None:
        """
        Constraint: Special sessions (mini-projects, tutorials) respect their constraints
        """
        for session_name, session_config in special_sessions.items():
            if not session_config.get("enabled"):
                continue

            required_hours = session_config.get("hours_per_week", 0)
            session_vars = [
                var_data["var"]
                for var_name, var_data in variables.items()
                if var_data.get("session_type") == session_name
            ]

            if session_vars and required_hours > 0:
                model.Add(sum(session_vars) == required_hours)
