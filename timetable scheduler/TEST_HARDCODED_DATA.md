# Testing Hardcoded Data

## ✅ Quick Verification Checklist

### Frontend Tests
- [ ] Open `index.html` in browser
- [ ] Check browser console (F12) for "Hardcoded data initialized" message
- [ ] Go to "Departments" tab - should see:
  - Electrical
  - Computer Science
  - IOT
- [ ] Go to "Rooms & Labs" tab - should see:
  - C1, C2, C3... C15 (classrooms)
  - L1, L2, L3... L10 (labs)
- [ ] Total: 25 rooms (15 classrooms + 10 labs)
- [ ] Go to "Generate Timetable" tab - department dropdown should show 3 departments
- [ ] Verify batches are set to Batch A, B, C for all years

### Backend Tests
1. **Start Backend**
   ```bash
   cd backend
   python main.py
   ```

2. **Check Startup Logs**
   Should see:
   ```
   Initializing hardcoded data...
   Departments: ['Electrical', 'Computer Science', 'IOT']
   Classrooms: C1-C15 (15 total)
   Labs: L1-L10 (10 total)
   Batches: ['Batch A', 'Batch B', 'Batch C']
   Years: [1, 2, 3, 4]
   Hardcoded data initialized successfully!
   ```

3. **Test API Endpoints**
   
   **Get Departments:**
   ```bash
   curl http://localhost:8000/api/departments/
   ```
   Expected: 3 departments (Electrical, Computer Science, IOT)

   **Get Rooms:**
   ```bash
   curl http://localhost:8000/api/rooms/
   ```
   Expected: 25 rooms (C1-C15, L1-L10)

### Integration Tests
1. **Generate Timetable**
   - Select a department from dropdown (should show 3 options)
   - Add some subjects
   - Click "Generate Timetable"
   - Should work with hardcoded rooms

2. **View Schedule**
   - After generating, go to "View Schedule"
   - Filter by department (should show 3 options)
   - Timetable should display using hardcoded rooms

---

## 📊 Expected Data Summary

### Departments
| Name | Code | Description |
|------|------|-------------|
| Electrical | EE | Department of Electrical Engineering |
| Computer Science | CS | Department of Computer Science and Engineering |
| IOT | IOT | Department of Internet of Things |

### Rooms
| Type | Count | Names | Capacity | Location |
|------|-------|-------|----------|----------|
| Classroom | 15 | C1-C15 | 60 | Building A |
| Lab | 10 | L1-L10 | 30 | Building B |
| **Total** | **25** | - | - | - |

### Batches
- Batch A
- Batch B
- Batch C

### Years
- First Year (3 batches)
- Second Year (3 batches)
- Third Year (3 batches)
- Fourth Year (3 batches)

---

## 🔍 Troubleshooting

### Frontend Issues

**Problem**: Hardcoded data not showing in dropdowns
- **Solution**: 
  1. Hard refresh browser (Ctrl+Shift+R)
  2. Check browser console for errors
  3. Verify `hardcoded_data.js` is loaded (check Network tab)

**Problem**: Departments showing but rooms not showing
- **Solution**:
  1. Check that `hardcoded_data.js` is loaded before `script.js`
  2. Verify `initializeHardcodedData()` is called
  3. Check console for any JavaScript errors

### Backend Issues

**Problem**: Backend won't start
- **Solution**:
  1. Check that `hardcoded_data.py` exists in backend folder
  2. Verify import statement in `main.py`
  3. Check Python syntax errors

**Problem**: API returns empty departments/rooms
- **Solution**:
  1. Verify `hardcoded_data.py` is imported in routes
  2. Check that `departments_db` and `rooms_db` are initialized
  3. Restart backend

---

## ✨ Success Criteria

✅ All tests pass when:
1. Frontend shows 3 departments in all dropdowns
2. Frontend shows 25 rooms (15 classrooms + 10 labs)
3. Backend startup logs show all hardcoded data
4. API endpoints return correct data
5. Timetable generation works with hardcoded data

---

**Ready to test!** 🚀

