"""
Test with Physics (type: theory+lab) to verify fix
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from solver.solver_relaxed import solve_relaxed

week_config = {
    "week_start_time": "09:00",
    "week_end_time": "16:00",
    "lunch_start": "13:00",
    "lunch_end": "14:00",
    "working_days": ["Mon", "Tue", "Wed", "Thu", "Fri"]
}

rooms = [
    {"name": "C14", "type": "classroom", "capacity": 60, "location": "Block A"},
    {"name": "C15", "type": "classroom", "capacity": 60, "location": "Block A"},
    {"name": "L1", "type": "lab", "capacity": 30, "location": "Block B"},
]

# Exact data from your appState
subjects = [
    {
        "name": "Maths 1",
        "type": "theory",
        "hours_per_week": 3
    },
    {
        "name": "Chemistry 1",
        "type": "theory",
        "hours_per_week": 3
    },
    {
        "name": "Physics 1",
        "type": "theory+lab",  # This is what frontend sends
        "hours_per_week": 5  # 3 theory + 2 practical
    },
]

print("=" * 70)
print("TESTING WITH PHYSICS (theory+lab)")
print("=" * 70)
print(f"\nSubjects:")
for s in subjects:
    print(f"  - {s['name']}: {s['hours_per_week']}h ({s['type']})")

print(f"\nTotal hours: {sum(s['hours_per_week'] for s in subjects)}h")
print(f"Available slots: 30 (5 days × 6 hours/day)")

print("\n" + "=" * 70)
print("RUNNING SOLVER...")
print("=" * 70)

result = solve_relaxed(
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
    print(f"Total slots: {result['stats']['total_slots']}")
    print(f"Total hours: {result['stats']['total_hours']}h")
    print(f"Subjects: {result['stats']['subjects_scheduled']}")
    
    print("\n" + "-" * 70)
    print("TIMETABLE:")
    print("-" * 70)
    
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
    
    print("\n" + "-" * 70)
    print("VERIFICATION:")
    print("-" * 70)
    
    subject_hours = {}
    for slot in result['timetable']:
        subject = slot['subject']
        if subject not in subject_hours:
            subject_hours[subject] = 0
        subject_hours[subject] += slot['duration']
    
    print(f"\n✅ Hours per subject:")
    for s in subjects:
        required = s['hours_per_week']
        scheduled = subject_hours.get(s['name'], 0)
        status = "✅" if scheduled == required else "❌"
        print(f"  {status} {s['name']:20} Required: {required}h, Scheduled: {scheduled}h")
    
else:
    print(f"\n❌ FAILED!")
    print(f"Status: {result['status']}")
    print(f"Reason: {result.get('reason', 'Unknown')}")

print("\n" + "=" * 70)
