# Quick Start Guide - Modular Timetable Solver

## ⚡ 5-Minute Setup

### 1. Start the Server
```bash
cd backend
python run_server.py
```
Server runs on `http://localhost:8000`

### 2. Test with Simple Example
```bash
python test_modular_solver.py
```

### 3. Call the API
```bash
curl -X POST http://localhost:8000/api/timetable/generate \
  -H "Content-Type: application/json" \
  -d '{
    "teachers": [
      {
        "id": "T1",
        "name": "Dr. Smith",
        "subjects": ["OS"],
        "availability": ["Mon_9", "Mon_10"]
      }
    ],
    "subjects": [
      {
        "id": "OS",
        "name": "Operating Systems",
        "type": "theory",
        "hours_per_week": 2
      }
    ],
    "rooms": [
      {
        "id": "C301",
        "name": "Classroom 301",
        "type": "classroom",
        "availability": ["Mon_9", "Mon_10"]
      }
    ],
    "batches": [
      {
        "id": "B1",
        "name": "TY CSE A",
        "subjects": ["OS"]
      }
    ],
    "timeslots": ["Mon_9", "Mon_10"]
  }'
```

---

## 📋 Input Format (Minimal Example)

```json
{
  "teachers": [
    {
      "id": "T1",
      "name": "Teacher Name",
      "subjects": ["SUBJECT_ID"],
      "availability": ["Mon_9", "Mon_10", "Tue_9"]
    }
  ],
  "subjects": [
    {
      "id": "SUBJECT_ID",
      "name": "Subject Name",
      "type": "theory",
      "hours_per_week": 2
    }
  ],
  "rooms": [
    {
      "id": "ROOM_ID",
      "name": "Room Name",
      "type": "classroom",
      "availability": ["Mon_9", "Mon_10", "Tue_9"]
    }
  ],
  "batches": [
    {
      "id": "BATCH_ID",
      "name": "Batch Name",
      "subjects": ["SUBJECT_ID"]
    }
  ],
  "timeslots": ["Mon_9", "Mon_10", "Tue_9"]
}
```

---

## 📤 Output Format

### Success Response
```json
{
  "status": "success",
  "message": "✅ Feasible timetable generated",
  "timetable": [
    {
      "subject": "Operating Systems",
      "teacher": "Dr. Smith",
      "room": "Classroom 301",
      "batch": "TY CSE A",
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

### Failure Response
```json
{
  "status": "failed",
  "reason": "infeasible",
  "message": "❌ No feasible solution found",
  "timetable": []
}
```

---

## 🔑 Key Concepts

### Subject Types
- **theory**: Classroom lectures (max 2 consecutive hours)
- **practical**: Lab sessions (exactly 2 consecutive hours)

### Room Types
- **classroom**: For theory classes
- **lab**: For practical classes

### Time Slots
Format: `"Day_Time"` (e.g., `"Mon_9"`, `"Tue_10"`)

### Break Time
Default: 12 PM - 1 PM (no classes scheduled)

---

## 🧪 Test Cases

Run all tests:
```bash
python test_modular_solver.py
```

Tests included:
1. ✅ Simple (1 subject, 2 hours)
2. ✅ Complex (3 subjects, 6 hours)
3. ✅ Theory + Practical mix
4. ❌ Infeasible (demonstrates graceful failure)

---

## 🐍 Python Usage

```python
from app.modular_solver import generate_timetable

result = generate_timetable(
    teachers=[
        {
            "id": "T1",
            "name": "Dr. Smith",
            "subjects": ["OS"],
            "availability": ["Mon_9", "Mon_10"]
        }
    ],
    subjects=[
        {
            "id": "OS",
            "name": "Operating Systems",
            "type": "theory",
            "hours_per_week": 2
        }
    ],
    rooms=[
        {
            "id": "C301",
            "name": "Classroom 301",
            "type": "classroom",
            "availability": ["Mon_9", "Mon_10"]
        }
    ],
    batches=[
        {
            "id": "B1",
            "name": "TY CSE A",
            "subjects": ["OS"]
        }
    ],
    timeslots=["Mon_9", "Mon_10"]
)

print(result)
```

---

## 🚨 Common Errors

### "No variables created"
**Cause**: No valid teacher-subject-room-batch combinations
**Fix**: Check that:
- Teachers have subjects assigned
- Subjects are in batches
- Room types match subject types

### "No feasible solution found"
**Cause**: Constraints cannot be satisfied
**Fix**: Check that:
- Total hours ≤ available slots
- Teacher/room availability overlaps
- Break times are correct

### "Solver timeout"
**Cause**: Problem too complex
**Fix**: 
- Reduce timeslots
- Increase `time_limit` parameter
- Simplify constraints

---

## 📚 Full Documentation

For complete details, see:
- **`REFACTORING_GUIDE.md`** - Full technical guide
- **`REFACTORING_SUMMARY.md`** - Architecture overview
- **`example_usage.py`** - Working examples

---

## 🎯 Next Steps

1. ✅ Run `python test_modular_solver.py`
2. ✅ Try the API with curl or Postman
3. ✅ Read `REFACTORING_GUIDE.md` for details
4. ✅ Integrate with your frontend

---

**Status**: ✅ Ready to use
**Version**: 2.0 (Refactored)
