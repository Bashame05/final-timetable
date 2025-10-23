# Backend Cleanup Plan

**Date**: October 21, 2025  
**Status**: Proposed Changes (Review Before Applying)

---

## 📊 Current Structure Analysis

### Files to KEEP (in root)
```
✅ main.py                          # New FastAPI entrypoint
✅ requirements.txt                 # Dependencies
✅ run_server.py                    # Server startup script
✅ test_integration.py              # Current integration tests
✅ test_modular_solver.py           # Current solver tests
✅ .env                             # Environment variables (if exists)
✅ .gitignore                       # Git configuration (if exists)
```

### Directories to KEEP
```
✅ routes/                          # New route handlers
✅ models/                          # New data models
✅ app/                             # Old app structure (contains solver logic)
```

### Documentation to KEEP (Essential)
```
✅ START_HERE.md                    # Entry point for users
✅ INTEGRATION_GUIDE.md             # Frontend integration
✅ QUICK_REFERENCE.md               # API reference
✅ README_REFACTORED.md             # Main documentation
```

### Files to ARCHIVE (Old/Redundant)
```
📦 CONSTRAINTS_DOCUMENTATION.md     # Duplicate documentation
📦 DEPLOYMENT_READY.md              # Duplicate documentation
📦 FILES_CREATED.md                 # Duplicate documentation
📦 GENERATE_ROUTE_README.md         # Old documentation
📦 IMPLEMENTATION_COMPLETE.md       # Duplicate documentation
📦 QUICKSTART.md                    # Duplicate (keep QUICK_REFERENCE.md)
📦 README.md                        # Old README
📦 README_MODULAR_SOLVER.md         # Duplicate documentation
📦 REFACTORING_COMPLETE.md          # Duplicate documentation
📦 REFACTORING_GUIDE.md             # Duplicate documentation
📦 REFACTORING_SUMMARY.md           # Duplicate documentation
📦 example_generate_request.json    # Example/test data
📦 example_request.json             # Example/test data
📦 example_usage.py                 # Old example
📦 feasible_test.py                 # Old test
📦 feasible_test_output.txt         # Test output
📦 full_test.py                     # Old test
📦 full_test_output.txt             # Test output
📦 quick_test.py                    # Old test
📦 test_constraints.py              # Old test
📦 test_example.py                  # Old test
📦 test_generate_route.py           # Old test
📦 test_output.txt                  # Test output
```

### Cache/Build Artifacts to ARCHIVE
```
📦 app/__pycache__/                 # Python cache
```

---

## 📁 Proposed New Structure

```
backend/
│
├── main.py                         # ✅ FastAPI entrypoint
├── requirements.txt                # ✅ Dependencies
├── run_server.py                   # ✅ Server startup
├── .env                            # ✅ Environment variables
├── .gitignore                      # ✅ Git config
│
├── routes/                         # ✅ New route handlers
│   ├── __init__.py
│   ├── timetable_routes.py
│   ├── department_routes.py
│   ├── room_routes.py
│   └── settings_routes.py
│
├── models/                         # ✅ New data models
│   ├── __init__.py
│   ├── data_models.py
│   ├── timetable_solver.py
│   ├── constraints.py
│   └── utils.py
│
├── app/                            # ✅ Old app (contains solver logic)
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── modular_solver.py
│   ├── solver.py
│   ├── utils.py
│   └── validator.py
│
├── tests/                          # ✅ Current tests
│   ├── test_integration.py
│   └── test_modular_solver.py
│
├── docs/                           # ✅ Essential documentation
│   ├── START_HERE.md
│   ├── INTEGRATION_GUIDE.md
│   ├── QUICK_REFERENCE.md
│   └── README_REFACTORED.md
│
└── archive/                        # 📦 Old/redundant files
    ├── documentation/
    │   ├── CONSTRAINTS_DOCUMENTATION.md
    │   ├── DEPLOYMENT_READY.md
    │   ├── FILES_CREATED.md
    │   ├── GENERATE_ROUTE_README.md
    │   ├── IMPLEMENTATION_COMPLETE.md
    │   ├── QUICKSTART.md
    │   ├── README.md
    │   ├── README_MODULAR_SOLVER.md
    │   ├── REFACTORING_COMPLETE.md
    │   ├── REFACTORING_GUIDE.md
    │   └── REFACTORING_SUMMARY.md
    │
    ├── old_tests/
    │   ├── example_usage.py
    │   ├── feasible_test.py
    │   ├── feasible_test_output.txt
    │   ├── full_test.py
    │   ├── full_test_output.txt
    │   ├── quick_test.py
    │   ├── test_constraints.py
    │   ├── test_example.py
    │   ├── test_generate_route.py
    │   └── test_output.txt
    │
    ├── example_data/
    │   ├── example_generate_request.json
    │   └── example_request.json
    │
    └── cache/
        └── app__pycache__/
            └── (all .pyc files)
```

---

## 📊 Summary of Changes

### Files to Keep (in root): 6
- main.py
- requirements.txt
- run_server.py
- test_integration.py
- test_modular_solver.py
- .env, .gitignore (if exist)

### Directories to Keep: 3
- routes/
- models/
- app/

### Documentation to Keep: 4
- START_HERE.md
- INTEGRATION_GUIDE.md
- QUICK_REFERENCE.md
- README_REFACTORED.md

### Files to Archive: 30+
- 11 documentation files (duplicates)
- 10 old test files
- 3 test output files
- 2 example JSON files
- 1 example Python file
- 1 __pycache__ directory

---

## ✅ Benefits of Cleanup

1. **Cleaner Root Directory** - Only essential files visible
2. **Better Organization** - Tests and docs in dedicated folders
3. **Easier Maintenance** - Clear structure for new developers
4. **No Data Loss** - Everything archived, nothing deleted
5. **Faster Navigation** - Less clutter to sort through

---

## ⚠️ Important Notes

- **No files are deleted** - All moved to archive/
- **App still works** - All imports remain valid
- **Easy recovery** - Archive folder contains everything
- **Documentation preserved** - All docs available in archive/

---

## 🎯 Next Steps

1. Review this plan
2. Approve the changes
3. Execute the cleanup
4. Verify app still runs: `python main.py`
5. Verify tests still work: `python test_integration.py`

---

**Status**: ⏳ Awaiting Approval  
**Estimated Time**: 2 minutes to execute

Ready to proceed? Reply with "yes" to apply these changes.
