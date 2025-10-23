"""
Hardcoded data for departments, rooms, labs, and batches
"""

# Departments
HARDCODED_DEPARTMENTS = [
    {"name": "Electrical", "code": "EE", "description": "Department of Electrical Engineering"},
    {"name": "Computer Science", "code": "CS", "description": "Department of Computer Science and Engineering"},
    {"name": "IOT", "code": "IOT", "description": "Department of Internet of Things"}
]

# Classrooms (C1-C15)
HARDCODED_CLASSROOMS = [
    {"name": f"C{i}", "type": "classroom", "capacity": 60, "location": "Building A", "tags": ["projector", "whiteboard"]}
    for i in range(1, 16)
]

# Labs (L1-L10)
HARDCODED_LABS = [
    {"name": f"L{i}", "type": "lab", "capacity": 30, "location": "Building B", "tags": ["computers", "equipment"]}
    for i in range(1, 11)
]

# All Rooms (Classrooms + Labs)
HARDCODED_ROOMS = HARDCODED_CLASSROOMS + HARDCODED_LABS

# Batches
HARDCODED_BATCHES = ["Batch A", "Batch B", "Batch C"]

# Years configuration
HARDCODED_YEARS = {
    1: {"name": "First Year", "batches": 3, "batch_names": HARDCODED_BATCHES},
    2: {"name": "Second Year", "batches": 3, "batch_names": HARDCODED_BATCHES},
    3: {"name": "Third Year", "batches": 3, "batch_names": HARDCODED_BATCHES},
    4: {"name": "Fourth Year", "batches": 3, "batch_names": HARDCODED_BATCHES}
}
