"""
Relaxed Timetable Solver - One hour slots with simplified constraints
"""

from ortools.sat.python import cp_model
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)


def generate_time_slots(week_config: Dict[str, Any]) -> List[Tuple[str, int]]:
    """Generate all valid one-hour time slots excluding lunch period."""
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
    
    logger.info(f"Generated {len(slots)} one-hour time slots")
    return slots


def get_available_rooms_for_subject(subject_type: str, rooms: List[Dict[str, Any]]) -> List[str]:
    """Filter rooms by subject type."""
    if subject_type == "theory":
        return [r["name"] for r in rooms if r["type"] == "classroom"]
    elif subject_type in ["practical", "lab"]:
        return [r["name"] for r in rooms if r["type"] == "lab"]
    elif subject_type in ["both", "theory+lab", "theory_lab"]:
        return [r["name"] for r in rooms]
    return []


def solve_relaxed(
    week_config: Dict[str, Any],
    subjects: List[Dict[str, Any]],
    rooms: List[Dict[str, Any]],
    batches: List[str] = None
) -> Dict[str, Any]:
    """
    Relaxed solver with simplified constraints:
    - One hour slots only
    - No room overlaps (hard constraint)
    - Exact hours per subject (hard constraint)
    - Even spread throughout week (soft constraint)
    """
    
    if batches is None:
        batches = ["Batch A"]
    
    logger.info("=" * 70)
    logger.info("STARTING RELAXED SOLVER (One-Hour Slots)")
    logger.info("=" * 70)
    
    try:
        # Generate time slots
        time_slots = generate_time_slots(week_config)
        logger.info(f"Available slots: {len(time_slots)}")
        
        # Create model
        model = cp_model.CpModel()
        variables = {}
        
        # Create variables: (subject, room, day, hour)
        # Each variable represents a 1-hour slot assignment
        for subject in subjects:
            subject_name = subject["name"]
            subject_type = subject["type"]
            subject_teacher = subject.get("teacher", "")
            
            # Calculate hours needed - handle both old and new format
            if "hours_per_week" in subject:
                # New format from frontend
                hours_needed = subject.get("hours_per_week", 0)
            elif "theory_hours" in subject or "practical_hours" in subject:
                # Old format with separate theory/practical hours
                if subject_type == "theory":
                    hours_needed = subject.get("theory_hours", 0)
                elif subject_type == "practical":
                    hours_needed = subject.get("practical_hours", 0)
                else:  # both
                    hours_needed = subject.get("theory_hours", 0) + subject.get("practical_hours", 0)
            else:
                hours_needed = 0
            
            logger.info(f"Subject: {subject_name}, Type: {subject_type}, Hours: {hours_needed}")
            
            if hours_needed == 0:
                logger.warning(f"Subject {subject_name} has 0 hours, skipping")
                continue
            
            available_rooms = get_available_rooms_for_subject(subject_type, rooms)
            
            if not available_rooms:
                logger.warning(f"No available rooms for {subject_name} ({subject_type})")
                continue
            
            # Create variables for each possible slot
            for day, hour in time_slots:
                for room in available_rooms:
                    var_name = f"x_{subject_name}_{room}_{day}_{hour}"
                    var = model.NewBoolVar(var_name)
                    variables[var_name] = {
                        "var": var,
                        "subject": subject_name,
                        "subject_type": subject_type,
                        "room": room,
                        "day": day,
                        "hour": hour,
                        "hours_needed": hours_needed,
                        "teacher": subject_teacher
                    }
        
        logger.info(f"Created {len(variables)} variables")
        
        # CONSTRAINT 1: No room overlaps
        logger.info("Adding constraint: No room overlaps...")
        room_time_slots = {}
        for var_name, var_data in variables.items():
            key = (var_data["day"], var_data["hour"], var_data["room"])
            if key not in room_time_slots:
                room_time_slots[key] = []
            room_time_slots[key].append(var_data["var"])
        
        for slot_vars in room_time_slots.values():
            if len(slot_vars) > 1:
                model.Add(sum(slot_vars) <= 1)
        
        logger.info(f"Added {len(room_time_slots)} room-time constraints")
        
        # CONSTRAINT 2: Room type matching
        logger.info("Adding constraint: Room type matching...")
        room_types = {r["name"]: r["type"] for r in rooms}
        for var_name, var_data in variables.items():
            room_name = var_data["room"]
            room_type = room_types.get(room_name, "classroom")
            subject_type = var_data["subject_type"]
            
            # Theory subjects only in classrooms
            if subject_type == "theory" and room_type == "lab":
                model.Add(var_data["var"] == 0)
            # Practical subjects only in labs
            if subject_type == "practical" and room_type == "classroom":
                model.Add(var_data["var"] == 0)
        
        logger.info("Added room type constraints")
        
        # CONSTRAINT 2.5: Each subject only once per time slot
        logger.info("Adding constraint: Each subject only once per time slot...")
        subject_time_slots = {}
        for var_name, var_data in variables.items():
            key = (var_data["subject"], var_data["day"], var_data["hour"])
            if key not in subject_time_slots:
                subject_time_slots[key] = []
            subject_time_slots[key].append(var_data["var"])
        
        for slot_vars in subject_time_slots.values():
            if len(slot_vars) > 1:
                model.Add(sum(slot_vars) <= 1)
        
        logger.info(f"Added {len(subject_time_slots)} subject-time constraints")
        
        # CONSTRAINT 2.6: Only one class per time slot (no overlapping subjects)
        logger.info("Adding constraint: Only one class per time slot...")
        all_time_slots = {}
        for var_name, var_data in variables.items():
            key = (var_data["day"], var_data["hour"])
            if key not in all_time_slots:
                all_time_slots[key] = []
            all_time_slots[key].append(var_data["var"])
        
        for slot_vars in all_time_slots.values():
            if len(slot_vars) > 1:
                model.Add(sum(slot_vars) <= 1)
        
        logger.info(f"Added {len(all_time_slots)} time-slot constraints (no overlaps)")
        
        # CONSTRAINT 2.7: Spread classes across different days (avoid bunching)
        logger.info("Adding constraint: Spread classes across days...")
        for subject in subjects:
            subject_name = subject["name"]
            # Group by day
            days_used = {}
            for var_name, var_data in variables.items():
                if var_data["subject"] == subject_name:
                    day = var_data["day"]
                    if day not in days_used:
                        days_used[day] = []
                    days_used[day].append(var_data["var"])
            
            # Limit max classes per day per subject (max 2 per day)
            for day, day_vars in days_used.items():
                if len(day_vars) > 2:
                    model.Add(sum(day_vars) <= 2)
        
        logger.info("Added spread-across-days constraints")
        
        # CONSTRAINT 3: Exact hours per subject
        logger.info("Adding constraint: Exact hours per subject...")
        subject_hours = {}
        for subject in subjects:
            subject_name = subject["name"]
            subject_type = subject["type"]
            
            # Handle both old and new format
            if "hours_per_week" in subject:
                hours = subject.get("hours_per_week", 0)
            elif "theory_hours" in subject or "practical_hours" in subject:
                if subject_type == "theory":
                    hours = subject.get("theory_hours", 0)
                elif subject_type == "practical":
                    hours = subject.get("practical_hours", 0)
                else:  # both
                    hours = subject.get("theory_hours", 0) + subject.get("practical_hours", 0)
            else:
                hours = 0
            
            if hours > 0:
                subject_hours[subject_name] = hours
        
        for subject_name, required_hours in subject_hours.items():
            subject_vars = []
            for var_name, var_data in variables.items():
                if var_data["subject"] == subject_name:
                    subject_vars.append(var_data["var"])
            
            if subject_vars:
                # Each slot is 1 hour, so sum of variables = required hours
                logger.info(f"Adding constraint: {subject_name} must have exactly {required_hours} hours")
                model.Add(sum(subject_vars) == required_hours)
            else:
                logger.warning(f"No variables created for subject {subject_name}")
        
        logger.info(f"Added {len(subject_hours)} subject hour constraints")
        
        # Solve
        logger.info("\nSolving...")
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 180.0
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
                    start_hour = var_data["hour"]
                    end_hour = start_hour + 1
                    
                    start_time_str = f"{start_hour:02d}:00"
                    end_time_str = f"{end_hour:02d}:00"
                    
                    timetable.append({
                        "subject": var_data["subject"],
                        "room": var_data["room"],
                        "day": var_data["day"],
                        "start_hour": start_hour,
                        "end_hour": end_hour,
                        "duration": 1,
                        "type": var_data["subject_type"],
                        "start_time": start_time_str,
                        "end_time": end_time_str,
                        "slot": f"{start_time_str}-{end_time_str}",
                        "teacher": var_data.get("teacher", "")
                    })
            
            # Sort by day and time
            day_order = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
            timetable.sort(key=lambda x: (day_order.get(x["day"], 7), x["start_hour"]))
            
            logger.info(f"Generated {len(timetable)} one-hour slots")
            
            # Log scheduling summary
            total_hours_scheduled = sum(t["duration"] for t in timetable)
            logger.info(f"Total hours scheduled: {total_hours_scheduled}h")
            logger.info(f"Expected hours: {sum(subject_hours.values())}h")
            logger.info("=" * 70)
            
            return {
                "status": "success",
                "timetable": timetable,
                "stats": {
                    "total_slots": len(timetable),
                    "subjects_scheduled": len(set(t["subject"] for t in timetable)),
                    "rooms_used": len(set(t["room"] for t in timetable)),
                    "total_hours": total_hours_scheduled
                }
            }
        
        else:
            logger.warning("❌ NO FEASIBLE SOLUTION")
            return {
                "status": "failed",
                "reason": "No feasible solution found - check if total hours exceed available slots"
            }
    
    except Exception as e:
        logger.error(f"Solver error: {str(e)}", exc_info=True)
        return {
            "status": "failed",
            "reason": f"Solver error: {str(e)}"
        }
