"""
Integration test script for the refactored backend
Tests all API endpoints with sample data
"""
import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
END = "\033[0m"


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{END}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{GREEN}✅ {text}{END}")


def print_error(text: str):
    """Print error message"""
    print(f"{RED}❌ {text}{END}")


def print_info(text: str):
    """Print info message"""
    print(f"{YELLOW}ℹ️  {text}{END}")


def test_health_check():
    """Test health check endpoint"""
    print_header("Testing Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_success("Health check passed")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Connection error: {str(e)}")
        return False


def test_settings():
    """Test settings endpoints"""
    print_header("Testing Settings Management")
    
    # Set week config
    print_info("Setting week configuration...")
    week_config = {
        "week_start_time": "09:00",
        "week_end_time": "16:00",
        "lunch_start": "13:00",
        "lunch_end": "14:00",
        "working_days": ["Mon", "Tue", "Wed", "Thu", "Fri"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/settings/week-config",
        json=week_config
    )
    
    if response.status_code == 200:
        print_success("Week configuration set")
    else:
        print_error(f"Failed to set week config: {response.status_code}")
        return False
    
    # Get week config
    print_info("Getting week configuration...")
    response = requests.get(f"{BASE_URL}/api/settings/week-config")
    
    if response.status_code == 200:
        print_success("Week configuration retrieved")
    else:
        print_error(f"Failed to get week config: {response.status_code}")
        return False
    
    return True


def test_departments():
    """Test department endpoints"""
    print_header("Testing Department Management")
    
    # Create department
    print_info("Creating department...")
    dept_data = {
        "department_name": "Computer Engineering",
        "subjects": [
            {"name": "DBMS", "type": "theory+lab", "hours_per_week": 3},
            {"name": "CN", "type": "theory", "hours_per_week": 3},
            {"name": "OS", "type": "theory", "hours_per_week": 2}
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/departments/",
        json=dept_data
    )
    
    if response.status_code == 200:
        print_success("Department created")
    else:
        print_error(f"Failed to create department: {response.status_code}")
        print(response.text)
        return False
    
    # List departments
    print_info("Listing departments...")
    response = requests.get(f"{BASE_URL}/api/departments/")
    
    if response.status_code == 200:
        print_success("Departments listed")
        data = response.json()
        print(f"Total departments: {data.get('count', 0)}")
    else:
        print_error(f"Failed to list departments: {response.status_code}")
        return False
    
    # Get specific department
    print_info("Getting department details...")
    response = requests.get(f"{BASE_URL}/api/departments/Computer Engineering")
    
    if response.status_code == 200:
        print_success("Department retrieved")
    else:
        print_error(f"Failed to get department: {response.status_code}")
        return False
    
    return True


def test_rooms():
    """Test room endpoints"""
    print_header("Testing Room Management")
    
    # Create rooms
    print_info("Creating rooms...")
    rooms_data = {
        "rooms": [
            {
                "name": "Room 101",
                "type": "classroom",
                "capacity": 60,
                "location": "Building A"
            },
            {
                "name": "Room 102",
                "type": "classroom",
                "capacity": 50,
                "location": "Building A"
            },
            {
                "name": "CS Lab 1",
                "type": "lab",
                "capacity": 30,
                "location": "Building C",
                "for_subject": "DBMS"
            },
            {
                "name": "CS Lab 2",
                "type": "lab",
                "capacity": 25,
                "location": "Building C"
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/rooms/",
        json=rooms_data
    )
    
    if response.status_code == 200:
        print_success("Rooms created")
    else:
        print_error(f"Failed to create rooms: {response.status_code}")
        print(response.text)
        return False
    
    # List all rooms
    print_info("Listing all rooms...")
    response = requests.get(f"{BASE_URL}/api/rooms/")
    
    if response.status_code == 200:
        print_success("Rooms listed")
        data = response.json()
        print(f"Total rooms: {data.get('count', 0)}")
        print(f"Classrooms: {data.get('classrooms_count', 0)}")
        print(f"Labs: {data.get('labs_count', 0)}")
    else:
        print_error(f"Failed to list rooms: {response.status_code}")
        return False
    
    # Get rooms by type
    print_info("Getting classrooms...")
    response = requests.get(f"{BASE_URL}/api/rooms/type/classroom")
    
    if response.status_code == 200:
        print_success("Classrooms retrieved")
    else:
        print_error(f"Failed to get classrooms: {response.status_code}")
        return False
    
    return True


def test_timetable_generation():
    """Test timetable generation"""
    print_header("Testing Timetable Generation")
    
    print_info("Generating timetable...")
    
    timetable_request = {
        "department": "Computer Engineering",
        "week_config": {
            "week_start_time": "09:00",
            "week_end_time": "16:00",
            "lunch_start": "13:00",
            "lunch_end": "14:00",
            "working_days": ["Mon", "Tue", "Wed", "Thu", "Fri"]
        },
        "rooms": [
            {
                "name": "Room 101",
                "type": "classroom",
                "capacity": 60,
                "location": "Building A"
            },
            {
                "name": "Room 102",
                "type": "classroom",
                "capacity": 50,
                "location": "Building A"
            },
            {
                "name": "CS Lab 1",
                "type": "lab",
                "capacity": 30,
                "location": "Building C",
                "for_subject": "DBMS"
            }
        ],
        "subjects": [
            {"name": "DBMS", "type": "theory+lab", "hours_per_week": 3},
            {"name": "CN", "type": "theory", "hours_per_week": 3},
            {"name": "OS", "type": "theory", "hours_per_week": 2}
        ],
        "special_sessions": {}
    }
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/api/timetable/generate",
        json=timetable_request
    )
    elapsed_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get("status") == "success":
            print_success(f"Timetable generated in {elapsed_time:.2f}s")
            print(f"Total slots: {len(data.get('timetable', []))}")
            
            # Display timetable
            print("\nGenerated Timetable:")
            print("-" * 80)
            for slot in data.get("timetable", [])[:5]:  # Show first 5 slots
                print(f"  {slot['day']} | {slot['slot']} | {slot['subject']} | {slot['room']} | {slot['type']}")
            
            if len(data.get("timetable", [])) > 5:
                print(f"  ... and {len(data.get('timetable', [])) - 5} more slots")
            
            return True
        else:
            print_error(f"Timetable generation failed: {data.get('message')}")
            if data.get("conflicts"):
                print("Conflicts:")
                for conflict in data.get("conflicts", []):
                    print(f"  - {conflict.get('reason')}")
            return False
    else:
        print_error(f"Request failed: {response.status_code}")
        print(response.text)
        return False


def test_validation():
    """Test timetable validation"""
    print_header("Testing Timetable Validation")
    
    print_info("Validating timetable request...")
    
    timetable_request = {
        "department": "Computer Engineering",
        "week_config": {
            "week_start_time": "09:00",
            "week_end_time": "16:00",
            "lunch_start": "13:00",
            "lunch_end": "14:00",
            "working_days": ["Mon", "Tue", "Wed", "Thu", "Fri"]
        },
        "rooms": [
            {
                "name": "Room 101",
                "type": "classroom",
                "capacity": 60,
                "location": "Building A"
            }
        ],
        "subjects": [
            {"name": "DBMS", "type": "theory+lab", "hours_per_week": 3}
        ],
        "special_sessions": {}
    }
    
    response = requests.post(
        f"{BASE_URL}/api/timetable/validate",
        json=timetable_request
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get("valid"):
            print_success("Request is valid")
        else:
            print_error(f"Request is invalid: {data.get('message')}")
        return True
    else:
        print_error(f"Validation failed: {response.status_code}")
        return False


def run_all_tests():
    """Run all integration tests"""
    print(f"\n{BLUE}{'='*60}")
    print("AI TIMETABLE SCHEDULER - INTEGRATION TEST SUITE")
    print(f"{'='*60}{END}\n")
    
    tests = [
        ("Health Check", test_health_check),
        ("Settings Management", test_settings),
        ("Department Management", test_departments),
        ("Room Management", test_rooms),
        ("Timetable Validation", test_validation),
        ("Timetable Generation", test_timetable_generation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{GREEN}PASSED{END}" if result else f"{RED}FAILED{END}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{BLUE}Total: {passed}/{total} tests passed{END}\n")
    
    if passed == total:
        print_success("All tests passed! Backend is ready for integration.")
    else:
        print_error(f"{total - passed} test(s) failed. Check the errors above.")


if __name__ == "__main__":
    print_info("Make sure the backend is running: python main.py")
    print_info("Starting integration tests...\n")
    
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
