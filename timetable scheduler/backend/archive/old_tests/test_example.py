"""
Simple test script to verify the timetable solver implementation
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models import (
    Teacher, Room, Subject, Batch, TimetableRequest, 
    SubjectType, RoomType
)
from app.solver import solve_timetable

def create_test_data():
    """Create test data for timetable scheduling"""
    
    # Teachers
    teachers = [
        Teacher(
            id="T1",
            name="Dr. Smith",
            available_slots=["Mon_9", "Mon_10", "Mon_11", "Tue_9", "Tue_10", "Wed_9", "Wed_10"],
            subjects=["OS", "DBMS"]
        ),
        Teacher(
            id="T2",
            name="Prof. Johnson", 
            available_slots=["Mon_2", "Mon_3", "Tue_2", "Tue_3", "Wed_2", "Wed_3"],
            subjects=["ML", "AI"]
        ),
        Teacher(
            id="T3",
            name="Dr. Brown",
            available_slots=["Mon_9", "Mon_10", "Tue_9", "Tue_10", "Wed_9", "Wed_10"],
            subjects=["MLBC_Lab"]
        )
    ]
    
    # Rooms
    rooms = [
        Room(
            id="C301",
            name="Classroom 301",
            type=RoomType.CLASSROOM,
            available_slots=["Mon_9", "Mon_10", "Mon_11", "Mon_2", "Mon_3", 
                           "Tue_9", "Tue_10", "Tue_11", "Tue_2", "Tue_3",
                           "Wed_9", "Wed_10", "Wed_11", "Wed_2", "Wed_3"],
            capacity=60
        ),
        Room(
            id="Lab2",
            name="Computer Lab 2",
            type=RoomType.LAB,
            available_slots=["Mon_9", "Mon_10", "Mon_11", "Mon_2", "Mon_3",
                           "Tue_9", "Tue_10", "Tue_11", "Tue_2", "Tue_3", 
                           "Wed_9", "Wed_10", "Wed_11", "Wed_2", "Wed_3"],
            capacity=30
        )
    ]
    
    # Subjects
    subjects = [
        Subject(
            id="OS",
            name="Operating Systems",
            type=SubjectType.THEORY,
            duration=2,
            teachers=["T1"],
            required_room_type=RoomType.CLASSROOM
        ),
        Subject(
            id="ML",
            name="Machine Learning",
            type=SubjectType.THEORY,
            duration=2,
            teachers=["T2"],
            required_room_type=RoomType.CLASSROOM
        ),
        Subject(
            id="MLBC_Lab",
            name="MLBC Lab",
            type=SubjectType.PRACTICAL,
            duration=2,
            teachers=["T3"],
            required_room_type=RoomType.LAB
        )
    ]
    
    # Batches
    batches = [
        Batch(
            id="TYCSE_A",
            name="TY CSE A",
            subjects=["OS", "ML", "MLBC_Lab"],
            strength=60
        )
    ]
    
    return TimetableRequest(
        teachers=teachers,
        rooms=rooms,
        subjects=subjects,
        batches=batches,
        days=["Mon", "Tue", "Wed", "Thu", "Fri"],
        time_slots=["9", "10", "11", "12", "1", "2", "3"],
        break_start="12",
        break_end="1"
    )

def test_solver():
    """Test the timetable solver"""
    print("Creating test data...")
    request = create_test_data()
    
    print("Solving timetable...")
    result = solve_timetable(request)
    
    print(f"Solution found: {result.success}")
    
    if result.success:
        print(f"Generated {len(result.timetables)} timetables")
        for timetable in result.timetables:
            print(f"\nBatch: {timetable.batch}")
            print(f"Number of lectures: {len(timetable.slots)}")
            for lecture in timetable.slots:
                print(f"  {lecture.day} {lecture.time}: {lecture.subject} by {lecture.teacher} in {lecture.room}")
    else:
        print("Errors:")
        for error in result.errors:
            print(f"  - {error}")
    
    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")

if __name__ == "__main__":
    test_solver()
