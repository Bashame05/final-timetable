"""
Simplified Modular Timetable Solver - Relaxed constraints for feasibility
"""

from ortools.sat.python import cp_model
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)


def generate_time_slots(week_config: Dict[str, Any]) -> List[Tuple[str, int]]:
    """Generate all valid time slots excluding lunch period."""
    slots = []
    working_days = week_config.get("working_days", ["Mon", "Tue", "Wed", "Thu", "Fri"])
    start_time = week_config.get("week_start_time", "09:00")
    end_time = week_config.get("week_end_time", "16:00")
    lunch_start = week_config.get("lunch_start", "13:00")
    lunch_end = week_config.get("lunch_end", "14:00")
    
    start_hour = int(start_time.split(":")[0])
    end_hour = int(end_time.split(":")[0])
    lunch_start_hour = int(lunch_start.split(":")[0])
    lunch_end_hour = int(lunch_end.split(":")[0])
    
    for day in working_days:
        for hour in range(start_hour, end_hour):
            if lunch_start_hour <= hour < lunch_end_hour:
                continue
            slots.append((day, hour))
    
    logger.info(f"Generated {len(slots)} time slots")
    return slots


def get_available_rooms_for_subject(subject_type: str, rooms: List[Dict[str, Any]]) -> List[str]:
    """Filter rooms by subject type."""
    if subject_type == "theory":
        return [r["name"] for r in rooms if r["type"] == "classroom"]
    elif subject_type in ["practical", "lab"]:
        return [r["name"] for r in rooms if r["type"] == "lab"]
    elif subject_type == "theory+lab":
        return [r["name"] for r in rooms]
    return []


def create_variables_simple(
    model: cp_model.CpModel,
    subjects: List[Dict[str, Any]],
    rooms: List[Dict[str, Any]],
    batches: List[str],
    time_slots: List[Tuple[str, int]]
) -> Dict[str, Dict[str, Any]]:
    """Create CP-SAT variables - simplified version."""
    variables = {}
    
    for subject in subjects:
        subject_name = subject["name"]
        subject_type = subject["type"]
        hours_needed = subject["hours_per_week"]
        
        available_rooms = get_available_rooms_for_subject(subject_type, rooms)
        
        if not available_rooms:
            logger.warning(f"No available rooms for {subject_name}")
            continue
        
        # All subjects: class-wide (no batches)
        for day, hour in time_slots:
            for duration in [1, 2]:
                if hour + duration > max(h for _, h in time_slots) + 1:
                    continue
                for room in available_rooms:
                    var_name = f"x_{subject_name}_{room}_{day}_{hour}_{duration}"
                    var = model.NewBoolVar(var_name)
                    variables[var_name] = {
                        "var": var,
                        "subject": subject_name,
                        "subject_type": subject_type,
                        "room": room,
                        "day": day,
                        "hour": hour,
                        "duration": duration,
                        "hours_needed": hours_needed
                    }
    
    logger.info(f"Created {len(variables)} variables")
    return variables


def add_basic_constraints_simple(
    model: cp_model.CpModel,
    variables: Dict[str, Dict[str, Any]],
    rooms: List[Dict[str, Any]],
    subjects: List[Dict[str, Any]]
) -> None:
    """Add only essential constraints."""
    
    # 1. No room overlaps
    room_time_slots = {}
    for var_name, var_data in variables.items():
        key = (var_data["day"], var_data["hour"], var_data["room"])
        if key not in room_time_slots:
            room_time_slots[key] = []
        room_time_slots[key].append(var_data["var"])
    
    for slot_vars in room_time_slots.values():
        if len(slot_vars) > 1:
            model.Add(sum(slot_vars) <= 1)
    
    logger.info("Added no-overlap constraint")
    
    # 2. Room type matching
    room_types = {r["name"]: r["type"] for r in rooms}
    for var_name, var_data in variables.items():
        room_name = var_data["room"]
        room_type = room_types.get(room_name, "classroom")
        subject_type = var_data["subject_type"]
        
        if subject_type == "theory" and room_type == "lab":
            model.Add(var_data["var"] == 0)
        if subject_type in ["practical", "lab"] and room_type == "classroom":
            model.Add(var_data["var"] == 0)
    
    logger.info("Added room type constraint")
    
    # 3. Duration constraints
    for var_name, var_data in variables.items():
        subject_type = var_data["subject_type"]
        duration = var_data["duration"]
        
        if subject_type == "theory" and duration > 2:
            model.Add(var_data["var"] == 0)
        if subject_type in ["practical", "lab"] and duration > 2:
            model.Add(var_data["var"] == 0)
    
    logger.info("Added duration constraint")
    
    # 4. Subject hours constraint
    subject_hours = {s["name"]: s["hours_per_week"] for s in subjects}
    
    for subject_name, required_hours in subject_hours.items():
        # All subjects: sum all entries for this subject
        subject_vars = []
        for var_name, var_data in variables.items():
            if var_data["subject"] == subject_name:
                subject_vars.append((var_data["var"], var_data["duration"]))
        
        if subject_vars:
            total_hours = sum(var * duration for var, duration in subject_vars)
            model.Add(total_hours == required_hours)
    
    logger.info("Added subject hours constraint")


def solve_simple(
    week_config: Dict[str, Any],
    subjects: List[Dict[str, Any]],
    rooms: List[Dict[str, Any]],
    batches: List[str] = None
) -> Dict[str, Any]:
    """Simplified solver with minimal constraints."""
    
    if batches is None:
        batches = ["Batch A", "Batch B", "Batch C"]
    
    logger.info("=" * 70)
    logger.info("STARTING SIMPLIFIED SOLVER")
    logger.info("=" * 70)
    
    try:
        # Generate slots
        time_slots = generate_time_slots(week_config)
        
        # Create model and variables
        model = cp_model.CpModel()
        variables = create_variables_simple(model, subjects, rooms, batches, time_slots)
        
        # Add constraints
        logger.info("\nAdding constraints...")
        add_basic_constraints_simple(model, variables, rooms, subjects)
        
        # Solve
        logger.info("\nSolving...")
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 180.0  # Increased from 60 to 180 seconds
        solver.parameters.num_workers = 4
        solver.parameters.log_search_progress = True
        
        status = solver.Solve(model)
        
        logger.info(f"Solver status: {status}")
        logger.info(f"Solver statistics: {solver.ResponseStats()}")
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            logger.info("✅ SOLUTION FOUND!")
            
            # Extract solution
            timetable = []
            for var_name, var_data in variables.items():
                if solver.Value(var_data["var"]) == 1:
                    session_type = "theory" if var_data["subject_type"] == "theory" else "practical"
                    start_hour = var_data["hour"]
                    duration = var_data["duration"]
                    
                    timetable.append({
                        "subject": var_data["subject"],
                        "room": var_data["room"],
                        "day": var_data["day"],
                        "start_hour": start_hour,
                        "end_hour": start_hour + duration,
                        "duration": duration,
                        "type": session_type,
                        "start_time": f"{start_hour:02d}:00",
                        "end_time": f"{start_hour + duration:02d}:00"
                    })
            
            # Sort
            day_order = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
            timetable.sort(key=lambda x: (day_order.get(x["day"], 7), x["start_hour"]))
            
            logger.info(f"Generated {len(timetable)} slots")
            
            # Log scheduling summary
            total_hours_scheduled = sum(t["duration"] for t in timetable)
            logger.info(f"Total hours scheduled: {total_hours_scheduled}h")
            logger.info(f"Expected hours: {sum(s['hours_per_week'] for s in subjects)}h")
            logger.info("=" * 70)
            
            return {
                "status": "success",
                "timetable": timetable,
                "stats": {
                    "total_slots": len(timetable),
                    "subjects_scheduled": len(set(t["subject"] for t in timetable)),
                    "rooms_used": len(set(t["room"] for t in timetable))
                }
            }
        
        else:
            logger.warning("❌ NO FEASIBLE SOLUTION")
            return {
                "status": "failed",
                "reason": "No feasible solution found"
            }
    
    except Exception as e:
        logger.error(f"Solver error: {str(e)}", exc_info=True)
        return {
            "status": "failed",
            "reason": f"Solver error: {str(e)}"
        }
