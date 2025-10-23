# Modular Timetable Solver - Refactoring Guide

## Overview

The backend has been completely refactored to use a **modular, clean architecture** for the OR-Tools CP-SAT solver. This guide explains the new structure and how to use it.

---

## 🎯 Architecture

### New File: `app/modular_solver.py`

The solver is now split into **independent, testable functions**:

```
modular_solver.py
├── build_variables()                    # Create CP-SAT Boolean variables
├── add_no_overlap_constraints()         # Teacher, room, batch no-overlap
├── add_availability_constraints()       # Respect availability windows
├── add_break_constraints()              # Exclude break times
├── add_duration_constraints()           # Subject duration rules
│   ├── _add_consecutive_block_constraint()    # Practical: 2-hour block
│   └── _add_max_consecutive_constraint()      # Theory: max 2 hours
├── solve_timetable()                   # Configure and run solver
├── format_solution()                    # Convert to JSON
└── generate_timetable()                 # Main entry point
```

---

## 📋 Input Format

The `/api/timetable/generate` endpoint expects this structure:

```json
{
  "teachers": [
    {
      "id": "T1",
      "name": "Dr. Smith",
      "subjects": ["OS", "DBMS"],
      "availability": ["Mon_9", "Mon_10", "Tue_9", "Tue_10"]
    }
  ],
  "subjects": [
    {
      "id": "OS",
      "name": "Operating Systems",
      "type": "theory",
      "hours_per_week": 2
    },
    {
      "id": "Lab",
      "name": "Programming Lab",
      "type": "practical",
      "hours_per_week": 2
    }
  ],
  "rooms": [
    {
      "id": "C301",
      "name": "Classroom 301",
      "type": "classroom",
      "availability": ["Mon_9", "Mon_10", "Tue_9", "Tue_10"]
    },
    {
      "id": "Lab1",
      "name": "Computer Lab 1",
      "type": "lab",
      "availability": ["Mon_9", "Mon_10", "Tue_9", "Tue_10"]
    }
  ],
  "batches": [
    {
      "id": "B1",
      "name": "TY CSE A",
      "subjects": ["OS", "Lab"]
    }
  ],
  "timeslots": ["Mon_9", "Mon_10", "Tue_9", "Tue_10"],
  "break_start": "12",
  "break_end": "1",
  "time_limit": 60
}
```

### Key Fields

- **teachers**: List of teachers with their available time slots
- **subjects**: List of subjects with type (theory/practical) and required hours
- **rooms**: List of rooms with type (classroom/lab) and availability
- **batches**: List of batches (student groups) with their subject requirements
- **timeslots**: All available time slots (format: "Day_Time", e.g., "Mon_9")
- **break_start/end**: Break time hours (e.g., 12 PM - 1 PM)
- **time_limit**: Solver timeout in seconds (default: 60)

---

## 📤 Output Format

```json
{
  "status": "success",
  "message": "✅ Feasible timetable generated",
  "timetable": [
    {
      "subject": "Operating Systems",
      "subject_id": "OS",
      "teacher": "Dr. Smith",
      "teacher_id": "T1",
      "room": "Classroom 301",
      "room_id": "C301",
      "batch": "TY CSE A",
      "batch_id": "B1",
      "day": "Mon",
      "time": "9",
      "slot": "Mon_9",
      "duration": 2,
      "type": "theory"
    }
  ],
  "total_assignments": 1
}
```

### Error Response

```json
{
  "status": "failed",
  "reason": "infeasible",
  "message": "❌ No feasible solution found. The constraints cannot be satisfied with the given data.",
  "timetable": []
}
```

---

## 🔧 Constraints Implemented (HARD ONLY)

All constraints are **hard constraints** (must be satisfied):

### 1. **No Overlap Constraints**
- ✅ No teacher teaches two classes at the same time
- ✅ No room hosts two classes at the same time
- ✅ No batch attends two classes at the same time

### 2. **Availability Constraints**
- ✅ Teachers only assigned during their available slots
- ✅ Rooms only assigned during their available slots

### 3. **Break Time Constraints**
- ✅ No classes scheduled during break time (e.g., 12 PM - 1 PM)

### 4. **Duration Constraints**
- ✅ **Theory**: Max 2 consecutive hours per session
- ✅ **Practical**: Exactly 2 consecutive hours in one block
- ✅ Each subject-batch must be scheduled for required hours

### 5. **Room Type Constraints**
- ✅ Theory classes only in classrooms
- ✅ Practical classes only in labs

---

## 🚀 How to Use

### 1. Start the Server

```bash
cd backend
python run_server.py
```

Server runs on `http://localhost:8000`

### 2. Call the Endpoint

```bash
curl -X POST http://localhost:8000/api/timetable/generate \
  -H "Content-Type: application/json" \
  -d @payload.json
```

Or use Python:

```python
import requests

payload = {
    "teachers": [...],
    "subjects": [...],
    "rooms": [...],
    "batches": [...],
    "timeslots": [...]
}

response = requests.post(
    "http://localhost:8000/api/timetable/generate",
    json=payload
)

result = response.json()
print(result)
```

### 3. Run Tests

```bash
python test_modular_solver.py
```

This runs 4 test cases:
- ✅ Simple case (1 subject, 2 hours)
- ✅ Complex feasible case (3 subjects, 6 hours)
- ✅ Theory + Practical mix
- ❌ Infeasible case (demonstrates graceful failure)

---

## 📊 Function Reference

### `build_variables(model, teachers, subjects, batches, rooms, timeslots)`

Creates Boolean variables for the CP-SAT model.

**Returns**: Dictionary of variables with metadata

```python
variables = {
    "x_T1_OS_B1_C301_Mon_9": {
        "var": BoolVar,
        "teacher_id": "T1",
        "subject_id": "OS",
        "batch_id": "B1",
        "room_id": "C301",
        "slot": "Mon_9",
        "subject_type": "theory",
        "duration": 2
    }
}
```

---

### `add_no_overlap_constraints(model, variables, teachers, rooms, batches, timeslots)`

Adds constraints to prevent resource conflicts.

---

### `add_availability_constraints(model, variables, teachers, rooms)`

Ensures resources are only used during available times.

---

### `add_break_constraints(model, variables, timeslots, break_start, break_end)`

Prevents scheduling during break times.

---

### `add_duration_constraints(model, variables, subjects, batches, timeslots)`

Enforces subject-specific duration requirements:
- Theory: ≤ 2 consecutive hours
- Practical: = 2 consecutive hours (one block)

---

### `solve_timetable(model, variables, time_limit=60)`

Configures and runs the CP-SAT solver.

**Returns**: `(success: bool, solution: dict)`

---

### `format_solution(solution, teachers, subjects, rooms, batches)`

Converts solver output to JSON-friendly format.

**Returns**: List of scheduled lectures

---

### `generate_timetable(teachers, subjects, rooms, batches, timeslots, ...)`

**Main entry point** - orchestrates the entire solving process.

**Returns**: Dictionary with status, message, and timetable

---

## 🧪 Testing

### Test Cases Included

1. **Simple Case**: 1 subject, 2 hours, 1 teacher, 1 room
   - Expected: ✅ SUCCESS

2. **Complex Feasible**: 3 subjects, 6 hours, 3 teachers, 2 rooms
   - Expected: ✅ SUCCESS

3. **Theory + Practical Mix**: 2 subjects (1 theory + 1 practical)
   - Expected: ✅ SUCCESS

4. **Infeasible Case**: 8 hours required, 4 slots available
   - Expected: ❌ INFEASIBLE (graceful failure)

### Running Tests

```bash
python test_modular_solver.py
```

Output shows:
- ✅ Feasible timetable generated
- ❌ No feasible solution found (with reason)

---

## 🎯 Key Improvements

### Before (Old Code)
- ❌ Monolithic 675-line `main.py`
- ❌ Mixed concerns (routing, validation, solving)
- ❌ Hard to test individual constraints
- ❌ Difficult to debug infeasibility

### After (New Code)
- ✅ Modular 400-line `modular_solver.py`
- ✅ Separated concerns (each function has one job)
- ✅ Easy to test each constraint independently
- ✅ Clear error messages for debugging
- ✅ Reusable functions for other projects

---

## 🔍 Debugging Tips

### Problem: "No variables created"
- Check that teachers have subjects assigned
- Check that subjects are in batches
- Check that room types match subject types (theory→classroom, practical→lab)
- Check that teacher/room availability overlaps with timeslots

### Problem: "No feasible solution found"
- Verify total required hours ≤ available slots
- Check for conflicting availability windows
- Ensure break times are correctly specified
- Increase `time_limit` for complex problems

### Problem: Solver is slow
- Reduce the number of timeslots
- Increase `time_limit` parameter
- Simplify constraints (fewer subjects/batches)

---

## 📝 Example: Adding a New Constraint

To add a new constraint (e.g., "no more than 3 classes per day per teacher"):

```python
def add_teacher_daily_limit_constraint(
    model: cp_model.CpModel,
    variables: Dict[str, Any],
    teachers: List[Dict],
    timeslots: List[str],
    max_per_day: int = 3
) -> None:
    """Limit classes per teacher per day"""
    
    # Group timeslots by day
    days = set()
    for slot in timeslots:
        day, _ = slot.split("_")
        days.add(day)
    
    for teacher in teachers:
        teacher_id = teacher["id"]
        for day in days:
            day_slots = [s for s in timeslots if s.startswith(f"{day}_")]
            
            day_vars = [
                var_data["var"]
                for var_name, var_data in variables.items()
                if var_data["teacher_id"] == teacher_id and var_data["slot"] in day_slots
            ]
            
            if day_vars:
                model.Add(sum(day_vars) <= max_per_day)
```

Then call it in `generate_timetable()`:

```python
add_teacher_daily_limit_constraint(model, variables, teachers, filtered_slots)
```

---

## 📚 References

- [OR-Tools CP-SAT Documentation](https://developers.google.com/optimization/cp/cp_solver)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

---

## 🤝 Contributing

To extend the solver:

1. Add new constraint function in `modular_solver.py`
2. Call it from `generate_timetable()`
3. Add test case in `test_modular_solver.py`
4. Update this guide

---

**Last Updated**: October 2025
**Version**: 2.0 (Refactored)
