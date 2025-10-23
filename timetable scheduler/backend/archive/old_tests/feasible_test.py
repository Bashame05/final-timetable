import requests
import json

# Feasible test data - reduced subjects to fit in available time
data = {
    "teachers": [
        {
            "id": "T1",
            "name": "Dr. Smith",
            "available_slots": ["Mon_9", "Mon_10", "Mon_11", "Tue_9", "Tue_10", "Wed_9", "Wed_10"],
            "subjects": ["OS", "DBMS"]
        },
        {
            "id": "T2",
            "name": "Dr. Brown",
            "available_slots": ["Mon_9", "Mon_10", "Mon_11", "Tue_9", "Tue_10", "Wed_9", "Wed_10"],
            "subjects": ["Lab"]
        },
        {
            "id": "T3",
            "name": "Prof. Johnson",
            "available_slots": ["Mon_2", "Mon_3", "Tue_2", "Tue_3", "Wed_2", "Wed_3"],
            "subjects": ["ML", "AI"]
        },
        {
            "id": "T4",
            "name": "Dr. Wilson",
            "available_slots": ["Mon_2", "Mon_3", "Tue_2", "Tue_3", "Wed_2", "Wed_3"],
            "subjects": ["CN"]
        }
    ],
    "subjects": [
        {"id": "OS", "name": "Operating Systems", "type": "theory", "duration": 2, "teachers": ["T1"]},
        {"id": "DBMS", "name": "Database Management Systems", "type": "theory", "duration": 2, "teachers": ["T1"]},
        {"id": "Lab", "name": "Programming Lab", "type": "practical", "duration": 2, "teachers": ["T2"]},
        {"id": "ML", "name": "Machine Learning", "type": "theory", "duration": 2, "teachers": ["T3"]},
        {"id": "AI", "name": "Artificial Intelligence", "type": "theory", "duration": 1, "teachers": ["T3"]},
        {"id": "CN", "name": "Computer Networks", "type": "theory", "duration": 2, "teachers": ["T4"]}
    ],
    "rooms": [
        {
            "id": "C301",
            "name": "Classroom 301",
            "type": "classroom",
            "available_slots": ["Mon_9", "Mon_10", "Mon_11", "Mon_2", "Mon_3", "Tue_9", "Tue_10", "Tue_11", "Tue_2", "Tue_3", "Wed_9", "Wed_10", "Wed_11", "Wed_2", "Wed_3"]
        },
        {
            "id": "C302",
            "name": "Classroom 302",
            "type": "classroom",
            "available_slots": ["Mon_9", "Mon_10", "Mon_11", "Mon_2", "Mon_3", "Tue_9", "Tue_10", "Tue_11", "Tue_2", "Tue_3", "Wed_9", "Wed_10", "Wed_11", "Wed_2", "Wed_3"]
        },
        {
            "id": "Lab1",
            "name": "Computer Lab 1",
            "type": "lab",
            "available_slots": ["Mon_9", "Mon_10", "Mon_11", "Mon_2", "Mon_3", "Tue_9", "Tue_10", "Tue_11", "Tue_2", "Tue_3", "Wed_9", "Wed_10", "Wed_11", "Wed_2", "Wed_3"]
        }
    ],
    "batches": [
        {
            "id": "B1",
            "name": "TY CSE A",
            "subjects": ["OS", "DBMS", "Lab", "ML", "AI", "CN"]
        }
    ],
    "days": ["Mon", "Tue", "Wed"],
    "time_slots": ["9", "10", "11", "12", "1", "2", "3"]
}

# Total hours: 2+2+2+2+1+2 = 11 hours
# Available: 3 days × 5 slots = 15 slots ✓ Feasible

response = requests.post("http://localhost:8000/api/timetable/generate", json=data)
result = response.json()

with open("feasible_test_output.txt", "w") as f:
    f.write(json.dumps(result, indent=2))

print(f"Status: {result.get('status')}")
if result.get('status') == 'success':
    print(f"✅ Total assignments: {result.get('total_assignments')}")
    print("\nTimetable:")
    for item in result.get('timetable', []):
        print(f"  {item['subject']:30} | {item['teacher']:20} | {item['room']:20} | {item['start_slot']}-{item['end_slot']}")
else:
    print(f"❌ Reason: {result.get('reason')}")
    print(f"Details: {result.get('details')}")
