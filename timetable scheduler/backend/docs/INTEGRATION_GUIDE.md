# Frontend-Backend Integration Guide

## 📋 Overview

This guide explains how to integrate your React frontend with the refactored FastAPI backend for the AI-based timetable scheduler.

---

## 🏗️ Backend Architecture

```
backend/
├── main.py                      # FastAPI entrypoint
├── routes/
│   ├── timetable_routes.py      # /api/timetable/*
│   ├── department_routes.py     # /api/departments/*
│   ├── room_routes.py           # /api/rooms/*
│   └── settings_routes.py       # /api/settings/*
├── models/
│   ├── data_models.py           # Pydantic validation models
│   ├── timetable_solver.py      # OR-Tools solver logic
│   ├── constraints.py           # Constraint definitions
│   └── utils.py                 # Helper functions
└── requirements.txt             # Python dependencies
```

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python main.py
```

Server runs on `http://localhost:8000`

### 3. View API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📡 API Endpoints

### Health Check
```
GET /health
```

### Settings Management

#### Set Week Configuration
```
POST /api/settings/week-config
Content-Type: application/json

{
  "week_start_time": "09:00",
  "week_end_time": "16:00",
  "lunch_start": "13:00",
  "lunch_end": "14:00",
  "working_days": ["Mon", "Tue", "Wed", "Thu", "Fri"]
}
```

#### Get Week Configuration
```
GET /api/settings/week-config
```

#### Set Special Sessions
```
POST /api/settings/special-sessions
Content-Type: application/json

{
  "mini_project": {
    "enabled": true,
    "hours_per_week": 4,
    "days_per_week": 2,
    "duration_per_session": 1
  },
  "math_tutorial": {
    "enabled": true,
    "hours_per_week": 1,
    "days_per_week": 1,
    "duration_per_session": 1
  }
}
```

### Department Management

#### Create Department
```
POST /api/departments/
Content-Type: application/json

{
  "department_name": "Computer Engineering",
  "subjects": [
    {
      "name": "DBMS",
      "type": "theory+lab",
      "hours_per_week": 3
    },
    {
      "name": "CN",
      "type": "theory",
      "hours_per_week": 3
    }
  ]
}
```

#### List Departments
```
GET /api/departments/
```

#### Get Department
```
GET /api/departments/{department_name}
```

#### Update Department
```
PUT /api/departments/{department_name}
Content-Type: application/json

{
  "department_name": "Computer Engineering",
  "subjects": [...]
}
```

#### Delete Department
```
DELETE /api/departments/{department_name}
```

#### Add Subject to Department
```
POST /api/departments/{department_name}/subjects
Content-Type: application/json

{
  "name": "AI",
  "type": "theory",
  "hours_per_week": 3
}
```

### Room Management

#### Create/Update Rooms
```
POST /api/rooms/
Content-Type: application/json

{
  "rooms": [
    {
      "name": "Room 101",
      "type": "classroom",
      "capacity": 60,
      "location": "Building A"
    },
    {
      "name": "CS Lab 1",
      "type": "lab",
      "capacity": 30,
      "location": "Building C",
      "for_subject": "DBMS"
    }
  ]
}
```

#### List All Rooms
```
GET /api/rooms/
```

#### Get Room by Name
```
GET /api/rooms/{room_name}
```

#### Get Rooms by Type
```
GET /api/rooms/type/{room_type}
```
Where `room_type` is "classroom" or "lab"

#### Get Rooms by Location
```
GET /api/rooms/location/{location}
```

#### Get Labs for Subject
```
GET /api/rooms/subject/{subject_name}
```

### Timetable Generation

#### Generate Timetable
```
POST /api/timetable/generate
Content-Type: application/json

{
  "department": "Computer Engineering",
  "week_config": {
    "week_start_time": "09:00",
    "week_end_time": "16:00",
    "lunch_start": "13:00",
    "lunch_end": "14:00",
    "working_days": ["Mon", "Tue", "Wed", "Thu", "Fri"]
  },
  "rooms": [
    {
      "name": "Room 101",
      "type": "classroom",
      "capacity": 60,
      "location": "Building A"
    }
  ],
  "subjects": [
    {
      "name": "DBMS",
      "type": "theory+lab",
      "hours_per_week": 3
    }
  ],
  "special_sessions": {}
}
```

#### Response (Success)
```json
{
  "status": "success",
  "message": "✅ Timetable generated successfully",
  "timetable": [
    {
      "day": "Mon",
      "slot": "09:00-10:00",
      "subject": "DBMS",
      "room": "Room 101",
      "teacher": null,
      "type": "theory+lab"
    }
  ],
  "conflicts": [],
  "metadata": {
    "department": "Computer Engineering",
    "total_slots": 1,
    "working_days": ["Mon", "Tue", "Wed", "Thu", "Fri"]
  }
}
```

#### Response (Failure)
```json
{
  "status": "failed",
  "message": "❌ Failed to generate timetable",
  "timetable": [],
  "conflicts": [
    {
      "type": "feasibility",
      "entity": "problem",
      "day": "",
      "slot": "",
      "reason": "Not enough slots: 10 hours required, 5 slots available"
    }
  ],
  "metadata": {
    "department": "Computer Engineering"
  }
}
```

---

## 💻 Frontend Integration Examples

### React Component Example

```javascript
import React, { useState } from 'react';

function TimetableGenerator() {
  const [loading, setLoading] = useState(false);
  const [timetable, setTimetable] = useState([]);
  const [error, setError] = useState(null);

  const generateTimetable = async () => {
    setLoading(true);
    setError(null);

    try {
      const payload = {
        department: "Computer Engineering",
        week_config: {
          week_start_time: "09:00",
          week_end_time: "16:00",
          lunch_start: "13:00",
          lunch_end: "14:00",
          working_days: ["Mon", "Tue", "Wed", "Thu", "Fri"]
        },
        rooms: [
          {
            name: "Room 101",
            type: "classroom",
            capacity: 60,
            location: "Building A"
          }
        ],
        subjects: [
          {
            name: "DBMS",
            type: "theory+lab",
            hours_per_week: 3
          }
        ],
        special_sessions: {}
      };

      const response = await fetch("http://localhost:8000/api/timetable/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (data.status === "success") {
        setTimetable(data.timetable);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={generateTimetable} disabled={loading}>
        {loading ? "Generating..." : "Generate Timetable"}
      </button>

      {error && <div style={{ color: "red" }}>{error}</div>}

      {timetable.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Day</th>
              <th>Time</th>
              <th>Subject</th>
              <th>Room</th>
              <th>Type</th>
            </tr>
          </thead>
          <tbody>
            {timetable.map((slot, idx) => (
              <tr key={idx}>
                <td>{slot.day}</td>
                <td>{slot.slot}</td>
                <td>{slot.subject}</td>
                <td>{slot.room}</td>
                <td>{slot.type}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default TimetableGenerator;
```

### Setup Departments and Rooms

```javascript
async function setupBackend() {
  // 1. Set week configuration
  await fetch("http://localhost:8000/api/settings/week-config", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      week_start_time: "09:00",
      week_end_time: "16:00",
      lunch_start: "13:00",
      lunch_end: "14:00",
      working_days: ["Mon", "Tue", "Wed", "Thu", "Fri"]
    })
  });

  // 2. Create department
  await fetch("http://localhost:8000/api/departments/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      department_name: "Computer Engineering",
      subjects: [
        { name: "DBMS", type: "theory+lab", hours_per_week: 3 },
        { name: "CN", type: "theory", hours_per_week: 3 }
      ]
    })
  });

  // 3. Create rooms
  await fetch("http://localhost:8000/api/rooms/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      rooms: [
        {
          name: "Room 101",
          type: "classroom",
          capacity: 60,
          location: "Building A"
        },
        {
          name: "CS Lab 1",
          type: "lab",
          capacity: 30,
          location: "Building C",
          for_subject: "DBMS"
        }
      ]
    })
  });

  console.log("Backend setup complete!");
}
```

---

## 🔄 Data Flow

```
Frontend (React)
    ↓
    ├─→ Week Configuration (Settings)
    ├─→ Department & Subjects
    ├─→ Rooms & Labs
    └─→ Generate Timetable Request
         ↓
Backend (FastAPI)
    ↓
    ├─→ Validate Input (Pydantic)
    ├─→ Create TimetableSolver
    ├─→ Generate Time Slots
    ├─→ Create CP-SAT Variables
    ├─→ Add Constraints
    ├─→ Solve with OR-Tools
    └─→ Extract & Format Solution
         ↓
Response (JSON)
    ↓
Frontend (React)
    ↓
    ├─→ Display Timetable
    ├─→ Highlight Conflicts
    └─→ Show Statistics
```

---

## ✅ Data Validation

All inputs are validated using Pydantic models:

### Room
- `name`: str (required)
- `type`: "classroom" or "lab" (required)
- `capacity`: int > 0 (required)
- `location`: str (required)
- `for_subject`: str (optional)

### Subject
- `name`: str (required)
- `type`: "theory", "lab", or "theory+lab" (required)
- `hours_per_week`: int > 0 (required)

### WeekConfig
- `week_start_time`: str in "HH:MM" format (required)
- `week_end_time`: str in "HH:MM" format (required)
- `lunch_start`: str in "HH:MM" format (required)
- `lunch_end`: str in "HH:MM" format (required)
- `working_days`: List of valid day names (required)

---

## 🧪 Testing the Integration

### 1. Test Health Check
```bash
curl http://localhost:8000/health
```

### 2. Test Settings
```bash
curl -X POST http://localhost:8000/api/settings/week-config \
  -H "Content-Type: application/json" \
  -d '{
    "week_start_time": "09:00",
    "week_end_time": "16:00",
    "lunch_start": "13:00",
    "lunch_end": "14:00",
    "working_days": ["Mon", "Tue", "Wed", "Thu", "Fri"]
  }'
```

### 3. Test Department Creation
```bash
curl -X POST http://localhost:8000/api/departments/ \
  -H "Content-Type: application/json" \
  -d '{
    "department_name": "Computer Engineering",
    "subjects": [
      {"name": "DBMS", "type": "theory+lab", "hours_per_week": 3}
    ]
  }'
```

### 4. Test Room Creation
```bash
curl -X POST http://localhost:8000/api/rooms/ \
  -H "Content-Type: application/json" \
  -d '{
    "rooms": [
      {"name": "Room 101", "type": "classroom", "capacity": 60, "location": "Building A"}
    ]
  }'
```

### 5. Test Timetable Generation
```bash
curl -X POST http://localhost:8000/api/timetable/generate \
  -H "Content-Type: application/json" \
  -d '{
    "department": "Computer Engineering",
    "week_config": {
      "week_start_time": "09:00",
      "week_end_time": "16:00",
      "lunch_start": "13:00",
      "lunch_end": "14:00",
      "working_days": ["Mon", "Tue", "Wed", "Thu", "Fri"]
    },
    "rooms": [
      {"name": "Room 101", "type": "classroom", "capacity": 60, "location": "Building A"}
    ],
    "subjects": [
      {"name": "DBMS", "type": "theory+lab", "hours_per_week": 3}
    ],
    "special_sessions": {}
  }'
```

---

## 🔧 Troubleshooting

### "Connection refused"
- Make sure backend is running: `python main.py`
- Check if port 8000 is available

### "Validation error"
- Check data types match Pydantic models
- Verify time format is "HH:MM"
- Ensure day names are valid (Mon, Tue, etc.)

### "No feasible solution found"
- Verify total hours ≤ available slots
- Check room types match subject types
- Ensure working days are configured

---

## 📚 Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **OR-Tools Docs**: https://developers.google.com/optimization
- **API Swagger UI**: http://localhost:8000/docs

---

**Status**: ✅ Ready for Integration
**Version**: 2.0.0
