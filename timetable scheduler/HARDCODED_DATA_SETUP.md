# Hardcoded Data Setup - Complete

**Status**: ✅ Implemented in both Frontend and Backend

---

## 📋 What's Hardcoded

### Departments (3)
- **Electrical** (Code: EE)
- **Computer Science** (Code: CS)
- **IOT** (Code: IOT)

### Classrooms (15)
- **C1 to C15**
- Type: Classroom
- Capacity: 60 students each
- Location: Building A
- Tags: projector, whiteboard

### Labs (10)
- **L1 to L10**
- Type: Lab
- Capacity: 30 students each
- Location: Building B
- Tags: computers, equipment

### Batches (3)
- **Batch A**
- **Batch B**
- **Batch C**

### Years (4)
- **First Year** (3 batches)
- **Second Year** (3 batches)
- **Third Year** (3 batches)
- **Fourth Year** (3 batches)

---

## 🔧 Frontend Implementation

### Files Created
- `timetableproject/hardcoded_data.js` - Contains all hardcoded data

### Files Modified
- `timetableproject/index.html` - Added script include for hardcoded_data.js
- `timetableproject/script.js` - Changed initialization to use `initializeHardcodedData()`

### How It Works
1. `hardcoded_data.js` defines constants:
   - `HARDCODED_DEPARTMENTS`
   - `HARDCODED_CLASSROOMS`
   - `HARDCODED_LABS`
   - `HARDCODED_ROOMS` (combined)
   - `HARDCODED_BATCHES`

2. `initializeHardcodedData()` function:
   - Copies hardcoded data to `appState`
   - Sets batch names for all years
   - Logs initialization status

3. Called on page load via DOMContentLoaded event

---

## 🔧 Backend Implementation

### Files Created
- `backend/hardcoded_data.py` - Contains all hardcoded data

### Files Modified
- `backend/main.py` - Added startup event to log hardcoded data
- `backend/routes/department_routes.py` - Initialize departments_db with hardcoded data
- `backend/routes/room_routes.py` - Initialize rooms_db with hardcoded data

### How It Works
1. `hardcoded_data.py` defines:
   - `HARDCODED_DEPARTMENTS`
   - `HARDCODED_CLASSROOMS`
   - `HARDCODED_LABS`
   - `HARDCODED_ROOMS` (combined)
   - `HARDCODED_BATCHES`
   - `HARDCODED_YEARS`

2. On backend startup:
   - `main.py` logs all hardcoded data
   - `department_routes.py` populates `departments_db`
   - `room_routes.py` populates `rooms_db`

3. API endpoints return hardcoded data:
   - `GET /api/departments/` → Returns 3 departments
   - `GET /api/rooms/` → Returns 25 rooms (15 classrooms + 10 labs)

---

## ✅ Verification

### Frontend
1. Open browser console (F12)
2. Check logs: "Hardcoded data initialized"
3. Verify in Departments tab: See Electrical, Computer Science, IOT
4. Verify in Rooms tab: See C1-C15 and L1-L10

### Backend
1. Start backend: `python main.py`
2. Check logs for:
   ```
   Initializing hardcoded data...
   Departments: ['Electrical', 'Computer Science', 'IOT']
   Classrooms: C1-C15 (15 total)
   Labs: L1-L10 (10 total)
   Batches: ['Batch A', 'Batch B', 'Batch C']
   Years: [1, 2, 3, 4]
   ```

3. Test endpoints:
   ```bash
   curl http://localhost:8000/api/departments/
   curl http://localhost:8000/api/rooms/
   ```

---

## 🚀 Usage

### Frontend
- Departments dropdown automatically populated with 3 departments
- Rooms management shows all 25 rooms (C1-C15, L1-L10)
- Batches automatically set to A, B, C for all years

### Backend
- All API endpoints return hardcoded data
- Can still add new departments/rooms (stored in memory)
- Restart backend to reset to hardcoded data

---

## 📝 Data Structure

### Department Object
```python
{
    "name": "Electrical",
    "code": "EE",
    "description": "Department of Electrical Engineering"
}
```

### Room Object
```python
{
    "name": "C1",
    "type": "classroom",
    "capacity": 60,
    "location": "Building A",
    "tags": ["projector", "whiteboard"]
}
```

### Batch Object
```python
"Batch A"  # String
```

### Year Object
```python
{
    "name": "First Year",
    "batches": 3,
    "batch_names": ["Batch A", "Batch B", "Batch C"]
}
```

---

## 🔄 Next Steps

1. ✅ Hardcoded data setup complete
2. ⏳ Implement batch-aware scheduling
3. ⏳ Add teacher management
4. ⏳ Support split lectures
5. ⏳ Add special sessions (projects, tutorials)

---

**Status**: Ready for Phase 2 - Batch-aware scheduling implementation

