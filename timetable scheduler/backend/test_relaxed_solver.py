"""
Test the relaxed solver with one-hour slots
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from solver.solver_relaxed import solve_relaxed

# Test data - one hour slots
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

# Subjects with exact hour requirements
subjects = [
    {
        "name": "Maths 1",
        "type": "theory",
        "theory_hours": 3,
        "practical_hours": 0
    },
    {
        "name": "Physics 1",
        "type": "theory",
        "theory_hours": 3,
        "practical_hours": 0
    },
    {
        "name": "Chemistry 1",
        "type": "practical",
        "theory_hours": 0,
        "practical_hours": 2
    },
    {
        "name": "Programming",
        "type": "both",
        "theory_hours": 3,
        "practical_hours": 2
    },
]

print("=" * 70)
print("TESTING RELAXED SOLVER (One-Hour Slots)")
print("=" * 70)
print(f"\nWeek Config: {week_config}")
print(f"Rooms: {len(rooms)} rooms")
print(f"Subjects: {len(subjects)} subjects")

total_hours = sum(s.get('theory_hours', 0) + s.get('practical_hours', 0) for s in subjects)
print(f"Total hours needed: {total_hours}h")
print(f"Available slots: 5 days × 6 hours/day (excluding lunch) = 30 slots")

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
    print(f"Status: {result['status']}")
    print(f"Total slots generated: {result['stats']['total_slots']}")
    print(f"Total hours scheduled: {result['stats']['total_hours']}h")
    print(f"Subjects scheduled: {result['stats']['subjects_scheduled']}")
    print(f"Rooms used: {result['stats']['rooms_used']}")
    
    print("\n" + "-" * 70)
    print("TIMETABLE SLOTS (One-Hour Each):")
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
    
    # Verify constraints
    print("\n" + "-" * 70)
    print("CONSTRAINT VERIFICATION:")
    print("-" * 70)
    
    # Check no room overlaps
    room_times = {}
    overlaps = 0
    for slot in result['timetable']:
        key = (slot['day'], slot['start_hour'], slot['room'])
        if key in room_times:
            overlaps += 1
        room_times[key] = slot
    
    print(f"✅ Room overlaps: {overlaps} (should be 0)")
    
    # Check hours per subject
    subject_hours = {}
    for slot in result['timetable']:
        subject = slot['subject']
        if subject not in subject_hours:
            subject_hours[subject] = 0
        subject_hours[subject] += slot['duration']
    
    print(f"\n✅ Hours per subject:")
    for subject in subjects:
        required = subject.get('theory_hours', 0) + subject.get('practical_hours', 0)
        scheduled = subject_hours.get(subject['name'], 0)
        status = "✅" if scheduled == required else "❌"
        print(f"  {status} {subject['name']:20} Required: {required}h, Scheduled: {scheduled}h")
    
else:
    print(f"\n❌ FAILED!")
    print(f"Status: {result['status']}")
    print(f"Reason: {result.get('reason', 'Unknown')}")

print("\n" + "=" * 70)
