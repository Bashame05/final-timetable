from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class SubjectType(str, Enum):
    THEORY = "theory"
    PRACTICAL = "practical"
    PROJECT = "project"

class RoomType(str, Enum):
    CLASSROOM = "classroom"
    LAB = "lab"

class Teacher(BaseModel):
    id: str
    name: str
    available_slots: List[str]  # e.g. ["Mon_9", "Mon_10", ...]
    subjects: List[str] = []  # List of subject IDs this teacher can teach

class Room(BaseModel):
    id: str
    name: str
    type: RoomType  # "classroom" or "lab"
    available_slots: List[str]
    capacity: Optional[int] = None

class Subject(BaseModel):
    id: str
    name: str
    type: SubjectType  # "theory" or "practical" or "project"
    duration: int  # in hours
    teachers: List[str] = []  # List of teacher IDs who can teach this subject
    required_room_type: Optional[RoomType] = None  # Specific room type requirement

class Batch(BaseModel):
    id: str
    name: str
    subjects: List[str] = []  # List of subject IDs for this batch
    strength: Optional[int] = None  # Number of students

class Lecture(BaseModel):
    day: str
    time: str
    subject: str
    teacher: str
    room: str
    type: str
    batch: str

class TimetableRequest(BaseModel):
    teachers: List[Teacher]
    rooms: List[Room]
    subjects: List[Subject]
    batches: List[Batch]
    days: List[str]
    time_slots: List[str]  # e.g. ["9", "10", "11", "12", "1", "2", "3"]
    break_start: Optional[str] = "12"  # Break time start (12 PM)
    break_end: Optional[str] = "1"     # Break time end (1 PM)

class TimetableResponse(BaseModel):
    batch: str
    slots: List[Lecture]
    status: str = "success"
    message: Optional[str] = None

class SolverResult(BaseModel):
    success: bool
    timetables: List[TimetableResponse]
    errors: List[str] = []
    warnings: List[str] = []

class ConstraintViolation(BaseModel):
    type: str
    description: str
    affected_entities: List[str]
    severity: str  # "error" or "warning"
