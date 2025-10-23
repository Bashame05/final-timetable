"""
OR-Tools CP-SAT Solver for Timetable Generation - FIXED VERSION
"""
from ortools.sat.python import cp_model
from typing import List, Dict, Tuple, Optional
import logging
# Assuming all models and utils functions are correctly defined in their respective files.
from .models import (
    TimetableRequest, TimetableResponse, SolverResult, 
    Teacher, Room, Subject, Batch, Lecture
)
from .utils import (
    create_time_slot_key, parse_time_slot, is_break_time,
    get_available_slots_for_teacher, get_available_slots_for_room,
    get_teachers_for_subject, get_rooms_for_subject,
    can_schedule_consecutive_hours, get_consecutive_slots,
    create_lecture_from_assignment, get_subjects_for_batch
)

logger = logging.getLogger(__name__)

class TimetableSolver:
    def __init__(self, request: TimetableRequest):
        self.request = request
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        
        # Core Variable: (batch, subject, slot) -> BoolVar. 1 if subject is taught to batch at slot.
        self.assignments = {} 
        
        # New Linking Variables: (batch, subject, slot, teacher) -> BoolVar. 1 if T teaches S to B at slot.
        self.lecture_teacher = {} 
        # New Linking Variables: (batch, subject, slot, room) -> BoolVar. 1 if B is in R for S at slot.
        self.lecture_room = {} 
        
        # Index mappings
        self.teacher_map = {t.id: t for t in request.teachers}
        self.room_map = {r.id: r for r in request.rooms}
        self.subject_map = {s.id: s for s in request.subjects}
        self.batch_map = {b.id: b for b in request.batches}
        
        # Available slots (excluding break time)
        self.available_slots = self._get_available_slots()
        
    def _get_available_slots(self) -> List[str]:
        """Get all available time slots excluding break time"""
        available = []
        for day in self.request.days:
            for time in self.request.time_slots:
                if not is_break_time(time, self.request.break_start, self.request.break_end):
                    available.append(create_time_slot_key(day, time))
        return available
    
    def _create_variables(self):
        """Create CP-SAT variables for assignments and resource links"""
        logger.info("Creating CP-SAT variables...")
        
        # 1. Create core assignment variables for each batch-subject-slot combination
        for batch in self.request.batches:
            batch_subjects = get_subjects_for_batch(batch, self.request.subjects)
            for subject in batch_subjects:
                for slot in self.available_slots:
                    var_name = f"assign_{batch.id}_{subject.id}_{slot}"
                    self.assignments[(batch.id, subject.id, slot)] = self.model.NewBoolVar(var_name)
                    
                    # 2. Create linking variables for Teacher and Room
                    
                    # Teacher links
                    available_teachers = get_teachers_for_subject(subject, self.request.teachers)
                    for teacher in available_teachers:
                        # Check teacher's general availability for this slot
                        day, time = parse_time_slot(slot)
                        teacher_available_slots = get_available_slots_for_teacher(
                            teacher, self.request.days, self.request.time_slots,
                            self.request.break_start, self.request.break_end
                        )
                        if slot in teacher_available_slots:
                            var_name_t = f"teach_{batch.id}_{subject.id}_{slot}_{teacher.id}"
                            self.lecture_teacher[(batch.id, subject.id, slot, teacher.id)] = self.model.NewBoolVar(var_name_t)
                            
                    # Room links
                    suitable_rooms = get_rooms_for_subject(subject, self.request.rooms)
                    for room in suitable_rooms:
                        # Check room's general availability for this slot
                        day, time = parse_time_slot(slot)
                        room_available_slots = get_available_slots_for_room(
                            room, self.request.days, self.request.time_slots,
                            self.request.break_start, self.request.break_end
                        )
                        if slot in room_available_slots:
                            var_name_r = f"room_{batch.id}_{subject.id}_{slot}_{room.id}"
                            self.lecture_room[(batch.id, subject.id, slot, room.id)] = self.model.NewBoolVar(var_name_r)

    def _add_basic_constraints(self):
        """Add basic scheduling constraints, including resource allocation logic."""
        logger.info("Adding basic constraints...")
        
        # Constraint 1: Subject Load (Each batch must have exactly one assignment for each subject)
        for batch in self.request.batches:
            batch_subjects = get_subjects_for_batch(batch, self.request.subjects)
            for subject in batch_subjects:
                subject_assignments = [
                    self.assignments[(batch.id, subject.id, slot)] 
                    for slot in self.available_slots
                    if (batch.id, subject.id, slot) in self.assignments
                ]
                
                if not subject_assignments:
                    logger.warning(f"Batch {batch.id} / Subject {subject.id} has no available slots. Infeasible.")
                    # If this happens, the problem is infeasible, but we let CP-SAT find it.
                    continue

                # Sum of assignments must equal the required duration (assuming a subject is 1 hour per slot)
                # NOTE: The original code used '1' regardless of subject duration. 
                # Assuming 'duration' means total required slots for now, matching the original (but flawed) logic.
                # A better model would track total hours needed across the week.
                self.model.Add(sum(subject_assignments) == subject.duration) 

        # Constraint 2: Resource Linkage (Teacher and Room Selection)
        for (batch_id, subject_id, slot), assignment_var in self.assignments.items():
            
            # Link to Teacher
            teacher_links = [
                self.lecture_teacher[(batch_id, subject_id, slot, t_id)]
                for t_id in self.teacher_map
                if (batch_id, subject_id, slot, t_id) in self.lecture_teacher
            ]
            
            # If the lecture is scheduled (assignment_var = 1), exactly one teacher must be selected.
            # If the lecture is NOT scheduled, zero teachers must be selected.
            self.model.Add(sum(teacher_links) == assignment_var)
            
            # Link to Room
            room_links = [
                self.lecture_room[(batch_id, subject_id, slot, r_id)]
                for r_id in self.room_map
                if (batch_id, subject_id, slot, r_id) in self.lecture_room
            ]
            
            # If the lecture is scheduled (assignment_var = 1), exactly one room must be selected.
            # If the lecture is NOT scheduled, zero rooms must be selected.
            self.model.Add(sum(room_links) == assignment_var)

        # Constraint 3: No Teacher Overlap (A teacher can only be assigned to one lecture per slot)
        for slot in self.available_slots:
            for teacher in self.request.teachers:
                # Sum of all teacher links involving this teacher at this slot
                teacher_usages = [
                    link_var 
                    for (b_id, s_id, sl, t_id), link_var in self.lecture_teacher.items()
                    if sl == slot and t_id == teacher.id
                ]
                
                # If the teacher is available for this slot, they can only be used once.
                if teacher_usages:
                    self.model.Add(sum(teacher_usages) <= 1)
                
        # Constraint 4: No Room Overlap (A room can only be assigned to one lecture per slot)
        for slot in self.available_slots:
            for room in self.request.rooms:
                # Sum of all room links involving this room at this slot
                room_usages = [
                    link_var 
                    for (b_id, s_id, sl, r_id), link_var in self.lecture_room.items()
                    if sl == slot and r_id == room.id
                ]
                
                # If the room is available for this slot, it can only be used once.
                if room_usages:
                    self.model.Add(sum(room_usages) <= 1)

    def _add_subject_type_constraints(self):
        """Add constraints specific to subject types (Consecutive Hours FIX)"""
        logger.info("Adding subject type constraints...")
        
        for batch in self.request.batches:
            batch_subjects = get_subjects_for_batch(batch, self.request.subjects)
            for subject in batch_subjects:
                
                # Practical: Must be scheduled in one block of 2 consecutive hours.
                if subject.type == "practical" and subject.duration == 2:
                    # Constraint: The two required slots MUST be placed in a single 2-hour block.
                    self._add_fixed_block_constraint(batch.id, subject.id, 2)
                    
                # Theory/Project: Maximum consecutive hours (e.g., max 2), but total duration is multiple of 1.
                # Project may have a minimum duration (e.g., min 2 hours per session).
                elif subject.type in ["theory", "project"]:
                    max_consecutive = subject.max_consecutive_hours if hasattr(subject, 'max_consecutive_hours') else 2
                    
                    # Constraint: Ensure no more than 'max_consecutive' slots are scheduled contiguously.
                    self._add_max_consecutive_constraint(batch.id, subject.id, max_consecutive)
    
    def _add_fixed_block_constraint(self, batch_id: str, subject_id: str, duration: int):
        """Enforces that a subject's total duration MUST be scheduled as one single block of 'duration' hours."""
        
        all_block_vars = []
        
        for day in self.request.days:
            # Iterate through all possible starting times
            for start_time in self.request.time_slots:
                
                consecutive_slots = get_consecutive_slots(
                    create_time_slot_key(day, start_time), duration,
                    self.request.days, self.request.time_slots
                )
                
                if len(consecutive_slots) == duration:
                    # Create a variable representing the choice of this specific block
                    block_var = self.model.NewBoolVar(f"block_{batch_id}_{subject_id}_{day}_{start_time}")
                    all_block_vars.append(block_var)
                    
                    # Force all assignments in this block to be equal to the block_var
                    literals = []
                    for slot in consecutive_slots:
                        if (batch_id, subject_id, slot) in self.assignments:
                            literals.append(self.assignments[(batch_id, subject_id, slot)])
                        else:
                            # If any slot in the block is unavailable (e.g., break time), this block is impossible
                            self.model.Add(block_var == 0)
                            literals = [] # Clear literals to skip the next constraint
                            break 
                            
                    if literals:
                        # If the block is chosen, all assignments must be 1.
                        # If the block is NOT chosen, all assignments are free to be 0 (but must be 0 for this block)
                        self.model.Add(sum(literals) == duration).OnlyEnforceIf(block_var)
                        self.model.Add(sum(literals) == 0).OnlyEnforceIf(block_var.Not())
                        
        # Constraint: Exactly one block must be chosen for the subject's required duration
        if all_block_vars:
            self.model.Add(sum(all_block_vars) == 1)

    def _add_max_consecutive_constraint(self, batch_id: str, subject_id: str, max_duration: int):
        """Enforces that a subject's total duration cannot have more than 'max_duration' consecutive slots."""
        
        # Iterate over all possible blocks of size (max_duration + 1)
        for day in self.request.days:
            
            # Time slots, including an artificial end slot for iteration
            slots = [create_time_slot_key(day, t) for t in self.request.time_slots]
            
            for i in range(len(slots) - max_duration):
                
                # Check the block of (max_duration + 1) slots
                consecutive_slots = [
                    slots[i+j] for j in range(max_duration + 1) 
                    if slots[i+j] in self.available_slots
                ]
                
                # Check for breaks within the block (which inherently breaks the sequence)
                has_break = any(
                    is_break_time(parse_time_slot(s)[1], self.request.break_start, self.request.break_end)
                    for s in consecutive_slots
                )
                
                if len(consecutive_slots) == max_duration + 1 and not has_break:
                    
                    # Literals for the assignments in this (max_duration + 1) block
                    long_block_assignments = []
                    
                    for slot in consecutive_slots:
                        if (batch_id, subject_id, slot) in self.assignments:
                            long_block_assignments.append(self.assignments[(batch_id, subject_id, slot)])
                        
                    if len(long_block_assignments) == max_duration + 1:
                        # Constraint: The sum of assignments in any (max_duration + 1) block must be <= max_duration
                        # This prevents an assignment in all (max_duration + 1) slots.
                        self.model.Add(sum(long_block_assignments) <= max_duration)

    def _add_room_type_constraints(self):
        """This constraint is now handled entirely within _create_variables and _add_basic_constraints 
        by only creating lecture_room variables for suitable rooms."""
        logger.info("Room type constraints handled by variable creation.")
        pass
    
    def _add_teacher_subject_constraints(self):
        """This constraint is now handled entirely within _create_variables and _add_basic_constraints 
        by only creating lecture_teacher variables for available teachers."""
        logger.info("Teacher-subject constraints handled by variable creation.")
        pass
    
    def _add_break_time_constraints(self):
        """Break time is already excluded from self.available_slots and the variables, 
        but an explicit constraint ensures no assignments are made during those times 
        (Good for robustness)."""
        logger.info("Adding explicit break time constraints...")
        
        # Find all break slots (if any were created in self.assignments for error checking)
        break_slots = []
        for day in self.request.days:
            for time in self.request.time_slots:
                if is_break_time(time, self.request.break_start, self.request.break_end):
                    break_slots.append(create_time_slot_key(day, time))
        
        for batch in self.request.batches:
            batch_subjects = get_subjects_for_batch(batch, self.request.subjects)
            for subject in batch_subjects:
                for slot in break_slots:
                    if (batch.id, subject.id, slot) in self.assignments:
                        # Explicitly set assignment to 0 during break time
                        self.model.Add(self.assignments[(batch.id, subject.id, slot)] == 0)
    
    def solve(self) -> SolverResult:
        """Solve the timetable scheduling problem"""
        logger.info("Starting timetable solver...")
        
        try:
            # 1. Create variables (including the crucial linking variables)
            self._create_variables()
            
            # 2. Add constraints
            self._add_basic_constraints()
            self._add_subject_type_constraints()
            self._add_room_type_constraints() # Now mostly a placeholder
            self._add_teacher_subject_constraints() # Now mostly a placeholder
            self._add_break_time_constraints()
            
            # 3. Add Objective (e.g., maximize utilization or minimize travel)
            # The current problem is a SAT (satisfiability) problem, so no objective is strictly needed.
            # We'll stick to satisfaction.
            
            # Set solver parameters
            self.solver.parameters.max_time_in_seconds = 300.0
            self.solver.parameters.log_search_progress = True
            
            # Solve
            logger.info("Solving CP-SAT model...")
            status = self.solver.Solve(self.model)
            
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                logger.info("Solution found!")
                return self._extract_solution()
            else:
                # This is where failure occurs if constraints are too strict
                logger.error("No solution found")
                return SolverResult(
                    success=False,
                    timetables=[],
                    errors=["No feasible solution found for the given constraints. Check your input data (e.g., available rooms/teachers vs. required hours)."]
                )
                
        except Exception as e:
            logger.error(f"Error during solving: {str(e)}")
            return SolverResult(
                success=False,
                timetables=[],
                errors=[f"Solver internal error: {str(e)}"]
            )
    
    def _extract_solution(self) -> SolverResult:
        """Extract solution using the lecture_teacher and lecture_room linking variables."""
        logger.info("Extracting solution...")
        
        timetables = []
        
        for batch in self.request.batches:
            batch_lectures = []
            batch_subjects = get_subjects_for_batch(batch, self.request.subjects)
            
            for subject in batch_subjects:
                for slot in self.available_slots:
                    if (batch.id, subject.id, slot) in self.assignments:
                        if self.solver.Value(self.assignments[(batch.id, subject.id, slot)]) == 1:
                            
                            # Find assigned teacher using lecture_teacher links
                            assigned_teacher = None
                            for t_id in self.teacher_map:
                                if (batch.id, subject.id, slot, t_id) in self.lecture_teacher:
                                    if self.solver.Value(self.lecture_teacher[(batch.id, subject.id, slot, t_id)]) == 1:
                                        assigned_teacher = self.teacher_map[t_id]
                                        break
                                        
                            # Find assigned room using lecture_room links
                            assigned_room = None
                            for r_id in self.room_map:
                                if (batch.id, subject.id, slot, r_id) in self.lecture_room:
                                    if self.solver.Value(self.lecture_room[(batch.id, subject.id, slot, r_id)]) == 1:
                                        assigned_room = self.room_map[r_id]
                                        break
                                        
                            if assigned_teacher and assigned_room:
                                lecture = create_lecture_from_assignment(
                                    {
                                        "subject": subject.id,
                                        "teacher": assigned_teacher.id,
                                        "room": assigned_room.id,
                                        "slot": slot,
                                        "batch": batch.id
                                    },
                                    self.request.subjects, self.request.teachers, 
                                    self.request.rooms, self.request.batches
                                )
                                batch_lectures.append(lecture)
            
            # Sort lectures by day and time
            batch_lectures.sort(key=lambda x: (x.day, x.time))
            
            timetables.append(TimetableResponse(
                batch=batch.name,
                slots=batch_lectures,
                status="success"
            ))
        
        return SolverResult(
            success=True,
            timetables=timetables,
            errors=[],
            warnings=[]
        )
        
    # The redundant _find_assigned_teacher and _find_assigned_room methods are removed
    # as the extraction logic is now contained in _extract_solution.

def solve_timetable(request: TimetableRequest) -> SolverResult:
    """Main function to solve timetable scheduling"""
    solver = TimetableSolver(request)
    return solver.solve()