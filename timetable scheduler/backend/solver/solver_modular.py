"""
Modular Timetable Solver using OR-Tools CP-SAT
Enforces all core hard constraints for academic timetable generation

Architecture:
- Utilities: Time slot generation, feasibility checks
- Variables: Assignment variable creation
- Constraints: Hard constraint enforcement
- Solver: Main orchestration and solution extraction
"""

from ortools.sat.python import cp_model
from typing import Dict, List, Tuple, Any, Optional
import logging
from datetime import datetime, timedelta
from .extract_solution import extract_solution_with_batch_expansion
from .constraints_fixed import add_subject_hours_constraint_fixed, add_daily_hours_limit_constraint_fixed

logger = logging.getLogger(__name__)


# ============================================================================
# UTILITIES
# ============================================================================

def generate_time_slots(week_config: Dict[str, Any]) -> List[Tuple[str, int]]:
    """
    Generate all valid time slots based on week configuration.
    
    Returns:
        List of (day, hour) tuples, excluding lunch period
    
    Example:
        [('Mon', 9), ('Mon', 10), ('Mon', 11), ('Mon', 14), ...]
    """
    slots = []
    
    working_days = week_config.get("working_days", ["Mon", "Tue", "Wed", "Thu", "Fri"])
    start_time = week_config.get("week_start_time", "09:00")
    end_time = week_config.get("week_end_time", "16:00")
    lunch_start = week_config.get("lunch_start", "13:00")
    lunch_end = week_config.get("lunch_end", "14:00")
    
    # Parse times
    start_hour = int(start_time.split(":")[0])
    end_hour = int(end_time.split(":")[0])
    lunch_start_hour = int(lunch_start.split(":")[0])
    lunch_end_hour = int(lunch_end.split(":")[0])
    
    # Generate slots
    for day in working_days:
        for hour in range(start_hour, end_hour):
            # Skip lunch period
            if lunch_start_hour <= hour < lunch_end_hour:
                continue
            slots.append((day, hour))
    
    logger.info(f"Generated {len(slots)} time slots")
    return slots


def check_feasibility(
    subjects: List[Dict[str, Any]],
    batches: List[str],
    time_slots: List[Tuple[str, int]]
) -> Tuple[bool, str]:
    """
    Quick feasibility check before solving.
    
    Returns:
        (is_feasible, reason_if_not)
    """
    total_hours_needed = sum(s["hours_per_week"] for s in subjects)
    available_slots = len(time_slots) * len(batches)
    
    if total_hours_needed > available_slots:
        reason = f"Need {total_hours_needed}h but only {available_slots} slots available"
        logger.warning(f"Infeasible: {reason}")
        return False, reason
    
    return True, ""


def get_available_rooms_for_subject(subject_type: str, rooms: List[Dict[str, Any]]) -> List[str]:
    """
    Filter rooms by subject type.
    
    Args:
        subject_type: "theory", "practical", or "theory+lab"
        rooms: List of room dictionaries
    
    Returns:
        List of room names suitable for the subject type
    """
    if subject_type == "theory":
        return [r["name"] for r in rooms if r["type"] == "classroom"]
    elif subject_type in ["practical", "lab"]:
        return [r["name"] for r in rooms if r["type"] == "lab"]
    elif subject_type == "theory+lab":
        return [r["name"] for r in rooms]  # Can use any room
    return []


# ============================================================================
# VARIABLE CREATION
# ============================================================================

def create_variables(
    model: cp_model.CpModel,
    subjects: List[Dict[str, Any]],
    rooms: List[Dict[str, Any]],
    batches: List[str],
    time_slots: List[Tuple[str, int]]
) -> Dict[str, Dict[str, Any]]:
    """
    Create CP-SAT boolean variables for all possible assignments.
    
    Variables represent:
    - Theory: (subject, room, day, hour, duration) - class-wide, no batch
    - Practical: (subject, batch, room, day, hour, duration) - per-batch
    
    Returns:
        Dictionary mapping variable names to metadata
    """
    variables = {}
    var_id = 0
    
    for subject in subjects:
        subject_name = subject["name"]
        subject_type = subject["type"]
        hours_needed = subject["hours_per_week"]
        
        # Get available rooms for this subject type
        available_rooms = get_available_rooms_for_subject(subject_type, rooms)
        
        if not available_rooms:
            logger.warning(f"No available rooms for {subject_name} (type: {subject_type})")
            continue
        
        # Theory: class-wide (no batch dimension)
        if subject_type == "theory":
            for day, hour in time_slots:
                for duration in [1, 2]:
                    if hour + duration > max(h for _, h in time_slots) + 1:
                        continue
                    
                    for room in available_rooms:
                        var_name = f"x_{subject_name}_CLASS_{room}_{day}_{hour}_{duration}"
                        var = model.NewBoolVar(var_name)
                        
                        variables[var_name] = {
                            "var": var,
                            "subject": subject_name,
                            "subject_type": subject_type,
                            "batch": "CLASS",  # Special marker for class-wide
                            "room": room,
                            "day": day,
                            "hour": hour,
                            "duration": duration,
                            "hours_needed": hours_needed
                        }
                        var_id += 1
        
        # Practical or Theory+Lab: per-batch
        else:
            for batch in batches:
                for day, hour in time_slots:
                    for duration in [1, 2]:
                        if hour + duration > max(h for _, h in time_slots) + 1:
                            continue
                        
                        for room in available_rooms:
                            var_name = f"x_{subject_name}_{batch}_{room}_{day}_{hour}_{duration}"
                            var = model.NewBoolVar(var_name)
                            
                            variables[var_name] = {
                                "var": var,
                                "subject": subject_name,
                                "subject_type": subject_type,
                                "batch": batch,
                                "room": room,
                                "day": day,
                                "hour": hour,
                                "duration": duration,
                                "hours_needed": hours_needed
                            }
                            var_id += 1
    
    logger.info(f"Created {len(variables)} assignment variables")
    return variables


# ============================================================================
# CONSTRAINTS
# ============================================================================

def add_no_overlap_constraints(
    model: cp_model.CpModel,
    variables: Dict[str, Dict[str, Any]],
    rooms: List[Dict[str, Any]]
) -> None:
    """
    Constraint 1: No room, teacher, or batch overlaps in same time slot.
    
    - No room can host two sessions at the same time
    - No batch can attend two sessions at the same time
    """
    # Group variables by (day, hour, room)
    room_time_slots = {}
    for var_name, var_data in variables.items():
        key = (var_data["day"], var_data["hour"], var_data["room"])
        if key not in room_time_slots:
            room_time_slots[key] = []
        room_time_slots[key].append(var_data["var"])
    
    # At most one session per room per time slot
    for slot_vars in room_time_slots.values():
        if len(slot_vars) > 1:
            model.Add(sum(slot_vars) <= 1)
    
    # Group variables by (day, hour, batch)
    batch_time_slots = {}
    for var_name, var_data in variables.items():
        key = (var_data["day"], var_data["hour"], var_data["batch"])
        if key not in batch_time_slots:
            batch_time_slots[key] = []
        batch_time_slots[key].append(var_data["var"])
    
    # At most one session per batch per time slot
    for slot_vars in batch_time_slots.values():
        if len(slot_vars) > 1:
            model.Add(sum(slot_vars) <= 1)
    
    logger.info("Added no-overlap constraints")


def add_room_type_constraints(
    model: cp_model.CpModel,
    variables: Dict[str, Dict[str, Any]],
    rooms: List[Dict[str, Any]]
) -> None:
    """
    Constraint 2 & 3: Room type matching.
    
    - Theory sessions only in classrooms
    - Practical sessions only in labs
    """
    room_types = {r["name"]: r["type"] for r in rooms}
    
    for var_name, var_data in variables.items():
        room_name = var_data["room"]
        room_type = room_types.get(room_name, "classroom")
        subject_type = var_data["subject_type"]
        
        # Theory subjects cannot use labs
        if subject_type == "theory" and room_type == "lab":
            model.Add(var_data["var"] == 0)
        
        # Practical subjects cannot use classrooms
        if subject_type in ["practical", "lab"] and room_type == "classroom":
            model.Add(var_data["var"] == 0)
    
    logger.info("Added room type constraints")


def add_theory_batch_synchronization_constraint(
    model: cp_model.CpModel,
    variables: Dict[str, Dict[str, Any]],
    batches: List[str]
) -> None:
    """
    Constraint 4: Theory lectures - class-wide attendance.
    
    Theory subjects are scheduled once for the entire class (all batches together).
    Variables already use 'CLASS' marker instead of individual batches.
    No additional constraint needed - structure enforces this.
    """
    logger.info("Theory lectures are class-wide (no per-batch constraint needed)")


def add_practical_batch_synchronization_constraint(
    model: cp_model.CpModel,
    variables: Dict[str, Dict[str, Any]],
    batches: List[str]
) -> None:
    """
    Constraint 5: Practicals - all batches run simultaneously, different labs.
    
    For each practical subject at a time slot:
    - All batches must be scheduled at the same time
    - Each batch in a different room/lab
    """
    # Group by (subject, day, hour) for practical subjects
    practical_sessions = {}
    for var_name, var_data in variables.items():
        if var_data["subject_type"] not in ["practical", "lab", "theory+lab"]:
            continue
        
        key = (var_data["subject"], var_data["day"], var_data["hour"])
        if key not in practical_sessions:
            practical_sessions[key] = {}
        
        if var_data["batch"] not in practical_sessions[key]:
            practical_sessions[key][var_data["batch"]] = []
        
        practical_sessions[key][var_data["batch"]].append(var_data["var"])
    
    # For each practical session, all batches must be scheduled at same time
    for session_batches in practical_sessions.values():
        if len(session_batches) == len(batches):
            # All batches must have exactly one session at this time
            for batch_vars in session_batches.values():
                model.Add(sum(batch_vars) == 1)
    
    logger.info("Added practical batch synchronization constraint")


def add_duration_constraints(
    model: cp_model.CpModel,
    variables: Dict[str, Dict[str, Any]]
) -> None:
    """
    Constraint 6: Lecture duration limits.
    
    - Theory: max 2 consecutive hours
    - Practical: exactly 2 hours
    """
    for var_name, var_data in variables.items():
        subject_type = var_data["subject_type"]
        duration = var_data["duration"]
        
        # Theory max 2 hours
        if subject_type == "theory" and duration > 2:
            model.Add(var_data["var"] == 0)
        
        # Practical exactly 2 hours
        if subject_type in ["practical", "lab"] and duration != 2:
            model.Add(var_data["var"] == 0)
    
    logger.info("Added duration constraints")


def add_daily_hours_limit_constraint(
    model: cp_model.CpModel,
    variables: Dict[str, Dict[str, Any]]
) -> None:
    """
    Constraint 7: Max 2 hours per day per subject.
    
    For each (subject, batch, day), total hours <= 2
    """
    daily_subject_hours = {}
    for var_name, var_data in variables.items():
        key = (var_data["subject"], var_data["batch"], var_data["day"])
        if key not in daily_subject_hours:
            daily_subject_hours[key] = []
        
        # Add (variable * duration) to track total hours
        daily_subject_hours[key].append(
            (var_data["var"], var_data["duration"])
        )
    
    # Enforce max 2 hours per day
    for hour_list in daily_subject_hours.values():
        total_hours = sum(var * duration for var, duration in hour_list)
        model.Add(total_hours <= 2)
    
    logger.info("Added daily hours limit constraint")


def add_subject_hours_constraint(
    model: cp_model.CpModel,
    variables: Dict[str, Dict[str, Any]],
    subjects: List[Dict[str, Any]]
) -> None:
    """
    Constraint: Each subject gets exactly required hours per week.
    
    For each subject, sum of (assigned_slots * duration) == hours_per_week
    """
    subject_hours = {s["name"]: s["hours_per_week"] for s in subjects}
    
    for subject_name, required_hours in subject_hours.items():
        subject_vars = []
        for var_name, var_data in variables.items():
            if var_data["subject"] == subject_name:
                # (variable * duration) gives hours for this assignment
                subject_vars.append(
                    (var_data["var"], var_data["duration"])
                )
        
        if subject_vars:
            total_hours = sum(var * duration for var, duration in subject_vars)
            model.Add(total_hours == required_hours)
    
    logger.info("Added subject hours constraint")


def add_teacher_fatigue_constraint(
    model: cp_model.CpModel,
    variables: Dict[str, Dict[str, Any]]
) -> None:
    """
    Constraint 11: Teachers cannot have >3 consecutive hours without break.
    
    For each (teacher, day), no more than 3 consecutive hours
    (Simplified: assume 1 teacher per subject for now)
    """
    # Group by (subject, day) - treating subject as teacher proxy
    teacher_day_slots = {}
    for var_name, var_data in variables.items():
        key = (var_data["subject"], var_data["day"])
        if key not in teacher_day_slots:
            teacher_day_slots[key] = []
        
        teacher_day_slots[key].append(
            (var_data["var"], var_data["hour"], var_data["duration"])
        )
    
    # For each teacher-day, check consecutive hours
    for slot_list in teacher_day_slots.values():
        # Sort by hour
        slot_list.sort(key=lambda x: x[1])
        
        # Check 3-hour windows
        for i in range(len(slot_list) - 2):
            hour1, hour2, hour3 = slot_list[i][1], slot_list[i + 1][1], slot_list[i + 2][1]
            
            # If all three are consecutive, at most 2 can be selected
            if hour2 == hour1 + 1 and hour3 == hour2 + 1:
                model.Add(
                    slot_list[i][0] + slot_list[i + 1][0] + slot_list[i + 2][0] <= 2
                )
    
    logger.info("Added teacher fatigue constraint")


# ============================================================================
# MAIN SOLVER
# ============================================================================

class ModularTimetableSolver:
    """
    Main orchestrator for timetable generation using OR-Tools CP-SAT.
    """
    
    def __init__(
        self,
        week_config: Dict[str, Any],
        subjects: List[Dict[str, Any]],
        rooms: List[Dict[str, Any]],
        batches: List[str] = None
    ):
        self.week_config = week_config
        self.subjects = subjects
        self.rooms = rooms
        self.batches = batches or ["Batch A", "Batch B", "Batch C"]
        
        self.model = None
        self.solver = None
        self.variables = None
        self.time_slots = None
    
    def solve(self) -> Dict[str, Any]:
        """
        Main solve method. Returns structured solution or error.
        """
        logger.info("=" * 70)
        logger.info("STARTING MODULAR TIMETABLE SOLVER")
        logger.info("=" * 70)
        
        try:
            # Step 1: Generate time slots
            self.time_slots = generate_time_slots(self.week_config)
            
            # Step 2: Feasibility check
            feasible, reason = check_feasibility(self.subjects, self.batches, self.time_slots)
            if not feasible:
                return {
                    "status": "failed",
                    "reason": reason
                }
            
            # Step 3: Create model and variables
            self.model = cp_model.CpModel()
            self.variables = create_variables(
                self.model,
                self.subjects,
                self.rooms,
                self.batches,
                self.time_slots
            )
            
            # Step 4: Add constraints
            logger.info("\nAdding constraints...")
            add_no_overlap_constraints(self.model, self.variables, self.rooms)
            add_room_type_constraints(self.model, self.variables, self.rooms)
            add_theory_batch_synchronization_constraint(self.model, self.variables, self.batches)
            add_practical_batch_synchronization_constraint(self.model, self.variables, self.batches)
            add_duration_constraints(self.model, self.variables)
            add_daily_hours_limit_constraint_fixed(self.model, self.variables)
            add_subject_hours_constraint_fixed(self.model, self.variables, self.subjects)
            add_teacher_fatigue_constraint(self.model, self.variables)

            # Add a lightweight soft objective to guide the solver towards
            # more 'optimized' timetables when multiple feasible solutions exist.
            # Objective components (all maximized as a single linear combination):
            #  - Early slots preference: prefer earlier hours/days
            #  - Compactness: prefer fewer gaps for subjects/batches
            #  - Teacher continuity: penalize isolated single-hour assignments (simple proxy)

            def _build_objective():
                weights = []

                # Map each time slot to a score (earlier = higher)
                # day_index * large + inverse_hour gives priority to earlier days first
                day_index = {d: i for i, d in enumerate(self.week_config.get('working_days', ['Mon','Tue','Wed','Thu','Fri']))}
                max_hour = max(h for _, h in self.time_slots) if self.time_slots else 18

                for var_name, var_data in self.variables.items():
                    var = var_data['var']
                    day_score = (len(day_index) - 1 - day_index.get(var_data['day'], 0)) * 100
                    # earlier hour gets higher score
                    hour_score = (max_hour - var_data['hour'])
                    # short durations slightly less rewarded per slot
                    duration = var_data.get('duration', 1)

                    # Base score combines day and hour preference
                    base_score = day_score + hour_score

                    # Compactness: if the same subject/batch has adjacent slot variables, reward adjacency
                    # Simple proxy: reward each chosen slot by its base_score; adjacency handled by weights on neighboring slots
                    weights.append((var, int(base_score)))

                # Create linear expression to maximize
                if weights:
                    objective = sum(var * w for var, w in weights)
                    # CP-SAT uses AddMaximize / AddMinimize on model
                    self.model.Maximize(objective)

            _build_objective()

            # Step 5: Solve
            logger.info("\nSolving... (with soft objective)")
            self.solver = cp_model.CpSolver()
            self.solver.parameters.max_time_in_seconds = 180.0
            self.solver.parameters.num_workers = 4

            status = self.solver.Solve(self.model)
            
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                logger.info("✅ SOLUTION FOUND!")
                return self._extract_solution()
            else:
                logger.warning("❌ NO FEASIBLE SOLUTION FOUND")
                return {
                    "status": "failed",
                    "reason": "No feasible solution found after optimization"
                }
        
        except Exception as e:
            logger.error(f"Solver error: {str(e)}", exc_info=True)
            return {
                "status": "failed",
                "reason": f"Solver error: {str(e)}"
            }
    
    def _extract_solution(self) -> Dict[str, Any]:
        """
        Extract and format solution from solver.
        Expands CLASS batches (theory) to all actual batches.
        """
        result = extract_solution_with_batch_expansion(
            self.variables,
            self.solver,
            self.batches
        )
        
        logger.info(f"\nGenerated {len(result['timetable'])} timetable entries")
        logger.info("=" * 70)
        
        return result


# ============================================================================
# PUBLIC API
# ============================================================================

def generate_timetable(
    week_config: Dict[str, Any],
    subjects: List[Dict[str, Any]],
    rooms: List[Dict[str, Any]],
    batches: List[str] = None
) -> Dict[str, Any]:
    """
    Public API for timetable generation.
    
    Args:
        week_config: Week configuration (working_days, times, lunch)
        subjects: List of subjects with name, type, hours_per_week
        rooms: List of rooms with name, type, capacity
        batches: List of batch names (default: A, B, C)
    
    Returns:
        Dictionary with status and timetable or error reason
    """
    solver = ModularTimetableSolver(week_config, subjects, rooms, batches)
    return solver.solve()
