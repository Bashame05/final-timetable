"""
Modular OR-Tools CP-SAT Solver for Timetable Generation
Refactored for clarity, maintainability, and feasibility
"""
from ortools.sat.python import cp_model
from typing import Dict, List, Tuple, Any, Optional
import logging

logger = logging.getLogger(__name__)


def build_variables(
    model: cp_model.CpModel,
    teachers: List[Dict],
    subjects: List[Dict],
    batches: List[Dict],
    rooms: List[Dict],
    timeslots: List[str]
) -> Dict[str, Any]:
    """
    Create Boolean variables for the timetable scheduling problem.
    
    Variable structure: x[teacher_id][subject_id][batch_id][room_id][slot] = 1 if assigned
    
    Returns:
        Dictionary mapping variable names to variable metadata
    """
    logger.info("Building variables...")
    variables = {}
    
    for teacher in teachers:
        teacher_id = teacher["id"]
        teacher_subjects = teacher.get("subjects", [])
        teacher_slots = teacher.get("availability", [])
        
        for subject in subjects:
            subject_id = subject["id"]
            if subject_id not in teacher_subjects:
                continue
            
            subject_type = subject.get("type", "theory")
            duration = subject.get("hours_per_week", 1)
            
            for batch in batches:
                batch_id = batch["id"]
                batch_subjects = batch.get("subjects", [])
                if subject_id not in batch_subjects:
                    continue
                
                for room in rooms:
                    room_id = room["id"]
                    room_type = room.get("type", "classroom")
                    room_slots = room.get("availability", [])
                    
                    # Room type compatibility check
                    if subject_type == "practical" and room_type != "lab":
                        continue
                    if subject_type == "theory" and room_type != "classroom":
                        continue
                    
                    # Create variables for each valid slot combination
                    for slot in timeslots:
                        if slot not in teacher_slots or slot not in room_slots:
                            continue
                        
                        var_name = f"x_{teacher_id}_{subject_id}_{batch_id}_{room_id}_{slot}"
                        var = model.NewBoolVar(var_name)
                        
                        variables[var_name] = {
                            "var": var,
                            "teacher_id": teacher_id,
                            "subject_id": subject_id,
                            "batch_id": batch_id,
                            "room_id": room_id,
                            "slot": slot,
                            "subject_type": subject_type,
                            "duration": duration
                        }
    
    logger.info(f"Created {len(variables)} variables")
    return variables


def add_no_overlap_constraints(
    model: cp_model.CpModel,
    variables: Dict[str, Any],
    teachers: List[Dict],
    rooms: List[Dict],
    batches: List[Dict],
    timeslots: List[str]
) -> None:
    """
    Add constraints to prevent overlaps:
    - No teacher can teach two classes at the same time
    - No room can host two classes at the same time
    - No batch can attend two classes at the same time
    """
    logger.info("Adding no-overlap constraints...")
    
    # Teacher no-overlap
    for teacher in teachers:
        teacher_id = teacher["id"]
        for slot in timeslots:
            teacher_slot_vars = [
                var_data["var"]
                for var_name, var_data in variables.items()
                if var_data["teacher_id"] == teacher_id and var_data["slot"] == slot
            ]
            if teacher_slot_vars:
                model.Add(sum(teacher_slot_vars) <= 1)
    
    # Room no-overlap
    for room in rooms:
        room_id = room["id"]
        for slot in timeslots:
            room_slot_vars = [
                var_data["var"]
                for var_name, var_data in variables.items()
                if var_data["room_id"] == room_id and var_data["slot"] == slot
            ]
            if room_slot_vars:
                model.Add(sum(room_slot_vars) <= 1)
    
    # Batch no-overlap
    for batch in batches:
        batch_id = batch["id"]
        for slot in timeslots:
            batch_slot_vars = [
                var_data["var"]
                for var_name, var_data in variables.items()
                if var_data["batch_id"] == batch_id and var_data["slot"] == slot
            ]
            if batch_slot_vars:
                model.Add(sum(batch_slot_vars) <= 1)


def add_availability_constraints(
    model: cp_model.CpModel,
    variables: Dict[str, Any],
    teachers: List[Dict],
    rooms: List[Dict]
) -> None:
    """
    Ensure teachers and rooms are only assigned during their available times.
    (This is already handled in build_variables, but explicit constraint for robustness)
    """
    logger.info("Adding availability constraints...")
    
    for var_name, var_data in variables.items():
        teacher_id = var_data["teacher_id"]
        room_id = var_data["room_id"]
        slot = var_data["slot"]
        
        # Find teacher and room
        teacher = next((t for t in teachers if t["id"] == teacher_id), None)
        room = next((r for r in rooms if r["id"] == room_id), None)
        
        if teacher and slot not in teacher.get("availability", []):
            model.Add(var_data["var"] == 0)
        
        if room and slot not in room.get("availability", []):
            model.Add(var_data["var"] == 0)


def add_break_constraints(
    model: cp_model.CpModel,
    variables: Dict[str, Any],
    timeslots: List[str],
    break_start: str = "12",
    break_end: str = "1"
) -> None:
    """
    Prevent scheduling during break time (typically 12 PM - 1 PM).
    """
    logger.info("Adding break-time constraints...")
    
    break_times = {break_start, break_end}
    
    for var_name, var_data in variables.items():
        slot = var_data["slot"]
        # Extract time from slot (format: "Day_Time")
        try:
            _, time = slot.split("_")
            if time in break_times:
                model.Add(var_data["var"] == 0)
        except ValueError:
            pass


def add_duration_constraints(
    model: cp_model.CpModel,
    variables: Dict[str, Any],
    subjects: List[Dict],
    batches: List[Dict],
    timeslots: List[str]
) -> None:
    """
    Add constraints for subject duration requirements:
    - Theory: max 2 consecutive hours
    - Practical: exactly 2 consecutive hours
    - Each subject-batch must be scheduled for required hours
    """
    logger.info("Adding duration constraints...")
    
    # Group variables by subject-batch
    for subject in subjects:
        subject_id = subject["id"]
        subject_type = subject.get("type", "theory")
        required_hours = subject.get("hours_per_week", 1)
        
        for batch in batches:
            batch_id = batch["id"]
            batch_subjects = batch.get("subjects", [])
            
            if subject_id not in batch_subjects:
                continue
            
            # Find all variables for this subject-batch combination
            subject_batch_vars = [
                var_data["var"]
                for var_name, var_data in variables.items()
                if var_data["subject_id"] == subject_id and var_data["batch_id"] == batch_id
            ]
            
            if not subject_batch_vars:
                logger.warning(f"No variables for subject {subject_id} in batch {batch_id}")
                continue
            
            # Constraint: Total assignments must equal required hours
            model.Add(sum(subject_batch_vars) == required_hours)
            
            # Type-specific constraints
            if subject_type == "practical":
                # Practical must be exactly 2 hours and in one block
                if required_hours == 2:
                    _add_consecutive_block_constraint(
                        model, variables, subject_id, batch_id, 2, timeslots
                    )
            elif subject_type == "theory":
                # Theory max 2 consecutive hours
                _add_max_consecutive_constraint(
                    model, variables, subject_id, batch_id, 2, timeslots
                )


def _add_consecutive_block_constraint(
    model: cp_model.CpModel,
    variables: Dict[str, Any],
    subject_id: str,
    batch_id: str,
    duration: int,
    timeslots: List[str]
) -> None:
    """
    Enforce that a subject is scheduled in one consecutive block of 'duration' hours.
    """
    logger.debug(f"Adding consecutive block constraint for {subject_id}-{batch_id}")
    
    # Get all unique days from timeslots
    days = set()
    for slot in timeslots:
        try:
            day, _ = slot.split("_")
            days.add(day)
        except ValueError:
            pass
    
    block_vars = []
    
    for day in days:
        day_slots = [s for s in timeslots if s.startswith(f"{day}_")]
        
        # Try each possible starting position
        for i in range(len(day_slots) - duration + 1):
            consecutive_slots = day_slots[i:i + duration]
            
            # Check if all slots in this block are available
            block_assignments = [
                var_data["var"]
                for var_name, var_data in variables.items()
                if (var_data["subject_id"] == subject_id and
                    var_data["batch_id"] == batch_id and
                    var_data["slot"] in consecutive_slots)
            ]
            
            if len(block_assignments) == duration:
                # Create a block variable
                block_var = model.NewBoolVar(f"block_{subject_id}_{batch_id}_{day}_{i}")
                block_vars.append(block_var)
                
                # If block is chosen, all assignments in it must be 1
                model.Add(sum(block_assignments) == duration).OnlyEnforceIf(block_var)
                model.Add(sum(block_assignments) == 0).OnlyEnforceIf(block_var.Not())
    
    # Exactly one block must be chosen
    if block_vars:
        model.Add(sum(block_vars) == 1)


def _add_max_consecutive_constraint(
    model: cp_model.CpModel,
    variables: Dict[str, Any],
    subject_id: str,
    batch_id: str,
    max_consecutive: int,
    timeslots: List[str]
) -> None:
    """
    Enforce that a subject cannot have more than 'max_consecutive' hours in a row.
    """
    logger.debug(f"Adding max consecutive constraint for {subject_id}-{batch_id}")
    
    days = set()
    for slot in timeslots:
        try:
            day, _ = slot.split("_")
            days.add(day)
        except ValueError:
            pass
    
    for day in days:
        day_slots = [s for s in timeslots if s.startswith(f"{day}_")]
        
        # Check each window of (max_consecutive + 1) slots
        for i in range(len(day_slots) - max_consecutive):
            window_slots = day_slots[i:i + max_consecutive + 1]
            
            window_assignments = [
                var_data["var"]
                for var_name, var_data in variables.items()
                if (var_data["subject_id"] == subject_id and
                    var_data["batch_id"] == batch_id and
                    var_data["slot"] in window_slots)
            ]
            
            if len(window_assignments) == max_consecutive + 1:
                # No more than max_consecutive assignments in this window
                model.Add(sum(window_assignments) <= max_consecutive)


def solve_timetable(
    model: cp_model.CpModel,
    variables: Dict[str, Any],
    time_limit: int = 60
) -> Tuple[bool, Dict[str, Any]]:
    """
    Configure and run the CP-SAT solver.
    
    Returns:
        Tuple of (success: bool, solution: dict)
    """
    logger.info("Configuring solver...")
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.log_search_progress = False
    
    logger.info("Solving timetable problem...")
    status = solver.Solve(model)
    
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        logger.info("✅ Feasible solution found!")
        
        solution = {}
        for var_name, var_data in variables.items():
            if solver.Value(var_data["var"]) == 1:
                solution[var_name] = var_data
        
        return True, solution
    else:
        logger.warning("❌ No feasible solution found")
        return False, {}


def format_solution(
    solution: Dict[str, Any],
    teachers: List[Dict],
    subjects: List[Dict],
    rooms: List[Dict],
    batches: List[Dict]
) -> List[Dict]:
    """
    Format the solver solution into a JSON-friendly timetable.
    
    Returns:
        List of scheduled lectures
    """
    logger.info("Formatting solution...")
    
    timetable = []
    
    for var_name, var_data in solution.items():
        teacher_id = var_data["teacher_id"]
        subject_id = var_data["subject_id"]
        batch_id = var_data["batch_id"]
        room_id = var_data["room_id"]
        slot = var_data["slot"]
        
        # Find full details
        teacher = next((t for t in teachers if t["id"] == teacher_id), None)
        subject = next((s for s in subjects if s["id"] == subject_id), None)
        batch = next((b for b in batches if b["id"] == batch_id), None)
        room = next((r for r in rooms if r["id"] == room_id), None)
        
        if teacher and subject and batch and room:
            day, time = slot.split("_")
            
            timetable.append({
                "subject": subject.get("name", subject_id),
                "subject_id": subject_id,
                "teacher": teacher.get("name", teacher_id),
                "teacher_id": teacher_id,
                "room": room.get("name", room_id),
                "room_id": room_id,
                "batch": batch.get("name", batch_id),
                "batch_id": batch_id,
                "day": day,
                "time": time,
                "slot": slot,
                "duration": var_data["duration"],
                "type": var_data["subject_type"]
            })
    
    # Sort by day and time
    timetable.sort(key=lambda x: (x["day"], x["time"]))
    
    logger.info(f"Formatted {len(timetable)} lectures")
    return timetable


def generate_timetable(
    teachers: List[Dict],
    subjects: List[Dict],
    rooms: List[Dict],
    batches: List[Dict],
    timeslots: List[str],
    break_start: str = "12",
    break_end: str = "1",
    time_limit: int = 60
) -> Dict[str, Any]:
    """
    Main entry point for timetable generation.
    
    Args:
        teachers: List of teacher dicts with id, name, subjects, availability
        subjects: List of subject dicts with id, name, type, hours_per_week
        rooms: List of room dicts with id, name, type, availability
        batches: List of batch dicts with id, name, subjects
        timeslots: List of all time slots (e.g., ["Mon_9", "Mon_10", ...])
        break_start: Start of break time (default "12")
        break_end: End of break time (default "1")
        time_limit: Solver time limit in seconds (default 60)
    
    Returns:
        Dict with status, timetable, and error messages
    """
    logger.info("=" * 60)
    logger.info("Starting timetable generation")
    logger.info(f"Teachers: {len(teachers)}, Subjects: {len(subjects)}, Rooms: {len(rooms)}, Batches: {len(batches)}")
    logger.info("=" * 60)
    
    try:
        # Filter out break times from timeslots
        filtered_slots = [
            slot for slot in timeslots
            if not (slot.endswith(f"_{break_start}") or slot.endswith(f"_{break_end}"))
        ]
        
        logger.info(f"Available slots (excluding breaks): {len(filtered_slots)}")
        
        # Create model
        model = cp_model.CpModel()
        
        # Build variables
        variables = build_variables(model, teachers, subjects, batches, rooms, filtered_slots)
        
        if not variables:
            logger.error("No variables created! Check data consistency.")
            return {
                "status": "failed",
                "reason": "no_variables",
                "message": "No valid variable combinations found. Check teacher/room availability and subject-batch assignments.",
                "timetable": []
            }
        
        # Add constraints
        add_no_overlap_constraints(model, variables, teachers, rooms, batches, filtered_slots)
        add_availability_constraints(model, variables, teachers, rooms)
        add_break_constraints(model, variables, filtered_slots, break_start, break_end)
        add_duration_constraints(model, variables, subjects, batches, filtered_slots)
        
        # Solve
        success, solution = solve_timetable(model, variables, time_limit)
        
        if success:
            timetable = format_solution(solution, teachers, subjects, rooms, batches)
            return {
                "status": "success",
                "message": "✅ Feasible timetable generated",
                "timetable": timetable,
                "total_assignments": len(timetable)
            }
        else:
            return {
                "status": "failed",
                "reason": "infeasible",
                "message": "❌ No feasible solution found. The constraints cannot be satisfied with the given data.",
                "timetable": []
            }
    
    except Exception as e:
        logger.error(f"Error during timetable generation: {str(e)}", exc_info=True)
        return {
            "status": "failed",
            "reason": "internal_error",
            "message": f"Internal error: {str(e)}",
            "timetable": []
        }
