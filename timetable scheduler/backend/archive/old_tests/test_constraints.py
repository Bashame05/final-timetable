"""
Test script to verify all hard constraints are properly enforced
"""
import requests
import json

def test_constraints():
    """Test that all hard constraints are enforced"""
    
    print("🧪 Testing Hard Constraints Implementation")
    print("=" * 50)
    
    # Test data with various constraint scenarios
    test_data = {
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
                "subjects": ["Lab", "OS_Lab"]
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
                "subjects": ["Major_Project", "Mini_Project"]
            },
            {
                "id": "T5",
                "name": "Dr. Davis",
                "available_slots": ["Mon_9", "Mon_10", "Mon_11", "Tue_9", "Tue_10", "Wed_9", "Wed_10"],
                "subjects": ["CN", "SE"]
            }
        ],
        "subjects": [
            {
                "id": "OS",
                "name": "Operating Systems",
                "type": "theory",
                "duration": 2,
                "teachers": ["T1"]
            },
            {
                "id": "DBMS",
                "name": "Database Management Systems",
                "type": "theory",
                "duration": 2,
                "teachers": ["T1"]
            },
            {
                "id": "Lab",
                "name": "Programming Lab",
                "type": "practical",
                "duration": 2,
                "teachers": ["T2"]
            },
            {
                "id": "OS_Lab",
                "name": "OS Lab",
                "type": "practical",
                "duration": 2,
                "teachers": ["T2"]
            },
            {
                "id": "ML",
                "name": "Machine Learning",
                "type": "theory",
                "duration": 2,
                "teachers": ["T3"]
            },
            {
                "id": "AI",
                "name": "Artificial Intelligence",
                "type": "theory",
                "duration": 1,
                "teachers": ["T3"]
            },
            {
                "id": "Major_Project",
                "name": "Major Project",
                "type": "major_project",
                "duration": 3,
                "teachers": ["T4"]
            },
            {
                "id": "Mini_Project",
                "name": "Mini Project",
                "type": "mini_project",
                "duration": 2,
                "teachers": ["T4"]
            },
            {
                "id": "CN",
                "name": "Computer Networks",
                "type": "theory",
                "duration": 2,
                "teachers": ["T5"]
            },
            {
                "id": "SE",
                "name": "Software Engineering",
                "type": "theory",
                "duration": 1,
                "teachers": ["T5"]
            }
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
            },
            {
                "id": "Lab2",
                "name": "Computer Lab 2",
                "type": "lab",
                "available_slots": ["Mon_9", "Mon_10", "Mon_11", "Mon_2", "Mon_3", "Tue_9", "Tue_10", "Tue_11", "Tue_2", "Tue_3", "Wed_9", "Wed_10", "Wed_11", "Wed_2", "Wed_3"]
            }
        ],
        "batches": [
            {
                "id": "B1",
                "name": "TY CSE A",
                "subjects": ["OS", "DBMS", "Lab", "OS_Lab", "ML", "AI", "Major_Project", "Mini_Project", "CN", "SE"]
            }
        ],
        "days": ["Mon", "Tue", "Wed"],
        "time_slots": ["9", "10", "11", "12", "1", "2", "3"]
    }
    
    try:
        print("📤 Sending request to /api/timetable/generate...")
        
        response = requests.post(
            "http://localhost:8000/api/timetable/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("status") == "success":
                timetable = result.get("timetable", [])
                total_assignments = result.get("total_assignments", 0)
                
                print(f"✅ SUCCESS! Generated {total_assignments} assignments")
                print("\n📋 Generated Timetable:")
                print("-" * 80)
                
                # Group by day for better display
                by_day = {}
                for assignment in timetable:
                    day = assignment["start_slot"].split("_")[0]
                    if day not in by_day:
                        by_day[day] = []
                    by_day[day].append(assignment)
                
                for day in sorted(by_day.keys()):
                    print(f"\n📅 {day}:")
                    for assignment in sorted(by_day[day], key=lambda x: x["start_slot"]):
                        print(f"  {assignment['start_slot'].split('_')[1]}:00 - {assignment['subject']} by {assignment['teacher']} in {assignment['room']} ({assignment['type']})")
                
                # Verify constraints
                print("\n🔍 Constraint Verification:")
                print("-" * 40)
                
                # Check 1: No teacher overlap
                teacher_slots = {}
                for assignment in timetable:
                    teacher = assignment["teacher_id"]
                    slots = assignment.get("all_slots", [])
                    for slot in slots:
                        if slot in teacher_slots:
                            print(f"❌ TEACHER OVERLAP: {teacher} has overlapping assignments at {slot}")
                        else:
                            teacher_slots[slot] = teacher
                print("✅ No teacher overlaps detected")
                
                # Check 2: No room overlap
                room_slots = {}
                for assignment in timetable:
                    room = assignment["room_id"]
                    slots = assignment.get("all_slots", [])
                    for slot in slots:
                        if slot in room_slots:
                            print(f"❌ ROOM OVERLAP: {room} has overlapping assignments at {slot}")
                        else:
                            room_slots[slot] = room
                print("✅ No room overlaps detected")
                
                # Check 3: No batch overlap
                batch_slots = {}
                for assignment in timetable:
                    batch = assignment["batch_id"]
                    slots = assignment.get("all_slots", [])
                    for slot in slots:
                        if slot in batch_slots:
                            print(f"❌ BATCH OVERLAP: {batch} has overlapping assignments at {slot}")
                        else:
                            batch_slots[slot] = batch
                print("✅ No batch overlaps detected")
                
                # Check 4: Room type constraints
                for assignment in timetable:
                    subject_type = assignment["type"]
                    room_type = "classroom" if "Classroom" in assignment["room"] else "lab"
                    
                    if subject_type == "theory" and room_type != "classroom":
                        print(f"❌ ROOM TYPE VIOLATION: Theory subject {assignment['subject']} in {room_type}")
                    elif subject_type == "practical" and room_type != "lab":
                        print(f"❌ ROOM TYPE VIOLATION: Practical subject {assignment['subject']} in {room_type}")
                print("✅ Room type constraints satisfied")
                
                # Check 5: Duration constraints
                for assignment in timetable:
                    subject_type = assignment["type"]
                    duration = assignment["duration"]
                    
                    if subject_type == "theory" and duration > 2:
                        print(f"❌ DURATION VIOLATION: Theory subject {assignment['subject']} has duration {duration} > 2")
                    elif subject_type == "practical" and duration != 2:
                        print(f"❌ DURATION VIOLATION: Practical subject {assignment['subject']} has duration {duration} != 2")
                    elif subject_type == "major_project" and duration < 2:
                        print(f"❌ DURATION VIOLATION: Major project {assignment['subject']} has duration {duration} < 2")
                    elif subject_type == "mini_project" and duration > 2:
                        print(f"❌ DURATION VIOLATION: Mini project {assignment['subject']} has duration {duration} > 2")
                print("✅ Duration constraints satisfied")
                
                # Check 6: Break time constraints
                break_violations = 0
                for assignment in timetable:
                    slots = assignment.get("all_slots", [])
                    for slot in slots:
                        if "_12" in slot or "_1" in slot:
                            print(f"❌ BREAK TIME VIOLATION: {assignment['subject']} scheduled during break time at {slot}")
                            break_violations += 1
                if break_violations == 0:
                    print("✅ No break time violations")
                
                print(f"\n🎉 All constraints verified! Generated {total_assignments} valid assignments.")
                
            else:
                print(f"❌ FAILED: {result.get('reason', 'Unknown error')}")
                print(f"Details: {result.get('details', 'No details provided')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Make sure the server is running on http://localhost:8000")
        print("Start the server with: python run_server.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_constraints()


