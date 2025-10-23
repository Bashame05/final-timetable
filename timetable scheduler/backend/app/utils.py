"""
Utility functions for timetable scheduling
"""
from typing import List, Dict, Tuple, Set
from .models import Teacher, Room, Subject, Batch, TimetableRequest, Lecture

def create_time_slot_key(day: str, time: str) -> str:
    """Create a standardized time slot key"""
    return f"{day}_{time}"

def parse_time_slot(slot_key: str) -> Tuple[str, str]:
    """Parse a time slot key into day and time"""
    parts = slot_key.split("_")
    if len(parts) == 2:
        return parts[0], parts[1]
    raise ValueError(f"Invalid time slot format: {slot_key}")

def is_break_time(time: str, break_start: str = "12", break_end: str = "1") -> bool:
    """Check if a time slot falls during break time"""
    return time == break_start or time == break_end

def get_available_slots_for_teacher(teacher: Teacher, days: List[str], time_slots: List[str], 
                                  break_start: str = "12", break_end: str = "1") -> List[str]:
    """Get available time slots for a teacher, excluding break time"""
    available = []
    for day in days:
        for time in time_slots:
            if not is_break_time(time, break_start, break_end):
                slot_key = create_time_slot_key(day, time)
                if slot_key in teacher.available_slots:
                    available.append(slot_key)
    return available

def get_available_slots_for_room(room: Room, days: List[str], time_slots: List[str],
                               break_start: str = "12", break_end: str = "1") -> List[str]:
    """Get available time slots for a room, excluding break time"""
    available = []
    for day in days:
        for time in time_slots:
            if not is_break_time(time, break_start, break_end):
                slot_key = create_time_slot_key(day, time)
                if slot_key in room.available_slots:
                    available.append(slot_key)
    return available

def get_teachers_for_subject(subject: Subject, teachers: List[Teacher]) -> List[Teacher]:
    """Get all teachers who can teach a specific subject"""
    return [t for t in teachers if subject.id in t.subjects or t.id in subject.teachers]

def get_rooms_for_subject(subject: Subject, rooms: List[Room]) -> List[Room]:
    """Get all rooms suitable for a specific subject"""
    if subject.required_room_type:
        return [r for r in rooms if r.type == subject.required_room_type]
    
    # Default room type based on subject type
    if subject.type == "practical":
        return [r for r in rooms if r.type == "lab"]
    else:
        return [r for r in rooms if r.type == "classroom"]

def can_schedule_consecutive_hours(subject: Subject, start_slot: str, 
                                 days: List[str], time_slots: List[str]) -> bool:
    """Check if a subject can be scheduled for consecutive hours"""
    if subject.type == "practical":
        return subject.duration == 2  # Practical must be exactly 2 hours
    elif subject.type == "theory":
        return subject.duration <= 2  # Theory max 2 hours
    elif subject.type == "project":
        return subject.duration >= 2  # Project min 2 hours
    return False

def get_consecutive_slots(start_slot: str, duration: int, 
                         days: List[str], time_slots: List[str]) -> List[str]:
    """Get consecutive time slots starting from a given slot"""
    day, start_time = parse_time_slot(start_slot)
    start_index = time_slots.index(start_time)
    
    consecutive_slots = []
    for i in range(duration):
        if start_index + i < len(time_slots):
            slot_time = time_slots[start_index + i]
            if not is_break_time(slot_time):
                consecutive_slots.append(create_time_slot_key(day, slot_time))
            else:
                return []  # Break time interrupts consecutive scheduling
        else:
            return []  # Not enough time slots
    
    return consecutive_slots

def format_time_display(time_slots: List[str]) -> str:
    """Format time slots for display (e.g., "9:00-10:00")"""
    if len(time_slots) == 1:
        time = time_slots[0]
        return f"{time}:00-{int(time)+1}:00"
    elif len(time_slots) == 2:
        start, end = time_slots[0], time_slots[-1]
        return f"{start}:00-{int(end)+1}:00"
    else:
        start, end = time_slots[0], time_slots[-1]
        return f"{start}:00-{int(end)+1}:00"

def create_lecture_from_assignment(assignment: Dict, subjects: List[Subject], 
                                 teachers: List[Teacher], rooms: List[Room],
                                 batches: List[Batch]) -> Lecture:
    """Create a Lecture object from solver assignment"""
    subject = next(s for s in subjects if s.id == assignment["subject"])
    teacher = next(t for t in teachers if t.id == assignment["teacher"])
    room = next(r for r in rooms if r.id == assignment["room"])
    batch = next(b for b in batches if b.id == assignment["batch"])
    
    day, time = parse_time_slot(assignment["slot"])
    
    return Lecture(
        day=day,
        time=format_time_display([time]),
        subject=subject.name,
        teacher=teacher.name,
        room=room.name,
        type=subject.type.value,
        batch=batch.name
    )

def validate_time_slots(time_slots: List[str]) -> bool:
    """Validate that time slots are properly formatted"""
    for slot in time_slots:
        try:
            int(slot)
        except ValueError:
            return False
    return True

def get_subjects_for_batch(batch: Batch, subjects: List[Subject]) -> List[Subject]:
    """Get all subjects for a specific batch"""
    return [s for s in subjects if s.id in batch.subjects]

def calculate_total_lecture_hours(subjects: List[Subject]) -> int:
    """Calculate total lecture hours needed for all subjects"""
    return sum(subject.duration for subject in subjects)

def get_available_time_slots(days: List[str], time_slots: List[str], 
                           break_start: str = "12", break_end: str = "1") -> List[str]:
    """Get all available time slots excluding break time"""
    available = []
    for day in days:
        for time in time_slots:
            if not is_break_time(time, break_start, break_end):
                available.append(create_time_slot_key(day, time))
    return available
