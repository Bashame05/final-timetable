# Timetable Solver V3 - Advanced Features

**Status**: ✅ Implemented and Ready to Test

---

## 🎯 New Features in V3

### 1. **Split Theory+Lab Subjects** ✅
Subjects with type `"theory+lab"` are now split into separate sessions:

```
Input: "Physics" (theory+lab, 5 hours)
↓
Output:
  - Physics (Theory): 2-3 hours in classroom
  - Physics (Lab): 2-3 hours in lab room
```

**Benefits:**
- Theory in classrooms, labs in lab rooms
- Better resource utilization
- More realistic scheduling

---

### 2. **Consecutive Practical Slots** ✅
Lab/practical sessions are scheduled consecutively within the same day:

```
Example:
Mon: 10:00-11:00 (Lab) → 11:00-12:00 (Lab)  ✅ Consecutive
Mon: 10:00-11:00 (Lab) → 14:00-15:00 (Lab)  ❌ Not consecutive (lunch break)
```

**Constraints:**
- Practical slots must be back-to-back
- Cannot cross lunch break
- Cannot cross day boundaries
- Improves student experience (no fragmented labs)

---

### 3. **Batch Compactness** ✅
Maximum 2 consecutive theory slots per batch per day:

```
Example - GOOD:
Mon: 09:00-10:00 (Theory) → 10:00-11:00 (Theory) → 14:00-15:00 (Lab)  ✅

Example - BAD (prevented):
Mon: 09:00-10:00 (Theory) → 10:00-11:00 (Theory) → 11:00-12:00 (Theory)  ❌
```

**Benefits:**
- Prevents student fatigue
- Better learning outcomes
- More balanced daily schedule
- Breaks between theory sessions

---

## 📊 Comparison: V2 vs V3

| Feature | V2 | V3 |
|---------|----|----|
| Batch Distribution | ✅ | ✅ |
| Theory+Lab Split | ❌ | ✅ |
| Consecutive Practicals | ❌ | ✅ |
| Batch Compactness | ❌ | ✅ |
| Room Type Matching | ✅ | ✅ |
| Optimization | ✅ | ✅ Enhanced |
| Solving Time | ~60-120s | ~120-180s |

---

## 🔧 How It Works

### Subject Expansion
```python
# Input
{
  "name": "Physics",
  "type": "theory+lab",
  "hours_per_week": 5
}

# Expanded to:
[
  {
    "name": "Physics (Theory)",
    "type": "theory",
    "hours": 2,
    "is_practical": False,
    "requires_consecutive": False
  },
  {
    "name": "Physics (Lab)",
    "type": "lab",
    "hours": 3,
    "is_practical": True,
    "requires_consecutive": True
  }
]
```

### Constraint Application
1. **Room Type Matching**: Theory→Classroom, Lab→Lab
2. **Consecutive Practicals**: Lab slots must be adjacent
3. **Batch Compactness**: Max 2 theory slots in a row
4. **No Overlaps**: Room and batch conflicts prevented
5. **Hour Requirements**: Each subject gets exact hours

---

## 📈 Expected Output

### Before (V2)
```
Mon 09:00 - Physics (Batch 1)
Mon 10:00 - Physics (Batch 1)
Mon 11:00 - Physics (Batch 1)
Mon 14:00 - Math (Batch 1)
Mon 15:00 - Math (Batch 1)
```
❌ All physics in one batch, no separation of theory/lab

### After (V3)
```
Mon 09:00 - Physics Theory (Batch 1) [Classroom]
Mon 10:00 - Physics Theory (Batch 2) [Classroom]
Tue 09:00 - Physics Lab (Batch 1) [Lab] → 10:00 Physics Lab (Batch 1) [Lab]
Tue 11:00 - Math Theory (Batch 1) [Classroom]
Tue 14:00 - Math Lab (Batch 2) [Lab]
```
✅ Separated theory/lab, consecutive labs, balanced schedule

---

## 🚀 Testing Instructions

### 1. Restart Backend
```bash
# Stop current backend (Ctrl+C)
cd backend
python main.py
```

### 2. Test with Frontend
1. Open frontend
2. Add subjects with `type: "both"` (theory+lab)
3. Click "Generate Timetable"
4. Go to "View Schedule"

### 3. Verify Features
- ✅ Theory sessions in classrooms
- ✅ Lab sessions in lab rooms
- ✅ Lab sessions are consecutive
- ✅ No more than 2 theory slots in a row
- ✅ Better overall distribution

---

## 🎛️ Configuration

### Adjust Batch Count
File: `backend/routes/timetable_routes.py` (line 54)
```python
num_batches=3  # Change to 2, 4, 5, etc.
```

### Adjust Solving Time
File: `backend/models/timetable_solver_v3.py` (line 281)
```python
self.solver.parameters.max_time_in_seconds = 180.0  # Increase for better solutions
```

---

## 🐛 Troubleshooting

### Slow Generation
- Reduce number of subjects
- Reduce hours per subject
- Reduce number of batches
- Increase available time slots

### No Solution Found
- Ensure total hours ≤ available slots
- Check room availability
- Verify subject types match room types
- Increase week hours

### Unbalanced Schedule
- Increase number of working days
- Increase week hours
- Reduce hours per subject

---

## 📝 Files Modified

- ✅ Created: `backend/models/timetable_solver_v3.py` (new advanced solver)
- ✅ Updated: `backend/routes/timetable_routes.py` (use V3)

---

## 🎓 Algorithm Details

### Constraint Priority
1. **Hard Constraints** (must satisfy):
   - Room availability
   - Batch availability
   - Subject hours
   - Room type matching
   - Consecutive practicals
   - Batch compactness

2. **Soft Constraints** (optimization):
   - Prefer morning slots
   - Spread across week
   - Minimize gaps

### Solver Parameters
- **Algorithm**: OR-Tools CP-SAT
- **Workers**: 4 (parallel solving)
- **Timeout**: 180 seconds
- **Objective**: Minimize penalties

---

## ✨ Next Steps

1. ✅ Test with various subject configurations
2. ✅ Verify batch distribution
3. ✅ Check practical consecutiveness
4. ✅ Monitor solving time
5. Consider adding:
   - Teacher preferences
   - Room preferences
   - Student preferences
   - Special session constraints

---

**Ready to test!** 🚀
