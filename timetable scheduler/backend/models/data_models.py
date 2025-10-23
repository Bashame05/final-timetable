"""
Pydantic models for data validation and schema definition
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum


class RoomType(str, Enum):
    CLASSROOM = "classroom"
    LAB = "lab"


class SubjectType(str, Enum):
    THEORY = "theory"
    LAB = "lab"
    THEORY_LAB = "theory+lab"


class Room(BaseModel):
    name: str = Field(..., description="Room name")
    type: RoomType = Field(..., description="classroom or lab")
    capacity: int = Field(..., gt=0, description="Room capacity")
    location: str = Field(..., description="Building/location")
    for_subject: Optional[str] = Field(None, description="Lab specific to subject")

    class Config:
        use_enum_values = True


class Subject(BaseModel):
    name: str = Field(..., description="Subject name")
    type: SubjectType = Field(..., description="theory, lab, or theory+lab")
    hours_per_week: Optional[int] = Field(None, ge=0, description="Total hours per week (new format)")
    theory_hours: Optional[int] = Field(None, ge=0, description="Theory hours (old format)")
    practical_hours: Optional[int] = Field(None, ge=0, description="Practical hours (old format)")
    teacher: Optional[str] = Field(None, description="Teacher name")

    class Config:
        use_enum_values = True


class WeekConfig(BaseModel):
    week_start_time: str = Field(..., description="Start time (HH:MM format)")
    week_end_time: str = Field(..., description="End time (HH:MM format)")
    lunch_start: str = Field(..., description="Lunch start time (HH:MM format)")
    lunch_end: str = Field(..., description="Lunch end time (HH:MM format)")
    working_days: List[str] = Field(..., description="List of working days")

    @validator("working_days")
    def validate_days(cls, v):
        valid_days = {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}
        if not all(day in valid_days for day in v):
            raise ValueError("Invalid day names")
        return v


class SpecialSession(BaseModel):
    enabled: bool = Field(default=False)
    hours_per_week: int = Field(default=0, ge=0)
    days_per_week: int = Field(default=0, ge=0)
    duration_per_session: int = Field(default=0, ge=0)


class TimetableRequest(BaseModel):
    department: str = Field(..., description="Department name")
    week_config: WeekConfig = Field(..., description="Week configuration")
    rooms: List[Room] = Field(..., description="Available rooms")
    subjects: List[Subject] = Field(..., description="Subjects to schedule")
    special_sessions: Optional[Dict[str, SpecialSession]] = Field(
        default_factory=dict,
        description="Special sessions (mini_project, tutorial, etc.)"
    )

    @validator("rooms")
    def validate_rooms(cls, v):
        if len(v) == 0:
            raise ValueError("At least one room is required")
        return v

    @validator("subjects")
    def validate_subjects(cls, v):
        if len(v) == 0:
            raise ValueError("At least one subject is required")
        return v


class TimetableSlot(BaseModel):
    day: str
    slot: str  # "09:00-10:00"
    subject: str
    room: str
    teacher: Optional[str] = None
    type: str  # "theory" or "lab"


class Conflict(BaseModel):
    type: str  # "teacher_overlap", "room_overlap", "batch_overlap"
    entity: str  # teacher/room/batch name
    day: str
    slot: str
    reason: str


class TimetableResponse(BaseModel):
    status: str  # "success" or "failed"
    message: str
    timetable: List[TimetableSlot] = []
    conflicts: List[Conflict] = []
    metadata: Optional[Dict[str, Any]] = None


class DepartmentRequest(BaseModel):
    department_name: str = Field(..., description="Department name")
    subjects: List[Subject] = Field(..., description="Subjects in department")


class RoomsRequest(BaseModel):
    rooms: List[Room] = Field(..., description="List of rooms")


class SettingsRequest(BaseModel):
    week_start_time: Optional[str] = None
    week_end_time: Optional[str] = None
    lunch_start: Optional[str] = None
    lunch_end: Optional[str] = None
    working_days: Optional[List[str]] = None
