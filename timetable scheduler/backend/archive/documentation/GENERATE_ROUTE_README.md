# New Timetable Generation Route

## Overview

A new FastAPI route `/api/timetable/generate` has been added that uses OR-Tools CP-SAT solver to generate feasible timetables with simplified constraints.

## Route Details

- **Endpoint**: `POST /api/timetable/generate`
- **Purpose**: Generate feasible timetables using CP-SAT constraint programming
- **Input**: JSON data with teachers, subjects, rooms, batches, days, and time slots
- **Output**: JSON response with generated timetable or failure reason

## Hard Constraints Implemented

1. **No Double-booking**: Teachers, rooms, and batches cannot be double-booked
2. **Teacher Availability**: Lectures must be in teacher's available slots
3. **Room Type Matching**: Practicals → labs, Theory → classrooms
4. **Consecutive Hours**:
   - Practicals: exactly 2 consecutive slots
   - Theory: at most 2 consecutive slots
   - Projects: at least 2 consecutive slots
5. **Break Time**: No scheduling during 12 PM - 1 PM
6. **Batch Constraints**: No overlapping classes for any batch

## Input Format

```json
{
  "teachers": [
    {
      "id": "T1",
      "name": "Dr. Smith",
      "available_slots": ["Mon_9", "Mon_10"],
      "subjects": ["OS"]
    }
  ],
  "subjects": [
    {
      "id": "OS",
      "name": "Operating Systems",
      "type": "theory",
      "duration": 2,
      "teachers": ["T1"]
    }
  ],
  "rooms": [
    {
      "id": "C301",
      "name": "Classroom 301",
      "type": "classroom",
      "available_slots": ["Mon_9", "Mon_10"]
    }
  ],
  "batches": [
    {
      "id": "B1",
      "name": "TY CSE A",
      "subjects": ["OS"]
    }
  ],
  "days": ["Mon", "Tue", "Wed"],
  "time_slots": ["9", "10", "11", "12", "1", "2", "3"]
}
```

## Output Format

### Success Response
```json
{
  "status": "success",
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
      "start_slot": "Mon_9",
      "end_slot": "Mon_10",
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
  "reason": "no feasible solution",
  "details": "The given constraints cannot be satisfied with the provided data"
}
```

## Testing

### 1. Start the Server
```bash
cd "timetable scheduler/backend"
python run_server.py
```

### 2. Test with curl
```bash
curl -X POST "http://localhost:8000/api/timetable/generate" \
     -H "Content-Type: application/json" \
     -d @example_generate_request.json
```

### 3. Test with Python Script
```bash
python test_generate_route.py
```

### 4. Interactive Testing
Visit `http://localhost:8000/docs` and use the Swagger UI to test the endpoint.

## Key Features

- **CP-SAT Solver**: Uses Google OR-Tools for constraint satisfaction
- **Feasibility Check**: Returns clear error messages when no solution exists
- **Consecutive Scheduling**: Handles multi-hour lectures properly
- **Room Type Validation**: Ensures practicals use labs, theory uses classrooms
- **Break Time Enforcement**: Automatically avoids 12 PM - 1 PM slots
- **Comprehensive Constraints**: Covers all major scheduling requirements

## Error Handling

The route handles various error scenarios:
- **Infeasible Constraints**: Returns "no feasible solution" with details
- **Invalid Data**: Returns "internal error" with specific error message
- **Missing Data**: Gracefully handles missing fields with defaults

## Performance

- **Timeout**: Solver has a 5-minute timeout for complex problems
- **Scalability**: Handles multiple batches, teachers, and subjects
- **Memory Efficient**: Uses boolean variables for optimal memory usage

## Integration

This route can be easily integrated with frontend applications:
- Accepts standard JSON input
- Returns structured JSON output
- Compatible with REST API standards
- Includes comprehensive error handling

