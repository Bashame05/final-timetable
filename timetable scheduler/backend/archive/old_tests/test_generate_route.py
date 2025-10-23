"""
Test script for the new /api/timetable/generate route
"""
import requests
import json

def test_generate_route():
    """Test the new timetable generation route"""
    
    # Test data - expanded version with more teachers and subjects
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
    
    # Test the route
    try:
        print("Testing /api/timetable/generate route...")
        print("Sending request with test data...")
        
        response = requests.post(
            "http://localhost:8000/api/timetable/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Response:")
            print(json.dumps(result, indent=2))
            
            if result.get("status") == "success":
                print(f"\n✅ Success! Generated {result.get('total_assignments', 0)} assignments")
                for assignment in result.get("timetable", []):
                    print(f"  - {assignment['subject']} by {assignment['teacher']} in {assignment['room']} at {assignment['start_slot']}")
            else:
                print(f"❌ Failed: {result.get('reason', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_generate_route()

