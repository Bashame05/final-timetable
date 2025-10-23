# Debug: Timetable Generation Error

**Issue**: "Error generating timetable" message

---

## 🔍 Quick Fixes

### 1. Check Backend is Running
```bash
# Terminal 1
cd backend
python main.py
```

**Expected Output**:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Verify Backend Health
Open browser:
```
http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "service": "timetable-scheduler",
  "version": "2.0.0"
}
```

### 3. Check Browser Console
1. Open DevTools (F12)
2. Go to **Console** tab
3. Look for error messages
4. Check **Network** tab for API call details

---

## 🚨 Common Errors & Solutions

### Error: "Failed to fetch"
**Cause**: Backend not running or wrong port  
**Fix**: 
```bash
# Make sure backend is running on port 8000
python main.py
```

### Error: "Cannot POST /api/timetable/generate"
**Cause**: Backend not running  
**Fix**: Start backend with `python main.py`

### Error: "Validation error"
**Cause**: Missing or wrong data format  
**Fix**: Check that:
- Department is selected
- At least one subject is added for Year 1
- Week configuration is set

### Error: "No feasible solution"
**Cause**: Not enough time slots for subjects  
**Fix**: 
- Reduce subject hours
- Add more working days
- Increase week hours

---

## 📋 Required Data for Timetable Generation

### Week Configuration
```
✅ Start Time: 09:00
✅ End Time: 16:00
✅ Lunch Start: 13:00
✅ Lunch End: 14:00
✅ Working Days: Mon-Fri (at least 3 days)
```

### Department
```
✅ Must select a department
```

### Subjects (Year 1)
```
✅ At least 1 subject
✅ Subject name (e.g., "Mathematics")
✅ Subject type (theory/practical/both)
✅ Hours per week (e.g., 3)
```

### Rooms
```
✅ At least 1 room
✅ Room name (e.g., "Room 101")
✅ Room type (classroom/lab)
✅ Capacity (e.g., 60)
```

---

## 🧪 Step-by-Step Test

### Step 1: Start Backend
```bash
cd backend
python main.py
```

### Step 2: Open Frontend
```
Open index.html in browser
```

### Step 3: Fill Form
1. **Week Configuration** - Already filled with defaults ✅
2. **Select Department** - Choose "Computer Science"
3. **Add Subjects (Year 1)**:
   - Click "+ Add Subject"
   - Name: "Mathematics"
   - Type: "Theory Only"
   - Hours: 3
   - Click "✕" to remove if needed

4. **Add Rooms**:
   - Go to "Rooms & Labs" tab
   - Click "+ Add Room/Lab"
   - Name: "Room 101"
   - Type: "Classroom"
   - Capacity: 60
   - Click "Save Room/Lab"

### Step 4: Generate
1. Go back to "Generate Timetable" tab
2. Click "Generate Timetable"
3. Wait for loading...
4. Should see timetable in "View Schedule" tab

---

## 🔧 API Request Format

The frontend sends this to backend:

```json
{
  "department": "Computer Science",
  "week_config": {
    "week_start_time": "09:00",
    "week_end_time": "16:00",
    "lunch_start": "13:00",
    "lunch_end": "14:00",
    "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
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
      "name": "Mathematics",
      "type": "theory",
      "hours_per_week": 3
    }
  ],
  "special_sessions": {}
}
```

---

## 📊 Backend Response

### Success Response
```json
{
  "status": "success",
  "timetable": [
    {
      "day": "Monday",
      "slot": "09:00-10:00",
      "subject": "Mathematics",
      "room": "Room 101",
      "type": "theory"
    }
  ]
}
```

### Error Response
```json
{
  "status": "error",
  "message": "No feasible solution found"
}
```

---

## 🐛 Debugging Steps

### 1. Check Backend Logs
Look at terminal where backend is running for error messages

### 2. Check Browser Network Tab
1. Open DevTools (F12)
2. Go to **Network** tab
3. Click "Generate Timetable"
4. Look for `/api/timetable/generate` request
5. Click it and check:
   - **Request** tab - see what was sent
   - **Response** tab - see what backend returned
   - **Status** - should be 200 for success

### 3. Check Browser Console
1. Open DevTools (F12)
2. Go to **Console** tab
3. Look for red error messages
4. Click on error to see details

### 4. Test Backend Directly
```bash
curl -X POST http://localhost:8000/api/timetable/generate \
  -H "Content-Type: application/json" \
  -d '{
    "department": "Computer Science",
    "week_config": {
      "week_start_time": "09:00",
      "week_end_time": "16:00",
      "lunch_start": "13:00",
      "lunch_end": "14:00",
      "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    },
    "rooms": [{
      "name": "Room 101",
      "type": "classroom",
      "capacity": 60,
      "location": "Building A"
    }],
    "subjects": [{
      "name": "Mathematics",
      "type": "theory",
      "hours_per_week": 3
    }],
    "special_sessions": {}
  }'
```

---

## ✅ Checklist

- [ ] Backend running on port 8000
- [ ] Health check returns 200
- [ ] Department selected
- [ ] At least 1 subject added
- [ ] At least 1 room added
- [ ] Week configuration filled
- [ ] No errors in browser console
- [ ] Network request shows 200 status

---

## 📞 Still Having Issues?

1. **Check backend logs** - Look at terminal output
2. **Check browser console** - F12 → Console tab
3. **Check network request** - F12 → Network tab
4. **Test backend directly** - Use curl command above
5. **Restart everything** - Stop and start backend

---

**Status**: Ready to debug! 🔍
