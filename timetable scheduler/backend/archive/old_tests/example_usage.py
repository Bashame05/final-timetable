"""
Example usage of the modular timetable solver
Shows how to use the solver both directly and via the API
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from modular_solver import generate_timetable
import json


def example_1_simple():
    """Example 1: Simple timetable - 1 subject, 2 hours"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Simple Timetable (1 subject, 2 hours)")
    print("=" * 70)
    
    result = generate_timetable(
        teachers=[
            {
                "id": "T1",
                "name": "Dr. Smith",
                "subjects": ["OS"],
                "availability": ["Mon_9", "Mon_10", "Tue_9", "Tue_10"]
            }
        ],
        subjects=[
            {
                "id": "OS",
                "name": "Operating Systems",
                "type": "theory",
                "hours_per_week": 2
            }
        ],
        rooms=[
            {
                "id": "C301",
                "name": "Classroom 301",
                "type": "classroom",
                "availability": ["Mon_9", "Mon_10", "Tue_9", "Tue_10"]
            }
        ],
        batches=[
            {
                "id": "B1",
                "name": "TY CSE A",
                "subjects": ["OS"]
            }
        ],
        timeslots=["Mon_9", "Mon_10", "Tue_9", "Tue_10"],
        break_start="12",
        break_end="1"
    )
    
    print(json.dumps(result, indent=2))


def example_2_complex():
    """Example 2: Complex timetable - 3 subjects, 6 hours, multiple teachers/rooms"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Complex Timetable (3 subjects, 6 hours)")
    print("=" * 70)
    
    result = generate_timetable(
        teachers=[
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
        subjects=[
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
        rooms=[
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
        batches=[
            {
                "id": "B1",
                "name": "TY CSE A",
                "subjects": ["OS", "DBMS", "Lab"]
            }
        ],
        timeslots=["Mon_9", "Mon_10", "Mon_2", "Mon_3", "Tue_9", "Tue_10", "Tue_2", "Tue_3", "Wed_9", "Wed_10", "Wed_2", "Wed_3"],
        break_start="12",
        break_end="1"
    )
    
    print(json.dumps(result, indent=2))


def example_3_infeasible():
    """Example 3: Infeasible case - more hours required than available"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Infeasible Case (8 hours required, 4 slots available)")
    print("=" * 70)
    
    result = generate_timetable(
        teachers=[
            {
                "id": "T1",
                "name": "Dr. Smith",
                "subjects": ["OS", "DBMS", "ML", "AI"],
                "availability": ["Mon_9", "Mon_10", "Tue_9", "Tue_10"]
            }
        ],
        subjects=[
            {"id": "OS", "name": "Operating Systems", "type": "theory", "hours_per_week": 2},
            {"id": "DBMS", "name": "Database Management", "type": "theory", "hours_per_week": 2},
            {"id": "ML", "name": "Machine Learning", "type": "theory", "hours_per_week": 2},
            {"id": "AI", "name": "Artificial Intelligence", "type": "theory", "hours_per_week": 2}
        ],
        rooms=[
            {
                "id": "C301",
                "name": "Classroom 301",
                "type": "classroom",
                "availability": ["Mon_9", "Mon_10", "Tue_9", "Tue_10"]
            }
        ],
        batches=[
            {
                "id": "B1",
                "name": "TY CSE A",
                "subjects": ["OS", "DBMS", "ML", "AI"]
            }
        ],
        timeslots=["Mon_9", "Mon_10", "Tue_9", "Tue_10"],
        break_start="12",
        break_end="1"
    )
    
    print(json.dumps(result, indent=2))


def example_4_practical_theory():
    """Example 4: Mix of theory and practical classes"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Theory + Practical Mix")
    print("=" * 70)
    
    result = generate_timetable(
        teachers=[
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
        subjects=[
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
        rooms=[
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
        batches=[
            {
                "id": "B1",
                "name": "TY CSE A",
                "subjects": ["OS", "Lab"]
            }
        ],
        timeslots=["Mon_9", "Mon_10", "Mon_2", "Mon_3", "Tue_9", "Tue_10", "Tue_2", "Tue_3", "Wed_9", "Wed_10", "Wed_2", "Wed_3"],
        break_start="12",
        break_end="1"
    )
    
    print(json.dumps(result, indent=2))


def print_summary(result):
    """Print a summary of the result"""
    if result.get("status") == "success":
        print(f"\n✅ {result.get('message', 'Success')}")
        timetable = result.get("timetable", [])
        print(f"Total assignments: {len(timetable)}")
        print("\nScheduled lectures:")
        for lecture in timetable:
            print(f"  - {lecture['subject']} ({lecture['type']}) by {lecture['teacher']} in {lecture['room']} at {lecture['slot']}")
    else:
        print(f"\n❌ {result.get('message', 'Failed')}")
        print(f"Reason: {result.get('reason', 'Unknown')}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("MODULAR TIMETABLE SOLVER - EXAMPLES")
    print("=" * 70)
    
    # Run examples
    result1 = generate_timetable(
        teachers=[
            {
                "id": "T1",
                "name": "Dr. Smith",
                "subjects": ["OS"],
                "availability": ["Mon_9", "Mon_10", "Tue_9", "Tue_10"]
            }
        ],
        subjects=[
            {
                "id": "OS",
                "name": "Operating Systems",
                "type": "theory",
                "hours_per_week": 2
            }
        ],
        rooms=[
            {
                "id": "C301",
                "name": "Classroom 301",
                "type": "classroom",
                "availability": ["Mon_9", "Mon_10", "Tue_9", "Tue_10"]
            }
        ],
        batches=[
            {
                "id": "B1",
                "name": "TY CSE A",
                "subjects": ["OS"]
            }
        ],
        timeslots=["Mon_9", "Mon_10", "Tue_9", "Tue_10"]
    )
    
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Simple Timetable")
    print("=" * 70)
    print_summary(result1)
    
    example_2_complex()
    example_3_infeasible()
    example_4_practical_theory()
    
    print("\n" + "=" * 70)
    print("EXAMPLES COMPLETED")
    print("=" * 70)
