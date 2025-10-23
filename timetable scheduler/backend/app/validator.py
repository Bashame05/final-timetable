"""
Constraint validator for timetable solutions
"""
from typing import List, Dict, Set, Tuple
from .models import (
    TimetableRequest, TimetableResponse, SolverResult, 
    ConstraintViolation, Teacher, Room, Subject, Batch, Lecture
)
from .utils import (
    parse_time_slot, is_break_time, get_teachers_for_subject,
    get_rooms_for_subject, get_subjects_for_batch
)

class TimetableValidator:
    def __init__(self, request: TimetableRequest):
        self.request = request
        self.violations = []
        
        # Create lookup maps
        self.teacher_map = {t.id: t for t in request.teachers}
        self.room_map = {r.id: r for r in request.rooms}
        self.subject_map = {s.id: s for s in request.subjects}
        self.batch_map = {b.id: b for b in request.batches}
    
    def validate_solution(self, result: SolverResult) -> List[ConstraintViolation]:
        """Validate a complete timetable solution"""
        self.violations = []
        
        if not result.success:
            self.violations.append(ConstraintViolation(
                type="solver_error",
                description="Solver failed to find a solution",
                affected_entities=[],
                severity="error"
            ))
            return self.violations
        
        for timetable in result.timetables:
            self._validate_timetable(timetable)
        
        return self.violations
    
    def _validate_timetable(self, timetable: TimetableResponse):
        """Validate a single batch timetable"""
        batch = next(b for b in self.request.batches if b.name == timetable.batch)
        
        # Check for duplicate slots
        self._check_duplicate_slots(timetable)
        
        # Check teacher availability
        self._check_teacher_availability(timetable)
        
        # Check room availability
        self._check_room_availability(timetable)
        
        # Check subject requirements
        self._check_subject_requirements(timetable, batch)
        
        # Check break time constraints
        self._check_break_time_constraints(timetable)
        
        # Check consecutive hours constraints
        self._check_consecutive_hours_constraints(timetable)
        
        # Check room type constraints
        self._check_room_type_constraints(timetable)
    
    def _check_duplicate_slots(self, timetable: TimetableResponse):
        """Check for duplicate time slots in a timetable"""
        slot_counts = {}
        for lecture in timetable.slots:
            slot_key = f"{lecture.day}_{lecture.time}"
            if slot_key in slot_counts:
                slot_counts[slot_key] += 1
                self.violations.append(ConstraintViolation(
                    type="duplicate_slot",
                    description=f"Duplicate time slot {slot_key} in batch {timetable.batch}",
                    affected_entities=[timetable.batch, slot_key],
                    severity="error"
                ))
            else:
                slot_counts[slot_key] = 1
    
    def _check_teacher_availability(self, timetable: TimetableResponse):
        """Check if teachers are available at assigned times"""
        teacher_slots = {}  # teacher -> set of assigned slots
        
        for lecture in timetable.slots:
            teacher = next((t for t in self.request.teachers if t.name == lecture.teacher), None)
            if not teacher:
                self.violations.append(ConstraintViolation(
                    type="unknown_teacher",
                    description=f"Unknown teacher {lecture.teacher}",
                    affected_entities=[lecture.teacher],
                    severity="error"
                ))
                continue
            
            slot_key = f"{lecture.day}_{lecture.time.split('-')[0].split(':')[0]}"
            
            if teacher.id not in teacher_slots:
                teacher_slots[teacher.id] = set()
            
            # Check if teacher is available at this slot
            if slot_key not in teacher.available_slots:
                self.violations.append(ConstraintViolation(
                    type="teacher_unavailable",
                    description=f"Teacher {lecture.teacher} not available at {slot_key}",
                    affected_entities=[lecture.teacher, slot_key],
                    severity="error"
                ))
            
            # Check for teacher overlap across batches
            if slot_key in teacher_slots[teacher.id]:
                self.violations.append(ConstraintViolation(
                    type="teacher_overlap",
                    description=f"Teacher {lecture.teacher} has overlapping assignments at {slot_key}",
                    affected_entities=[lecture.teacher, slot_key],
                    severity="error"
                ))
            else:
                teacher_slots[teacher.id].add(slot_key)
    
    def _check_room_availability(self, timetable: TimetableResponse):
        """Check if rooms are available at assigned times"""
        room_slots = {}  # room -> set of assigned slots
        
        for lecture in timetable.slots:
            room = next((r for r in self.request.rooms if r.name == lecture.room), None)
            if not room:
                self.violations.append(ConstraintViolation(
                    type="unknown_room",
                    description=f"Unknown room {lecture.room}",
                    affected_entities=[lecture.room],
                    severity="error"
                ))
                continue
            
            slot_key = f"{lecture.day}_{lecture.time.split('-')[0].split(':')[0]}"
            
            if room.id not in room_slots:
                room_slots[room.id] = set()
            
            # Check if room is available at this slot
            if slot_key not in room.available_slots:
                self.violations.append(ConstraintViolation(
                    type="room_unavailable",
                    description=f"Room {lecture.room} not available at {slot_key}",
                    affected_entities=[lecture.room, slot_key],
                    severity="error"
                ))
            
            # Check for room overlap across batches
            if slot_key in room_slots[room.id]:
                self.violations.append(ConstraintViolation(
                    type="room_overlap",
                    description=f"Room {lecture.room} has overlapping assignments at {slot_key}",
                    affected_entities=[lecture.room, slot_key],
                    severity="error"
                ))
            else:
                room_slots[room.id].add(slot_key)
    
    def _check_subject_requirements(self, timetable: TimetableResponse, batch: Batch):
        """Check if all required subjects are scheduled"""
        scheduled_subjects = set()
        for lecture in timetable.slots:
            subject = next((s for s in self.request.subjects if s.name == lecture.subject), None)
            if subject:
                scheduled_subjects.add(subject.id)
        
        batch_subjects = get_subjects_for_batch(batch, self.request.subjects)
        required_subjects = set(s.id for s in batch_subjects)
        
        missing_subjects = required_subjects - scheduled_subjects
        for subject_id in missing_subjects:
            subject = self.subject_map[subject_id]
            self.violations.append(ConstraintViolation(
                type="missing_subject",
                description=f"Subject {subject.name} not scheduled for batch {batch.name}",
                affected_entities=[batch.name, subject.name],
                severity="error"
            ))
    
    def _check_break_time_constraints(self, timetable: TimetableResponse):
        """Check that no lectures are scheduled during break time"""
        for lecture in timetable.slots:
            time_str = lecture.time.split('-')[0].split(':')[0]
            if is_break_time(time_str, self.request.break_start, self.request.break_end):
                self.violations.append(ConstraintViolation(
                    type="break_time_violation",
                    description=f"Lecture scheduled during break time: {lecture.day} {lecture.time}",
                    affected_entities=[lecture.subject, lecture.day, lecture.time],
                    severity="error"
                ))
    
    def _check_consecutive_hours_constraints(self, timetable: TimetableResponse):
        """Check consecutive hours constraints for different subject types"""
        # Group lectures by subject and day
        subject_lectures = {}
        for lecture in timetable.slots:
            subject = next((s for s in self.request.subjects if s.name == lecture.subject), None)
            if not subject:
                continue
            
            key = (subject.id, lecture.day)
            if key not in subject_lectures:
                subject_lectures[key] = []
            subject_lectures[key].append(lecture)
        
        for (subject_id, day), lectures in subject_lectures.items():
            subject = self.subject_map[subject_id]
            
            if subject.type == "practical":
                # Practical must be exactly 2 consecutive hours
                if len(lectures) != 1:
                    self.violations.append(ConstraintViolation(
                        type="practical_duration",
                        description=f"Practical subject {subject.name} must be exactly 2 consecutive hours",
                        affected_entities=[subject.name, day],
                        severity="error"
                    ))
                else:
                    # Check if it's actually 2 hours
                    lecture = lectures[0]
                    time_parts = lecture.time.split('-')
                    if len(time_parts) == 2:
                        start_time = time_parts[0].split(':')[0]
                        end_time = time_parts[1].split(':')[0]
                        duration = int(end_time) - int(start_time)
                        if duration != 2:
                            self.violations.append(ConstraintViolation(
                                type="practical_duration",
                                description=f"Practical subject {subject.name} must be exactly 2 hours, got {duration}",
                                affected_entities=[subject.name, day],
                                severity="error"
                            ))
            
            elif subject.type == "theory":
                # Theory max 2 consecutive hours
                total_hours = sum(self._get_lecture_duration(lecture) for lecture in lectures)
                if total_hours > 2:
                    self.violations.append(ConstraintViolation(
                        type="theory_duration",
                        description=f"Theory subject {subject.name} exceeds 2 hours limit: {total_hours} hours",
                        affected_entities=[subject.name, day],
                        severity="warning"
                    ))
            
            elif subject.type == "project":
                # Project min 2 hours
                total_hours = sum(self._get_lecture_duration(lecture) for lecture in lectures)
                if total_hours < 2:
                    self.violations.append(ConstraintViolation(
                        type="project_duration",
                        description=f"Project subject {subject.name} must be at least 2 hours, got {total_hours}",
                        affected_entities=[subject.name, day],
                        severity="error"
                    ))
    
    def _check_room_type_constraints(self, timetable: TimetableResponse):
        """Check that subjects are assigned to appropriate room types"""
        for lecture in timetable.slots:
            subject = next((s for s in self.request.subjects if s.name == lecture.subject), None)
            room = next((r for r in self.request.rooms if r.name == lecture.room), None)
            
            if not subject or not room:
                continue
            
            # Check room type requirements
            if subject.type == "practical" and room.type != "lab":
                self.violations.append(ConstraintViolation(
                    type="room_type_mismatch",
                    description=f"Practical subject {subject.name} assigned to non-lab room {room.name}",
                    affected_entities=[subject.name, room.name],
                    severity="error"
                ))
            
            if subject.type == "theory" and room.type != "classroom":
                self.violations.append(ConstraintViolation(
                    type="room_type_mismatch",
                    description=f"Theory subject {subject.name} assigned to non-classroom room {room.name}",
                    affected_entities=[subject.name, room.name],
                    severity="warning"
                ))
    
    def _get_lecture_duration(self, lecture: Lecture) -> int:
        """Get duration of a lecture in hours"""
        time_parts = lecture.time.split('-')
        if len(time_parts) == 2:
            start_time = int(time_parts[0].split(':')[0])
            end_time = int(time_parts[1].split(':')[0])
            return end_time - start_time
        return 1  # Default to 1 hour if parsing fails

def validate_timetable(request: TimetableRequest, result: SolverResult) -> List[ConstraintViolation]:
    """Main function to validate a timetable solution"""
    validator = TimetableValidator(request)
    return validator.validate_solution(result)
