# Quick Test - Frontend & Backend Integration

**Status**: Ready to Test ✅

---

## 🧪 Step-by-Step Test

### Step 1: Start Backend
```bash
cd backend
python main.py
```

**Expected Output**:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Verify Backend is Running
Open browser and go to:
```
http://localhost:8000/docs
```

**Expected**: Swagger UI with all API endpoints listed

### Step 3: Open Frontend
Open browser and go to:
```
file:///path/to/index.html
```

Or use Python server:
```bash
cd timetableproject
python -m http.server 3000
# Then open http://localhost:3000
```

### Step 4: Test Timetable Generation

1. **Fill Week Configuration**
   - Start Time: 09:00
   - End Time: 16:00
   - Lunch: 13:00-14:00
   - Days: Mon-Fri

2. **Select Department**
   - Choose "Computer Science"

3. **Configure Subjects (Year 1)**
   - Add: Mathematics (3 hours, theory)
   - Add: Physics (2 hours, theory)
   - Add: Programming (2 hours, practical)

4. **Click "Generate Timetable"**

**Expected Result**:
- Loading overlay appears
- Backend receives request on `/api/timetable/generate`
- Timetable is generated
- Results displayed in "View Schedule" tab

### Step 5: Test Department Management

1. **Go to "Departments" tab**
2. **Click "+ Add Department"**
3. **Fill in**:
   - Name: "Electrical Engineering"
   - Code: "EE"
4. **Click "Save Department"**

**Expected Result**:
- Department saved to backend
- Department appears in list
- No errors in console

### Step 6: Test Room Management

1. **Go to "Rooms & Labs" tab**
2. **Click "+ Add Room/Lab"**
3. **Fill in**:
   - Name: "Room 201"
   - Type: "Classroom"
   - Capacity: 50
   - Location: "Building B"
4. **Click "Save Room/Lab"**

**Expected Result**:
- Room saved to backend
- Room appears in list
- No errors in console

---

## 🔍 Debugging Checklist

### Backend Issues
- [ ] Backend running on port 8000?
  ```bash
  curl http://localhost:8000/health
  ```

- [ ] All routes working?
  ```bash
  curl http://localhost:8000/docs
  ```

- [ ] Check logs for errors

### Frontend Issues
- [ ] Open DevTools (F12)
- [ ] Check Console tab for errors
- [ ] Check Network tab for API calls
- [ ] Verify API URLs use port 8000

### Network Issues
- [ ] Backend and frontend on same machine?
- [ ] Firewall blocking port 8000?
- [ ] CORS enabled in backend? (Should be ✅)

---

## ✅ Success Indicators

### Backend
- ✅ Server starts without errors
- ✅ Health check returns 200
- ✅ API docs accessible at /docs
- ✅ All endpoints listed

### Frontend
- ✅ Page loads without errors
- ✅ Console has no errors
- ✅ API calls visible in Network tab
- ✅ Responses are successful (200)

### Integration
- ✅ Timetable generates successfully
- ✅ Departments can be added/deleted
- ✅ Rooms can be added/deleted
- ✅ Data persists across page reloads

---

## 🚨 Common Issues & Fixes

### Issue: "Cannot POST /api/timetable/generate"
**Cause**: Backend not running  
**Fix**: Start backend with `python main.py`

### Issue: "Failed to fetch"
**Cause**: Port 5000 vs 8000 mismatch  
**Fix**: Already fixed in script.js ✅

### Issue: CORS Error
**Cause**: Backend CORS not configured  
**Fix**: Already configured in main.py ✅

### Issue: Blank response
**Cause**: Backend error  
**Fix**: Check backend logs for errors

---

## 📊 Expected API Calls

When you generate a timetable, you should see:

```
POST http://localhost:8000/api/timetable/generate
Content-Type: application/json

{
  "department": "Computer Science",
  "mode": "all",
  "selectedYear": null,
  "yearConfigs": {...},
  "weekConfig": {...},
  "miniProject": {...},
  "mathsTutorial": {...},
  "rooms": [...],
  "labs": [...]
}

Response:
{
  "status": "success",
  "timetable": [...],
  "conflicts": []
}
```

---

## 🎯 Test Results

| Test | Status | Notes |
|------|--------|-------|
| Backend starts | ⏳ | Run `python main.py` |
| Health check | ⏳ | Visit `/health` endpoint |
| Frontend loads | ⏳ | Open `index.html` |
| Generate timetable | ⏳ | Fill form and click button |
| Add department | ⏳ | Use Departments tab |
| Add room | ⏳ | Use Rooms & Labs tab |
| Load data | ⏳ | Check if data persists |

---

## 🚀 Next Steps

1. ✅ Start backend
2. ✅ Open frontend
3. ✅ Run through all tests
4. ✅ Check console for errors
5. ✅ Verify all features work
6. ✅ Deploy to production

---

**Ready to test!** 🧪

Start with: `python main.py` in the backend folder
