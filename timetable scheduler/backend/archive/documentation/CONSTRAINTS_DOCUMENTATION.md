# Hard Constraints Implementation

This document outlines all the hard constraints that are enforced by the OR-Tools CP-SAT solver in the `/api/timetable/generate` route.

## ✅ Implemented Hard Constraints

### 1. **No Teacher Overlap**
- **Constraint**: A teacher cannot teach two batches at the same time
- **Implementation**: For each teacher and each time slot, at most one assignment can be active
- **CP-SAT Code**: `model.Add(sum(teacher_slot_vars) <= 1)`

### 2. **No Room/Lab Overlap**
- **Constraint**: A room cannot host two lectures at the same time
- **Implementation**: For each room and each time slot, at most one assignment can be active
- **CP-SAT Code**: `model.Add(sum(room_slot_vars) <= 1)`

### 3. **No Batch Overlap**
- **Constraint**: A batch can only attend one lecture at a time
- **Implementation**: For each batch and each time slot, at most one assignment can be active
- **CP-SAT Code**: `model.Add(sum(batch_slot_vars) <= 1)`

### 4. **Break Time Enforcement**
- **Constraint**: No classes scheduled between 12 PM – 1 PM
- **Implementation**: Any assignment that includes break time slots is invalidated
- **CP-SAT Code**: `model.Add(var_data["var"] == 0)` for break time assignments

### 5. **Theory Lectures Constraints**
- **Room Type**: Theory lectures must be conducted only in classrooms
- **Duration**: Theory lectures duration ≤ 2 consecutive hours
- **Implementation**: 
  - Room type validation: `if room.get("type") != "classroom": model.Add(var_data["var"] == 0)`
  - Duration validation: `if var_data["duration"] > 2: model.Add(var_data["var"] == 0)`

### 6. **Practical Lectures Constraints**
- **Room Type**: Practical lectures must be conducted only in labs
- **Duration**: Practical lectures duration = exactly 2 consecutive hours
- **Implementation**:
  - Room type validation: `if room.get("type") != "lab": model.Add(var_data["var"] == 0)`
  - Duration validation: `if var_data["duration"] != 2: model.Add(var_data["var"] == 0)`

### 7. **Major Project Constraints**
- **Duration**: Major project duration ≥ 2 hours
- **Room Type**: Can be conducted in any classroom/lab
- **Implementation**: `if var_data["duration"] < 2: model.Add(var_data["var"] == 0)`

### 8. **Mini Project Constraints**
- **Duration**: Mini project duration ≤ 2 hours
- **Room Type**: Can be conducted in any classroom/lab
- **Implementation**: `if var_data["duration"] > 2: model.Add(var_data["var"] == 0)`

### 9. **Subject-Batch Assignment**
- **Constraint**: Each subject-batch combination must be scheduled exactly once
- **Implementation**: For each subject-batch pair, exactly one assignment must be active
- **CP-SAT Code**: `model.Add(sum(subject_batch_vars) == 1)`

## 🔧 Technical Implementation Details

### Variable Creation
- **Variables**: `x[subject_id][batch_id][teacher_id][start_slot][room_id]`
- **Type**: Boolean variables (0 or 1)
- **Meaning**: 1 if the assignment is active, 0 otherwise

### Consecutive Slot Handling
- **Function**: `_get_consecutive_slots_from_available()`
- **Purpose**: Ensures multi-hour lectures are scheduled in consecutive time slots
- **Validation**: Checks that all consecutive slots are available for both teacher and room

### Constraint Enforcement
- **Method**: Uses `model.Add()` to add constraints to the CP-SAT model
- **Validation**: Invalid assignments are set to 0 using `model.Add(var_data["var"] == 0)`

## 📊 Test Data Structure

### Teachers (5 teachers)
- **T1**: Dr. Smith - OS, DBMS (Morning slots)
- **T2**: Dr. Brown - Lab, OS_Lab (Morning slots)
- **T3**: Prof. Johnson - ML, AI (Afternoon slots)
- **T4**: Dr. Wilson - Major_Project, Mini_Project (Afternoon slots)
- **T5**: Dr. Davis - CN, SE (Morning slots)

### Subjects (10 subjects)
- **Theory**: OS (2h), DBMS (2h), ML (2h), AI (1h), CN (2h), SE (1h)
- **Practical**: Lab (2h), OS_Lab (2h)
- **Major Project**: Major_Project (3h)
- **Mini Project**: Mini_Project (2h)

### Rooms (4 rooms)
- **Classrooms**: C301, C302
- **Labs**: Lab1, Lab2

### Time Slots
- **Days**: Mon, Tue, Wed, Thu, Fri
- **Times**: 9, 10, 11, 12, 1, 2, 3
- **Break Time**: 12 PM - 1 PM (automatically excluded)

## 🎯 Expected Behavior

### Successful Scheduling
- All 10 subjects should be scheduled for the batch
- No constraint violations
- Proper room type assignments (theory → classroom, practical → lab)
- Consecutive hour scheduling for multi-hour subjects
- No scheduling during break time

### Constraint Validation
- Teacher availability respected
- Room availability respected
- Duration constraints enforced
- Room type constraints enforced
- Break time constraints enforced

## 🚀 Usage

### Test the Implementation
```bash
# Start the server
python run_server.py

# Test with expanded data
python test_generate_route.py

# Test with curl
curl -X POST "http://localhost:8000/api/timetable/generate" \
     -H "Content-Type: application/json" \
     -d @example_generate_request.json
```

### Expected Output
```json
{
  "status": "success",
  "timetable": [
    {
      "subject": "Operating Systems",
      "teacher": "Dr. Smith",
      "room": "Classroom 301",
      "batch": "TY CSE A",
      "start_slot": "Mon_9",
      "end_slot": "Mon_10",
      "duration": 2,
      "type": "theory",
      "all_slots": ["Mon_9", "Mon_10"]
    }
    // ... more assignments
  ],
  "total_assignments": 10
}
```

## 🔍 Debugging

### Log Output
The implementation includes comprehensive logging:
- Variable creation process
- Constraint application
- Solution extraction
- Error handling

### Common Issues
1. **No feasible solution**: Check if constraints are too restrictive
2. **Zero assignments**: Verify teacher/room availability overlaps
3. **Missing subjects**: Ensure all subjects have valid teacher-room combinations

## 📈 Performance

- **Solver Timeout**: 5 minutes for complex problems
- **Memory Usage**: Scales with number of variables
- **Optimization**: Uses boolean variables for efficiency
- **Scalability**: Handles multiple batches, teachers, and subjects


