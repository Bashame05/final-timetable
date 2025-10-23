"""
FastAPI application for AI-based college timetable scheduler
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import List
import uvicorn

from .models import (
    TimetableRequest, TimetableResponse, SolverResult, 
    ConstraintViolation
)
from .solver import solve_timetable
from .validator import validate_timetable
from .modular_solver import generate_timetable as modular_generate_timetable

# Import for the new simplified solver
from ortools.sat.python import cp_model
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Timetable Scheduler",
    description="Backend API for AI-based college timetable scheduling using OR-Tools CP-SAT solver",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Timetable Scheduler API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "timetable-scheduler"}

@app.post("/api/timetable/solve", response_model=SolverResult)
async def solve_timetable_endpoint(request: TimetableRequest):
    """
    Solve timetable scheduling problem using OR-Tools CP-SAT solver
    
    This endpoint takes a timetable request with teachers, rooms, subjects, and batches,
    and returns an optimized timetable solution that satisfies all constraints.
    """
    try:
        logger.info(f"Received timetable request for {len(request.batches)} batches")
        
        # Validate input
        validation_errors = _validate_request(request)
        if validation_errors:
            return SolverResult(
                success=False,
                timetables=[],
                errors=validation_errors
            )
        
        # Solve the timetable
        result = solve_timetable(request)
        
        # Validate the solution
        if result.success:
            violations = validate_timetable(request, result)
            if violations:
                # Add violations as warnings/errors
                for violation in violations:
                    if violation.severity == "error":
                        result.errors.append(violation.description)
                    else:
                        result.warnings.append(violation.description)
        
        logger.info(f"Timetable solution completed. Success: {result.success}")
        return result
        
    except Exception as e:
        logger.error(f"Error solving timetable: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/api/timetable/validate")
async def validate_timetable_endpoint(
    request: TimetableRequest, 
    result: SolverResult
):
    """
    Validate a timetable solution against constraints
    
    This endpoint validates an existing timetable solution and returns
    any constraint violations found.
    """
    try:
        logger.info("Validating timetable solution")
        
        violations = validate_timetable(request, result)
        
        return {
            "valid": len([v for v in violations if v.severity == "error"]) == 0,
            "violations": violations,
            "error_count": len([v for v in violations if v.severity == "error"]),
            "warning_count": len([v for v in violations if v.severity == "warning"])
        }
        
    except Exception as e:
        logger.error(f"Error validating timetable: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/api/timetable/generate")
async def generate_timetable_endpoint(data: dict):
    """
    Generate a feasible timetable using modular CP-SAT solver.
    
    Input format:
    {
        "teachers": [
            {"id": "T1", "name": "Dr. Smith", "subjects": ["OS"], "availability": ["Mon_9", "Mon_10"]}
        ],
        "subjects": [
            {"id": "OS", "name": "Operating Systems", "type": "theory", "hours_per_week": 2}
        ],
        "rooms": [
            {"id": "C301", "name": "Classroom 301", "type": "classroom", "availability": ["Mon_9", "Mon_10"]}
        ],
        "batches": [
            {"id": "B1", "name": "TY CSE A", "subjects": ["OS"]}
        ],
        "timeslots": ["Mon_9", "Mon_10", "Tue_9", "Tue_10"],
        "break_start": "12",
        "break_end": "1"
    }
    """
    try:
        logger.info("Generating timetable with modular solver")
        
        # Extract data
        teachers = data.get("teachers", [])
        subjects = data.get("subjects", [])
        rooms = data.get("rooms", [])
        batches = data.get("batches", [])
        timeslots = data.get("timeslots", [])
        break_start = data.get("break_start", "12")
        break_end = data.get("break_end", "1")
        time_limit = data.get("time_limit", 60)
        
        # Call modular solver
        result = modular_generate_timetable(
            teachers=teachers,
            subjects=subjects,
            rooms=rooms,
            batches=batches,
            timeslots=timeslots,
            break_start=break_start,
            break_end=break_end,
            time_limit=time_limit
        )
        
        return result
            
    except Exception as e:
        logger.error(f"Error generating timetable: {str(e)}", exc_info=True)
        return {
            "status": "failed",
            "reason": "internal_error",
            "message": f"Internal error: {str(e)}",
            "timetable": []
        }

@app.get("/api/timetable/example")
async def get_example_request():
    """
    Get an example timetable request for testing
    """
    return {
        "teachers": [
            {
                "id": "T1",
                "name": "Dr. Smith",
                "available_slots": ["Mon_9", "Mon_10", "Mon_11", "Tue_9", "Tue_10", "Wed_9", "Wed_10"],
                "subjects": ["OS", "DBMS"]
            },
            {
                "id": "T2", 
                "name": "Prof. Johnson",
                "available_slots": ["Mon_2", "Mon_3", "Tue_2", "Tue_3", "Wed_2", "Wed_3"],
                "subjects": ["ML", "AI"]
            },
            {
                "id": "T3",
                "name": "Dr. Brown",
                "available_slots": ["Mon_9", "Mon_10", "Tue_9", "Tue_10", "Wed_9", "Wed_10"],
                "subjects": ["MLBC_Lab"]
            }
        ],
        "rooms": [
            {
                "id": "C301",
                "name": "Classroom 301",
                "type": "classroom",
                "available_slots": ["Mon_9", "Mon_10", "Mon_11", "Mon_2", "Mon_3", "Tue_9", "Tue_10", "Tue_11", "Tue_2", "Tue_3", "Wed_9", "Wed_10", "Wed_11", "Wed_2", "Wed_3"],
                "capacity": 60
            },
            {
                "id": "Lab2",
                "name": "Computer Lab 2",
                "type": "lab",
                "available_slots": ["Mon_9", "Mon_10", "Mon_11", "Mon_2", "Mon_3", "Tue_9", "Tue_10", "Tue_11", "Tue_2", "Tue_3", "Wed_9", "Wed_10", "Wed_11", "Wed_2", "Wed_3"],
                "capacity": 30
            }
        ],
        "subjects": [
            {
                "id": "OS",
                "name": "Operating Systems",
                "type": "theory",
                "duration": 2,
                "teachers": ["T1"],
                "required_room_type": "classroom"
            },
            {
                "id": "ML",
                "name": "Machine Learning",
                "type": "theory", 
                "duration": 2,
                "teachers": ["T2"],
                "required_room_type": "classroom"
            },
            {
                "id": "MLBC_Lab",
                "name": "MLBC Lab",
                "type": "practical",
                "duration": 2,
                "teachers": ["T3"],
                "required_room_type": "lab"
            }
        ],
        "batches": [
            {
                "id": "TYCSE_A",
                "name": "TY CSE A",
                "subjects": ["OS", "ML", "MLBC_Lab"],
                "strength": 60
            }
        ],
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "time_slots": ["9", "10", "11", "12", "1", "2", "3"],
        "break_start": "12",
        "break_end": "1"
    }

def _validate_request(request: TimetableRequest) -> List[str]:
    """Validate the incoming timetable request"""
    errors = []
    
    # Check if we have required data
    if not request.teachers:
        errors.append("No teachers provided")
    
    if not request.rooms:
        errors.append("No rooms provided")
    
    if not request.subjects:
        errors.append("No subjects provided")
    
    if not request.batches:
        errors.append("No batches provided")
    
    if not request.days:
        errors.append("No days provided")
    
    if not request.time_slots:
        errors.append("No time slots provided")
    
    # Check for duplicate IDs
    teacher_ids = [t.id for t in request.teachers]
    if len(teacher_ids) != len(set(teacher_ids)):
        errors.append("Duplicate teacher IDs found")
    
    room_ids = [r.id for r in request.rooms]
    if len(room_ids) != len(set(room_ids)):
        errors.append("Duplicate room IDs found")
    
    subject_ids = [s.id for s in request.subjects]
    if len(subject_ids) != len(set(subject_ids)):
        errors.append("Duplicate subject IDs found")
    
    batch_ids = [b.id for b in request.batches]
    if len(batch_ids) != len(set(batch_ids)):
        errors.append("Duplicate batch IDs found")
    
    # Check if batches have subjects
    for batch in request.batches:
        if not batch.subjects:
            errors.append(f"Batch {batch.name} has no subjects assigned")
    
    # Check if subjects have teachers
    for subject in request.subjects:
        if not subject.teachers:
            errors.append(f"Subject {subject.name} has no teachers assigned")
    
    return errors

# Helper functions for the simplified timetable generator

def _can_schedule_consecutive(start_slot: str, duration: int, all_slots: List[str], 
                            teacher_slots: List[str], room_slots: List[str]) -> bool:
    """Check if we can schedule consecutive slots for the given duration"""
    try:
        start_index = all_slots.index(start_slot)
        
        # Check if we have enough consecutive slots
        for i in range(duration):
            if start_index + i >= len(all_slots):
                return False
            
            slot = all_slots[start_index + i]
            
            # Check if slot is available for both teacher and room
            if slot not in teacher_slots or slot not in room_slots:
                return False
            
            # Check if it's break time (12 PM - 1 PM)
            if _is_break_time(slot):
                return False
        
        return True
    except ValueError:
        return False

def _get_consecutive_slots_from_available(start_slot: str, duration: int, 
                                        teacher_slots: List[str], room_slots: List[str]) -> List[str]:
    """Get consecutive slots from available slots for teacher and room"""
    try:
        # Find the start slot in teacher's available slots
        if start_slot not in teacher_slots or start_slot not in room_slots:
            return []
        
        # Get the day and time from start_slot
        day, time = start_slot.split("_")
        
        # Extract all unique times from teacher_slots and room_slots, sorted
        all_times_set = set()
        for slot in teacher_slots + room_slots:
            try:
                _, t = slot.split("_")
                if not _is_break_time(slot):
                    all_times_set.add(t)
            except ValueError:
                pass
        
        # Sort times numerically (9, 10, 11, 2, 3 → sorted as strings: "10", "11", "2", "3", "9")
        # Better: sort by converting to int where possible, handling non-numeric gracefully
        all_times = sorted(all_times_set, key=lambda x: (int(x) if x.isdigit() else float('inf')))
        
        try:
            start_index = all_times.index(time)
        except ValueError:
            return []  # Start time not in valid times
        
        # Find consecutive slots on the same day
        consecutive_slots = [start_slot]
        
        for i in range(1, duration):
            if start_index + i >= len(all_times):
                return []  # Not enough slots remaining
            
            next_time = all_times[start_index + i]
            next_slot = f"{day}_{next_time}"
            
            if next_slot in teacher_slots and next_slot in room_slots:
                consecutive_slots.append(next_slot)
            else:
                return []  # Can't get consecutive slots
        
        return consecutive_slots
    except (ValueError, IndexError):
        return []

def _is_break_time(slot: str) -> bool:
    """Check if a slot falls during break time (12 PM - 1 PM)"""
    # Only treat exact hour tokens 12 and 1 as break hours, not substrings like 10/11
    try:
        _, time_token = slot.split("_", 1)
        return time_token in ("12", "1")
    except ValueError:
        return False

def _is_slot_in_range(slot: str, start_slot: str, duration: int, all_slots: List[str]) -> bool:
    """Check if a slot falls within the range of consecutive slots"""
    try:
        start_index = all_slots.index(start_slot)
        slot_index = all_slots.index(slot)
        
        return start_index <= slot_index < start_index + duration
    except ValueError:
        return False

def _get_consecutive_slots(start_slot: str, duration: int, all_slots: List[str]) -> List[str]:
    """Get consecutive slots starting from start_slot for the given duration"""
    try:
        start_index = all_slots.index(start_slot)
        return all_slots[start_index:start_index + duration]
    except ValueError:
        return []

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
