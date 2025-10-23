"""
Routes package
"""
from .timetable_routes import router as timetable_router
from .department_routes import router as department_router
from .room_routes import router as room_router
from .settings_routes import router as settings_router

__all__ = [
    "timetable_router",
    "department_router",
    "room_router",
    "settings_router"
]
