"""
Direct test of the solver without running the server
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from solver.solver_simple import solve_simple

# Test data
week_config = {
    "week_start_time": "09:00",
    "week_end_time": "16:00",
    "lunch_start": "13:00",
    "lunch_end": "14:00",
    "working_days": ["Mon", "Tue", "Wed", "Thu", "Fri"]
}

rooms = [
    {"name": "C1", "type": "classroom", "capacity": 60},
    {"name": "C2", "type": "classroom", "capacity": 60},
    {"name": "C3", "type": "classroom", "capacity": 60},
    {"name": "L1", "type": "lab", "capacity": 30},
    {"name": "L2", "type": "lab", "capacity": 30},
]

subjects = [
    {"name": "Maths 1", "type": "theory", "hours_per_week": 3},
    {"name": "Physics 1", "type": "theory", "hours_per_week": 3},
    {"name": "Chemistry 1", "type": "practical", "hours_per_week": 2},
    {"name": "Programming", "type": "both", "hours_per_week": 5},
]

print("=" * 70)
print("TESTING SOLVER DIRECTLY")
print("=" * 70)
print(f"\nWeek Config: {week_config}")
print(f"Rooms: {len(rooms)} rooms")
print(f"Subjects: {len(subjects)} subjects")
print(f"Total hours needed: {sum(s['hours_per_week'] for s in subjects)}h")

print("\n" + "=" * 70)
print("RUNNING SOLVER...")
print("=" * 70)

result = solve_simple(
    week_config=week_config,
    subjects=subjects,
    rooms=rooms,
    batches=["Batch A"]
)

print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)

if result["status"] == "success":
    print(f"\n✅ SUCCESS!")
    print(f"Status: {result['status']}")
    print(f"Total slots generated: {result['stats']['total_slots']}")
    print(f"Subjects scheduled: {result['stats']['subjects_scheduled']}")
    print(f"Rooms used: {result['stats']['rooms_used']}")
    
    print("\n" + "-" * 70)
    print("TIMETABLE SLOTS:")
    print("-" * 70)
    
    # Group by day
    by_day = {}
    for slot in result['timetable']:
        day = slot['day']
        if day not in by_day:
            by_day[day] = []
        by_day[day].append(slot)
    
    day_order = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    for day in day_order:
        if day in by_day:
            print(f"\n{day}:")
            for slot in sorted(by_day[day], key=lambda x: x['start_hour']):
                print(f"  {slot['start_time']}-{slot['end_time']} | {slot['subject']:20} | {slot['room']:5} | {slot['type']}")
else:
    print(f"\n❌ FAILED!")
    print(f"Status: {result['status']}")
    print(f"Reason: {result.get('reason', 'Unknown')}")

print("\n" + "=" * 70)
