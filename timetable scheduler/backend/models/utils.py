"""
Utility functions for timetable generation
"""
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


def time_to_minutes(time_str: str) -> int:
    """
    Convert time string (HH:MM) to minutes since midnight
    """
    try:
        hours, minutes = map(int, time_str.split(":"))
        return hours * 60 + minutes
    except (ValueError, AttributeError):
        logger.error(f"Invalid time format: {time_str}")
        return 0


def minutes_to_time(minutes: int) -> str:
    """
    Convert minutes since midnight to time string (HH:MM)
    """
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


def generate_time_slots(
    start_time: str,
    end_time: str,
    slot_duration: int = 60,
    lunch_start: str = None,
    lunch_end: str = None,
    working_days: List[str] = None
) -> List[Tuple[str, str]]:
    """
    Generate all time slots for the week
    
    Returns:
        List of tuples (day, slot) where slot is "HH:MM-HH:MM"
    """
    if working_days is None:
        working_days = ["Mon", "Tue", "Wed", "Thu", "Fri"]

    slots = []
    start_mins = time_to_minutes(start_time)
    end_mins = time_to_minutes(end_time)
    lunch_start_mins = time_to_minutes(lunch_start) if lunch_start else None
    lunch_end_mins = time_to_minutes(lunch_end) if lunch_end else None

    current_mins = start_mins
    while current_mins < end_mins:
        slot_end_mins = current_mins + slot_duration

        # Skip lunch break
        if lunch_start_mins and lunch_end_mins:
            if current_mins >= lunch_start_mins and current_mins < lunch_end_mins:
                current_mins = lunch_end_mins
                continue
            if slot_end_mins > lunch_start_mins and current_mins < lunch_start_mins:
                current_mins = lunch_start_mins
                continue

        if slot_end_mins <= end_mins:
            slot_str = f"{minutes_to_time(current_mins)}-{minutes_to_time(slot_end_mins)}"

            for day in working_days:
                slots.append((day, slot_str))

        current_mins = slot_end_mins

    return slots


def is_slot_in_lunch_break(slot: str, lunch_start: str, lunch_end: str) -> bool:
    """
    Check if a slot overlaps with lunch break
    """
    try:
        start_time = slot.split("-")[0]
        start_mins = time_to_minutes(start_time)
        lunch_start_mins = time_to_minutes(lunch_start)
        lunch_end_mins = time_to_minutes(lunch_end)

        return lunch_start_mins <= start_mins < lunch_end_mins
    except (ValueError, IndexError):
        return False


def get_consecutive_slots(
    day: str,
    start_slot: str,
    duration_hours: int,
    all_slots: List[Tuple[str, str]]
) -> List[str]:
    """
    Get consecutive slots for a given duration
    """
    day_slots = [slot for d, slot in all_slots if d == day]

    try:
        start_idx = day_slots.index(start_slot)
    except ValueError:
        return []

    consecutive = []
    for i in range(duration_hours):
        if start_idx + i < len(day_slots):
            consecutive.append(day_slots[start_idx + i])
        else:
            return []  # Not enough consecutive slots

    return consecutive


def validate_time_format(time_str: str) -> bool:
    """
    Validate time string format (HH:MM)
    """
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False


def validate_day_name(day: str) -> bool:
    """
    Validate day name
    """
    valid_days = {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}
    return day in valid_days


def calculate_total_hours(subjects: List[Dict[str, Any]]) -> int:
    """
    Calculate total hours required for all subjects
    """
    return sum(subject.get("hours_per_week", 0) for subject in subjects)


def get_available_rooms_for_subject(
    subject_type: str,
    rooms: List[Dict[str, Any]]
) -> List[str]:
    """
    Get rooms suitable for a subject type
    """
    if subject_type == "theory":
        return [r["name"] for r in rooms if r["type"] == "classroom"]
    elif subject_type == "lab":
        return [r["name"] for r in rooms if r["type"] == "lab"]
    elif subject_type == "theory+lab":
        return [r["name"] for r in rooms]
    return []


def check_feasibility(
    total_hours: int,
    available_slots: int,
    working_days: int
) -> Tuple[bool, str]:
    """
    Check if the problem is feasible
    """
    if available_slots == 0:
        return False, "No available time slots"

    if total_hours > available_slots:
        return (
            False,
            f"Not enough slots: {total_hours} hours required, {available_slots} slots available"
        )

    if working_days == 0:
        return False, "No working days specified"

    return True, "Problem is feasible"


def format_slot_display(slot: str) -> str:
    """
    Format slot for display (e.g., "09:00-10:00" -> "9:00 AM - 10:00 AM")
    """
    try:
        start, end = slot.split("-")
        start_hour, start_min = map(int, start.split(":"))
        end_hour, end_min = map(int, end.split(":"))

        start_ampm = "AM" if start_hour < 12 else "PM"
        end_ampm = "AM" if end_hour < 12 else "PM"

        if start_hour > 12:
            start_hour -= 12
        if end_hour > 12:
            end_hour -= 12

        return f"{start_hour}:{start_min:02d} {start_ampm} - {end_hour}:{end_min:02d} {end_ampm}"
    except (ValueError, IndexError):
        return slot


def merge_consecutive_slots(slots: List[str]) -> List[str]:
    """
    Merge consecutive time slots into ranges
    """
    if not slots:
        return []

    merged = []
    current_start = slots[0]
    current_end = slots[0]

    for slot in slots[1:]:
        # Check if slot is consecutive
        try:
            current_end_time = current_end.split("-")[1]
            slot_start_time = slot.split("-")[0]

            if current_end_time == slot_start_time:
                current_end = slot
            else:
                merged.append(f"{current_start.split('-')[0]}-{current_end.split('-')[1]}")
                current_start = slot
                current_end = slot
        except (ValueError, IndexError):
            merged.append(current_start)
            current_start = slot
            current_end = slot

    merged.append(f"{current_start.split('-')[0]}-{current_end.split('-')[1]}")
    return merged


def get_slot_duration_minutes(slot: str) -> int:
    """
    Get duration of a slot in minutes
    """
    try:
        start, end = slot.split("-")
        start_mins = time_to_minutes(start)
        end_mins = time_to_minutes(end)
        return end_mins - start_mins
    except (ValueError, IndexError):
        return 0
