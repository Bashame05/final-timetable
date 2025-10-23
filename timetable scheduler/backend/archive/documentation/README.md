# AI Timetable Scheduler Backend

A FastAPI-based backend service for AI-powered college timetable scheduling using Google OR-Tools CP-SAT solver.

## Features

- **Constraint Programming**: Uses OR-Tools CP-SAT solver for optimal timetable generation
- **Flexible Constraints**: Supports various scheduling constraints including:
  - Teacher availability and overlap prevention
  - Room availability and type requirements
  - Break time enforcement (12 PM - 1 PM)
  - Subject-specific duration rules (Practical = 2h, Theory ≤ 2h, Project ≥ 2h)
  - Consecutive hour scheduling
- **RESTful API**: Clean FastAPI endpoints for timetable generation and validation
- **Data Validation**: Comprehensive input validation using Pydantic models
- **Solution Validation**: Post-solution constraint checking and violation reporting

## Project Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI application entrypoint
│   ├── models.py        # Pydantic data models
│   ├── solver.py        # OR-Tools CP-SAT solver implementation
│   ├── validator.py     # Constraint validation logic
│   └── utils.py         # Helper functions and utilities
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python -m app.main
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Example API Usage

#### 1. Get Example Request
```bash
curl -X GET "http://localhost:8000/api/timetable/example"
```

#### 2. Solve Timetable
```bash
curl -X POST "http://localhost:8000/api/timetable/solve" \
     -H "Content-Type: application/json" \
     -d @example_request.json
```

#### 3. Validate Solution
```bash
curl -X POST "http://localhost:8000/api/timetable/validate" \
     -H "Content-Type: application/json" \
     -d '{"request": {...}, "result": {...}}'
```

## Data Models

### Core Entities

- **Teacher**: Faculty members with availability slots and subject expertise
- **Room**: Physical spaces (classrooms/labs) with availability and capacity
- **Subject**: Academic courses with type, duration, and requirements
- **Batch**: Student groups with assigned subjects
- **Lecture**: Scheduled class sessions with time, location, and participants

### Request Format

```json
{
  "teachers": [
    {
      "id": "T1",
      "name": "Dr. Smith",
      "available_slots": ["Mon_9", "Mon_10", "Tue_9"],
      "subjects": ["OS", "DBMS"]
    }
  ],
  "rooms": [
    {
      "id": "C301",
      "name": "Classroom 301",
      "type": "classroom",
      "available_slots": ["Mon_9", "Mon_10", "Tue_9"],
      "capacity": 60
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
    }
  ],
  "batches": [
    {
      "id": "TYCSE_A",
      "name": "TY CSE A",
      "subjects": ["OS"],
      "strength": 60
    }
  ],
  "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
  "time_slots": ["9", "10", "11", "12", "1", "2", "3"],
  "break_start": "12",
  "break_end": "1"
}
```

### Response Format

```json
{
  "success": true,
  "timetables": [
    {
      "batch": "TY CSE A",
      "slots": [
        {
          "day": "Mon",
          "time": "9:00-10:00",
          "subject": "Operating Systems",
          "teacher": "Dr. Smith",
          "room": "Classroom 301",
          "type": "theory",
          "batch": "TY CSE A"
        }
      ],
      "status": "success"
    }
  ],
  "errors": [],
  "warnings": []
}
```

## Constraint Rules

### 1. **No Overlaps**
- Teachers cannot be assigned to multiple classes simultaneously
- Rooms cannot host multiple classes simultaneously
- Each batch can have only one class per time slot

### 2. **Break Time**
- No classes scheduled during 12 PM - 1 PM break period

### 3. **Subject Duration Rules**
- **Practical**: Must be exactly 2 consecutive hours in labs
- **Theory**: Maximum 2 consecutive hours in classrooms
- **Project**: Minimum 2 hours, can be in labs or classrooms

### 4. **Room Type Requirements**
- Practical subjects must use lab rooms
- Theory subjects should use classroom rooms
- Project subjects can use either room type

### 5. **Teacher-Subject Matching**
- Only teachers assigned to a subject can teach it
- Teachers must be available during assigned time slots

## Development

### Running Tests
```bash
pytest
```

### Code Style
The project follows Python PEP 8 standards. Consider using:
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

### Adding New Constraints

1. **In Solver**: Add constraint logic in `solver.py`
2. **In Validator**: Add validation logic in `validator.py`
3. **In Models**: Update data models in `models.py` if needed

## Performance Considerations

- **Solver Timeout**: Default 5 minutes for complex problems
- **Memory Usage**: Scales with number of variables (teachers × rooms × subjects × time_slots)
- **Optimization**: Consider reducing search space for large problems

## Troubleshooting

### Common Issues

1. **No Solution Found**: Check constraint feasibility, reduce requirements
2. **Timeout**: Increase solver timeout or simplify constraints
3. **Import Errors**: Ensure all dependencies are installed correctly

### Logging

The application uses Python's standard logging module. Set log level via environment variable:
```bash
export LOG_LEVEL=DEBUG
```

## License

This project is part of an AI-based timetable scheduling system for educational institutions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions, please refer to the project documentation or contact the development team.
