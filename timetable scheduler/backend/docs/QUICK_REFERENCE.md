# Quick Reference Guide

## 🚀 Start Backend
```bash
cd backend
python main.py
```

## 📖 Documentation
- **Full Guide**: INTEGRATION_GUIDE.md
- **API Docs**: http://localhost:8000/docs
- **Project Info**: README_REFACTORED.md
- **Summary**: REFACTORING_COMPLETE.md

---

## 📡 API Endpoints Quick Reference

### Settings
```bash
# Set week config
POST /api/settings/week-config
{
  "week_start_time": "09:00",
  "week_end_time": "16:00",
  "lunch_start": "13:00",
  "lunch_end": "14:00",
  "working_days": ["Mon", "Tue", "Wed", "Thu", "Fri"]
}

# Get week config
GET /api/settings/week-config

# Set special sessions
POST /api/settings/special-sessions
{
  "mini_project": {
    "enabled": true,
    "hours_per_week": 4,
    "days_per_week": 2,
    "duration_per_session": 1
  }
}

# Get all settings
GET /api/settings/
```

### Departments
```bash
# Create department
POST /api/departments/
{
  "department_name": "Computer Engineering",
  "subjects": [
    {"name": "DBMS", "type": "theory+lab", "hours_per_week": 3},
    {"name": "CN", "type": "theory", "hours_per_week": 3}
  ]
}

# List departments
GET /api/departments/

# Get department
GET /api/departments/{name}

# Update department
PUT /api/departments/{name}

# Delete department
DELETE /api/departments/{name}

# Add subject
POST /api/departments/{name}/subjects
{"name": "AI", "type": "theory", "hours_per_week": 3}

# Remove subject
DELETE /api/departments/{name}/subjects/{subject}
```

### Rooms
```bash
# Create/update rooms
POST /api/rooms/
{
  "rooms": [
    {"name": "Room 101", "type": "classroom", "capacity": 60, "location": "Building A"},
    {"name": "CS Lab 1", "type": "lab", "capacity": 30, "location": "Building C", "for_subject": "DBMS"}
  ]
}

# List all rooms
GET /api/rooms/

# Get room
GET /api/rooms/{name}

# Get by type
GET /api/rooms/type/classroom
GET /api/rooms/type/lab

# Get by location
GET /api/rooms/location/{location}

# Get labs for subject
GET /api/rooms/subject/{subject}
```

### Timetable
```bash
# Generate timetable
POST /api/timetable/generate
{
  "department": "Computer Engineering",
  "week_config": {...},
  "rooms": [...],
  "subjects": [...],
  "special_sessions": {}
}

# Get status
GET /api/timetable/status

# Validate request
POST /api/timetable/validate
{...}
```

---

## 📊 Data Models

### Room
```json
{
  "name": "Room 101",
  "type": "classroom",  // or "lab"
  "capacity": 60,
  "location": "Building A",
  "for_subject": null
}
```

### Subject
```json
{
  "name": "DBMS",
  "type": "theory",  // or "lab" or "theory+lab"
  "hours_per_week": 3
}
```

### WeekConfig
```json
{
  "week_start_time": "09:00",
  "week_end_time": "16:00",
  "lunch_start": "13:00",
  "lunch_end": "14:00",
  "working_days": ["Mon", "Tue", "Wed", "Thu", "Fri"]
}
```

---

## 🧪 Test with cURL

```bash
# Health check
curl http://localhost:8000/health

# Create department
curl -X POST http://localhost:8000/api/departments/ \
  -H "Content-Type: application/json" \
  -d '{
    "department_name": "Computer Engineering",
    "subjects": [
      {"name": "DBMS", "type": "theory+lab", "hours_per_week": 3}
    ]
  }'

# Create rooms
curl -X POST http://localhost:8000/api/rooms/ \
  -H "Content-Type: application/json" \
  -d '{
    "rooms": [
      {"name": "Room 101", "type": "classroom", "capacity": 60, "location": "Building A"}
    ]
  }'

# Generate timetable
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

## 💻 React Integration

```javascript
// Setup
async function setupBackend() {
  // 1. Set week config
  await fetch("/api/settings/week-config", {
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
  await fetch("/api/departments/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      department_name: "Computer Engineering",
      subjects: [
        { name: "DBMS", type: "theory+lab", hours_per_week: 3 }
      ]
    })
  });

  // 3. Create rooms
  await fetch("/api/rooms/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      rooms: [
        { name: "Room 101", type: "classroom", capacity: 60, location: "Building A" }
      ]
    })
  });
}

// Generate timetable
async function generateTimetable() {
  const response = await fetch("/api/timetable/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      department: "Computer Engineering",
      week_config: {
        week_start_time: "09:00",
        week_end_time: "16:00",
        lunch_start: "13:00",
        lunch_end: "14:00",
        working_days: ["Mon", "Tue", "Wed", "Thu", "Fri"]
      },
      rooms: [
        { name: "Room 101", type: "classroom", capacity: 60, location: "Building A" }
      ],
      subjects: [
        { name: "DBMS", type: "theory+lab", hours_per_week: 3 }
      ],
      special_sessions: {}
    })
  });

  const data = await response.json();
  if (data.status === "success") {
    console.log("Timetable:", data.timetable);
  } else {
    console.error("Error:", data.message);
  }
}
```

---

## 🏗️ Project Structure

```
backend/
├── main.py                      # FastAPI app
├── routes/
│   ├── timetable_routes.py      # /api/timetable/*
│   ├── department_routes.py     # /api/departments/*
│   ├── room_routes.py           # /api/rooms/*
│   └── settings_routes.py       # /api/settings/*
└── models/
    ├── data_models.py           # Pydantic models
    ├── timetable_solver.py      # OR-Tools solver
    ├── constraints.py           # Constraints
    └── utils.py                 # Helpers
```

---

## ✅ Constraints

1. **No Overlaps** - Teachers, rooms, batches
2. **Availability** - Respect available times
3. **Break Time** - No classes during lunch
4. **Duration** - Theory max 2h, Lab exactly 2h
5. **Room Type** - Theory→classroom, Lab→lab
6. **Special Sessions** - Respect constraints

---

## 🚨 Common Issues

| Issue | Solution |
|-------|----------|
| Connection refused | Start backend: `python main.py` |
| Validation error | Check data types and formats |
| No feasible solution | Total hours ≤ available slots |
| Solver timeout | Increase time_limit or reduce problem size |

---

## 📚 Files

| File | Purpose |
|------|---------|
| main.py | FastAPI app |
| routes/*.py | API endpoints |
| models/data_models.py | Validation |
| models/timetable_solver.py | Solver |
| models/constraints.py | Constraints |
| models/utils.py | Helpers |
| INTEGRATION_GUIDE.md | Frontend guide |
| README_REFACTORED.md | Full docs |
| REFACTORING_COMPLETE.md | Summary |
| QUICK_REFERENCE.md | This file |

---

## 🎯 Next Steps

1. Start backend: `python main.py`
2. View API docs: http://localhost:8000/docs
3. Read INTEGRATION_GUIDE.md
4. Integrate with React frontend
5. Test with sample data

---

**Status**: ✅ Ready to Use  
**Version**: 2.0.0
