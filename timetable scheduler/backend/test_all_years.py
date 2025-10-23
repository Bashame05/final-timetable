"""
Test timetable generation for all years (Year 2, 3, 4) with their respective subjects
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
    {"name": "C16", "type": "classroom", "capacity": 60, "location": "Block A"},
    {"name": "L10", "type": "lab", "capacity": 30, "location": "Block B"},
    {"name": "L11", "type": "lab", "capacity": 30, "location": "Block B"},
    {"name": "L12", "type": "lab", "capacity": 30, "location": "Block B"},
]

# Year 2 Subjects (10 subjects)
year2_subjects = [
    {"name": "Data Structures", "type": "theory", "hours_per_week": 3},
    {"name": "Database Management", "type": "theory", "hours_per_week": 3},
    {"name": "Computer Networks", "type": "theory", "hours_per_week": 3},
    {"name": "Operating Systems", "type": "theory", "hours_per_week": 3},
    {"name": "Web Development", "type": "theory+lab", "hours_per_week": 5},
    {"name": "Software Engineering", "type": "theory", "hours_per_week": 3},
    {"name": "Digital Electronics", "type": "theory+lab", "hours_per_week": 4},
    {"name": "Microprocessors", "type": "theory", "hours_per_week": 2},
    {"name": "Probability & Statistics", "type": "theory", "hours_per_week": 3},
    {"name": "Discrete Mathematics", "type": "theory", "hours_per_week": 2},
]

# Year 3 Subjects (5 subjects)
year3_subjects = [
    {"name": "Machine Learning", "type": "theory+lab", "hours_per_week": 5},
    {"name": "Compiler Design", "type": "theory", "hours_per_week": 3},
    {"name": "Computer Graphics", "type": "theory+lab", "hours_per_week": 4},
    {"name": "Artificial Intelligence", "type": "theory", "hours_per_week": 3},
    {"name": "Cloud Computing", "type": "theory", "hours_per_week": 3},
]

# Year 4 Subjects (5 subjects)
year4_subjects = [
    {"name": "Deep Learning", "type": "theory+lab", "hours_per_week": 5},
    {"name": "Blockchain Technology", "type": "theory", "hours_per_week": 3},
    {"name": "IoT Systems", "type": "theory+lab", "hours_per_week": 4},
    {"name": "Cybersecurity", "type": "theory", "hours_per_week": 3},
    {"name": "Big Data Analytics", "type": "theory+lab", "hours_per_week": 4},
]

def test_year(year_num, subjects):
    """Test timetable generation for a specific year"""
    print("\n" + "=" * 70)
    print(f"TESTING YEAR {year_num}")
    print("=" * 70)
    
    print(f"\nSubjects ({len(subjects)} total):")
    total_hours = 0
    for s in subjects:
        hours = s['hours_per_week']
        total_hours += hours
        print(f"  - {s['name']:30} {hours}h ({s['type']})")
    
    print(f"\nTotal hours: {total_hours}h")
    print(f"Available slots: 30 (5 days × 6 hours/day)")
    print(f"Utilization: {(total_hours/30)*100:.1f}%")
    
    print("\n" + "-" * 70)
    print("RUNNING SOLVER...")
    print("-" * 70)
    
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
                    print(f"  {slot['start_time']}-{slot['end_time']} | {slot['subject']:30} | {slot['room']:5} | {slot['type']}")
        
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
        all_correct = True
        for s in subjects:
            required = s['hours_per_week']
            scheduled = subject_hours.get(s['name'], 0)
            status = "✅" if scheduled == required else "❌"
            if scheduled != required:
                all_correct = False
            print(f"  {status} {s['name']:30} Required: {required}h, Scheduled: {scheduled}h")
        
        # Check room types
        print(f"\n✅ Room type verification:")
        room_errors = []
        for slot in result['timetable']:
            room_type = next((r['type'] for r in rooms if r['name'] == slot['room']), None)
            subject_type = slot['type']
            
            if subject_type == 'theory' and room_type == 'lab':
                room_errors.append(f"❌ {slot['subject']} (theory) in {slot['room']} (lab)")
            elif subject_type == 'practical' and room_type == 'classroom':
                room_errors.append(f"❌ {slot['subject']} (practical) in {slot['room']} (classroom)")
        
        if room_errors:
            for error in room_errors:
                print(f"  {error}")
        else:
            print(f"  ✅ All subjects in correct room types")
        
        return all_correct and len(room_errors) == 0
        
    else:
        print(f"\n❌ FAILED!")
        print(f"Status: {result['status']}")
        print(f"Reason: {result.get('reason', 'Unknown')}")
        return False

# Run tests
print("\n" + "=" * 70)
print("TIMETABLE GENERATION TEST - ALL YEARS")
print("=" * 70)

results = {}
results['Year 2'] = test_year(2, year2_subjects)
results['Year 3'] = test_year(3, year3_subjects)
results['Year 4'] = test_year(4, year4_subjects)

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

for year, success in results.items():
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{year}: {status}")

all_pass = all(results.values())
print("\n" + "=" * 70)
if all_pass:
    print("🎉 ALL TESTS PASSED! 🎉")
else:
    print("⚠️  SOME TESTS FAILED")
print("=" * 70)
