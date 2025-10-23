"""
Routes for settings and configuration management
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging

from models.data_models import WeekConfig, SettingsRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/settings", tags=["settings"])

# In-memory storage (replace with database in production)
settings_db: Dict[str, Any] = {
    "week_config": {
        "week_start_time": "09:00",
        "week_end_time": "16:00",
        "lunch_start": "13:00",
        "lunch_end": "14:00",
        "working_days": ["Mon", "Tue", "Wed", "Thu", "Fri"]
    },
    "special_sessions": {}
}


@router.post("/week-config", response_model=Dict[str, Any])
async def set_week_config(config: WeekConfig) -> Dict[str, Any]:
    """
    Set week configuration (working hours, break times, working days)
    
    Request body:
    {
        "week_start_time": "09:00",
        "week_end_time": "16:00",
        "lunch_start": "13:00",
        "lunch_end": "14:00",
        "working_days": ["Mon", "Tue", "Wed", "Thu", "Fri"]
    }
    """
    try:
        logger.info("Updating week configuration")

        settings_db["week_config"] = config.dict()

        return {
            "status": "success",
            "message": "Week configuration updated successfully",
            "week_config": settings_db["week_config"]
        }

    except Exception as e:
        logger.error(f"Error setting week config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/week-config", response_model=Dict[str, Any])
async def get_week_config() -> Dict[str, Any]:
    """
    Get current week configuration
    """
    try:
        return {
            "status": "success",
            "week_config": settings_db["week_config"]
        }

    except Exception as e:
        logger.error(f"Error retrieving week config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/special-sessions", response_model=Dict[str, Any])
async def set_special_sessions(sessions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Set special sessions configuration (mini-projects, tutorials, etc.)
    
    Request body:
    {
        "mini_project": {
            "enabled": true,
            "hours_per_week": 4,
            "days_per_week": 2,
            "duration_per_session": 1
        },
        "math_tutorial": {
            "enabled": true,
            "hours_per_week": 1,
            "days_per_week": 1,
            "duration_per_session": 1
        }
    }
    """
    try:
        logger.info("Updating special sessions configuration")

        settings_db["special_sessions"] = sessions

        return {
            "status": "success",
            "message": "Special sessions configuration updated successfully",
            "special_sessions": settings_db["special_sessions"]
        }

    except Exception as e:
        logger.error(f"Error setting special sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/special-sessions", response_model=Dict[str, Any])
async def get_special_sessions() -> Dict[str, Any]:
    """
    Get current special sessions configuration
    """
    try:
        return {
            "status": "success",
            "special_sessions": settings_db["special_sessions"]
        }

    except Exception as e:
        logger.error(f"Error retrieving special sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/special-sessions/{session_name}", response_model=Dict[str, Any])
async def add_special_session(
    session_name: str,
    session_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Add or update a specific special session
    """
    try:
        logger.info(f"Adding/updating special session: {session_name}")

        settings_db["special_sessions"][session_name] = session_config

        return {
            "status": "success",
            "message": f"Special session '{session_name}' added/updated successfully",
            "special_sessions": settings_db["special_sessions"]
        }

    except Exception as e:
        logger.error(f"Error adding special session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/special-sessions/{session_name}", response_model=Dict[str, Any])
async def remove_special_session(session_name: str) -> Dict[str, Any]:
    """
    Remove a special session
    """
    try:
        logger.info(f"Removing special session: {session_name}")

        if session_name in settings_db["special_sessions"]:
            del settings_db["special_sessions"][session_name]

        return {
            "status": "success",
            "message": f"Special session '{session_name}' removed successfully",
            "special_sessions": settings_db["special_sessions"]
        }

    except Exception as e:
        logger.error(f"Error removing special session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=Dict[str, Any])
async def get_all_settings() -> Dict[str, Any]:
    """
    Get all settings
    """
    try:
        return {
            "status": "success",
            "settings": settings_db
        }

    except Exception as e:
        logger.error(f"Error retrieving settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset", response_model=Dict[str, Any])
async def reset_settings() -> Dict[str, Any]:
    """
    Reset all settings to defaults
    """
    try:
        logger.info("Resetting settings to defaults")

        settings_db.clear()
        settings_db.update({
            "week_config": {
                "week_start_time": "09:00",
                "week_end_time": "16:00",
                "lunch_start": "13:00",
                "lunch_end": "14:00",
                "working_days": ["Mon", "Tue", "Wed", "Thu", "Fri"]
            },
            "special_sessions": {}
        })

        return {
            "status": "success",
            "message": "Settings reset to defaults",
            "settings": settings_db
        }

    except Exception as e:
        logger.error(f"Error resetting settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
