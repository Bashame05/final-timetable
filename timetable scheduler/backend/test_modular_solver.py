"""
Test script for the modular timetable solver
Tests the /api/timetable/generate endpoint with various scenarios
"""
import requests
import json
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"
ENDPOINT = f"{BASE_URL}/api/timetable/generate"


def print_result(result: Dict[str, Any], test_name: str) -> None:
    """Pretty print test results"""
    print("\n" + "=" * 70)
    print(f"TEST: {test_name}")
    print("=" * 70)
    print(f"Status: {result.get('status', 'unknown')}")
    print(f"Message: {result.get('message', 'N/A')}")
    
    if result.get('status') == 'success':
        timetable = result.get('timetable', [])
        print(f"\n✅ Feasible timetable generated with {len(timetable)} assignments:\n")
        
        for i, lecture in enumerate(timetable, 1):
            print(f"{i}. {lecture['subject']} ({lecture['type']})")
            print(f"   Teacher: {lecture['teacher']}")
            print(f"   Room: {lecture['room']} ({lecture.get('room_id', 'N/A')})")
            print(f"   Batch: {lecture['batch']}")
            print(f"   Slot: {lecture['slot']}")
            print(f"   Duration: {lecture['duration']} hour(s)")
            print()
    else:
        print(f"\n❌ Failed to generate timetable")
        print(f"Reason: {result.get('reason', 'unknown')}")
        if 'details' in result:
            print(f"Details: {result['details']}")


def test_simple_case() -> None:
    """Test 1: Simple case - 1 subject, 2 hours, 1 teacher, 1 room, 1 batch"""
    payload = {
        "teachers": [
            {
                "id": "T1",
                "name": "Dr. Smith",
                "subjects": ["OS"],
                "availability": ["Mon_9", "Mon_10", "Tue_9", "Tue_10"]
            }
        ],
        "subjects": [
            {
                "id": "OS",
                "name": "Operating Systems",
                "type": "theory",
                "hours_per_week": 2
            }
        ],
        "rooms": [
            {
                "id": "C301",
                "name": "Classroom 301",
                "type": "classroom",
                "availability": ["Mon_9", "Mon_10", "Tue_9", "Tue_10"]
            }
        ],
        "batches": [
            {
                "id": "B1",
                "name": "TY CSE A",
                "subjects": ["OS"]
            }
        ],
        "timeslots": ["Mon_9", "Mon_10", "Tue_9", "Tue_10"],
        "break_start": "12",
        "break_end": "1"
    }
    
    try:
        response = requests.post(ENDPOINT, json=payload, timeout=120)
        result = response.json()
        print_result(result, "Simple Case (1 subject, 2 hours)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_feasible_complex_case() -> None:
    """Test 2: Complex feasible case - 3 subjects, 6 hours total, 3 teachers, 2 rooms, 1 batch"""
    payload = {
        "teachers": [
            {
                "id": "T1",
                "name": "Dr. Smith",
                "subjects": ["OS", "DBMS"],
                "availability": ["Mon_9", "Mon_10", "Tue_9", "Tue_10", "Wed_9", "Wed_10"]
            },
            {
                "id": "T2",
                "name": "Prof. Johnson",
                "subjects": ["ML"],
                "availability": ["Mon_2", "Mon_3", "Tue_2", "Tue_3", "Wed_2", "Wed_3"]
            },
            {
                "id": "T3",
                "name": "Dr. Brown",
                "subjects": ["Lab"],
                "availability": ["Mon_9", "Mon_10", "Tue_9", "Tue_10"]
            }
        ],
        "subjects": [
            {
                "id": "OS",
                "name": "Operating Systems",
                "type": "theory",
                "hours_per_week": 2
            },
            {
                "id": "DBMS",
                "name": "Database Management",
                "type": "theory",
                "hours_per_week": 2
            },
            {
                "id": "Lab",
                "name": "Programming Lab",
                "type": "practical",
                "hours_per_week": 2
            }
        ],
        "rooms": [
            {
                "id": "C301",
                "name": "Classroom 301",
                "type": "classroom",
                "availability": ["Mon_9", "Mon_10", "Mon_2", "Mon_3", "Tue_9", "Tue_10", "Tue_2", "Tue_3", "Wed_9", "Wed_10", "Wed_2", "Wed_3"]
            },
            {
                "id": "Lab1",
                "name": "Computer Lab 1",
                "type": "lab",
                "availability": ["Mon_9", "Mon_10", "Tue_9", "Tue_10", "Wed_9", "Wed_10"]
            }
        ],
        "batches": [
            {
                "id": "B1",
                "name": "TY CSE A",
                "subjects": ["OS", "DBMS", "Lab"]
            }
        ],
        "timeslots": ["Mon_9", "Mon_10", "Mon_2", "Mon_3", "Tue_9", "Tue_10", "Tue_2", "Tue_3", "Wed_9", "Wed_10", "Wed_2", "Wed_3"],
        "break_start": "12",
        "break_end": "1"
    }
    
    try:
        response = requests.post(ENDPOINT, json=payload, timeout=120)
        result = response.json()
        print_result(result, "Complex Feasible Case (3 subjects, 6 hours)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_infeasible_case() -> None:
    """Test 3: Infeasible case - More hours required than available slots"""
    payload = {
        "teachers": [
            {
                "id": "T1",
                "name": "Dr. Smith",
                "subjects": ["OS", "DBMS", "ML", "AI"],
                "availability": ["Mon_9", "Mon_10", "Tue_9", "Tue_10"]
            }
        ],
        "subjects": [
            {
                "id": "OS",
                "name": "Operating Systems",
                "type": "theory",
                "hours_per_week": 2
            },
            {
                "id": "DBMS",
                "name": "Database Management",
                "type": "theory",
                "hours_per_week": 2
            },
            {
                "id": "ML",
                "name": "Machine Learning",
                "type": "theory",
                "hours_per_week": 2
            },
            {
                "id": "AI",
                "name": "Artificial Intelligence",
                "type": "theory",
                "hours_per_week": 2
            }
        ],
        "rooms": [
            {
                "id": "C301",
                "name": "Classroom 301",
                "type": "classroom",
                "availability": ["Mon_9", "Mon_10", "Tue_9", "Tue_10"]
            }
        ],
        "batches": [
            {
                "id": "B1",
                "name": "TY CSE A",
                "subjects": ["OS", "DBMS", "ML", "AI"]
            }
        ],
        "timeslots": ["Mon_9", "Mon_10", "Tue_9", "Tue_10"],
        "break_start": "12",
        "break_end": "1"
    }
    
    try:
        response = requests.post(ENDPOINT, json=payload, timeout=120)
        result = response.json()
        print_result(result, "Infeasible Case (8 hours required, 4 slots available)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_practical_theory_mix() -> None:
    """Test 4: Mix of theory and practical classes"""
    payload = {
        "teachers": [
            {
                "id": "T1",
                "name": "Dr. Smith",
                "subjects": ["OS"],
                "availability": ["Mon_9", "Mon_10", "Tue_9", "Tue_10", "Wed_9", "Wed_10"]
            },
            {
                "id": "T2",
                "name": "Prof. Johnson",
                "subjects": ["Lab"],
                "availability": ["Mon_2", "Mon_3", "Tue_2", "Tue_3"]
            }
        ],
        "subjects": [
            {
                "id": "OS",
                "name": "Operating Systems",
                "type": "theory",
                "hours_per_week": 2
            },
            {
                "id": "Lab",
                "name": "Programming Lab",
                "type": "practical",
                "hours_per_week": 2
            }
        ],
        "rooms": [
            {
                "id": "C301",
                "name": "Classroom 301",
                "type": "classroom",
                "availability": ["Mon_9", "Mon_10", "Tue_9", "Tue_10", "Wed_9", "Wed_10"]
            },
            {
                "id": "Lab1",
                "name": "Computer Lab 1",
                "type": "lab",
                "availability": ["Mon_2", "Mon_3", "Tue_2", "Tue_3", "Wed_2", "Wed_3"]
            }
        ],
        "batches": [
            {
                "id": "B1",
                "name": "TY CSE A",
                "subjects": ["OS", "Lab"]
            }
        ],
        "timeslots": ["Mon_9", "Mon_10", "Mon_2", "Mon_3", "Tue_9", "Tue_10", "Tue_2", "Tue_3", "Wed_9", "Wed_10", "Wed_2", "Wed_3"],
        "break_start": "12",
        "break_end": "1"
    }
    
    try:
        response = requests.post(ENDPOINT, json=payload, timeout=120)
        result = response.json()
        print_result(result, "Theory + Practical Mix (2 theory + 2 practical hours)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def run_all_tests() -> None:
    """Run all test cases"""
    print("\n" + "=" * 70)
    print("MODULAR TIMETABLE SOLVER - TEST SUITE")
    print("=" * 70)
    print("Make sure the server is running: python run_server.py")
    print("=" * 70)
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running\n")
        else:
            print("❌ Server is not responding correctly")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:8000")
        return
    
    # Run tests
    test_simple_case()
    test_feasible_complex_case()
    test_practical_theory_mix()
    test_infeasible_case()
    
    print("\n" + "=" * 70)
    print("TEST SUITE COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()
