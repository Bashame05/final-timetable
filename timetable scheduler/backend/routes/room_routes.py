"""
Routes for room and lab management
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
import logging

from models.data_models import Room, RoomsRequest
from hardcoded_data import HARDCODED_ROOMS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/rooms", tags=["rooms"])

# In-memory storage (replace with database in production)
rooms_db: Dict[str, Dict[str, Any]] = {}

# Initialize with hardcoded rooms
for room in HARDCODED_ROOMS:
    rooms_db[room['name']] = room


@router.post("/", response_model=Dict[str, Any])
async def create_rooms(request: RoomsRequest) -> Dict[str, Any]:
    """
    Create/update rooms and labs
    
    Request body:
    {
        "rooms": [
            {"name": "Room 101", "type": "classroom", "capacity": 60, "location": "Building A"},
            {"name": "CS Lab 1", "type": "lab", "capacity": 30, "location": "Building C", "for_subject": "DBMS"}
        ]
    }
    """
    try:
        logger.info(f"Creating/updating {len(request.rooms)} rooms")

        for room in request.rooms:
            room_dict = room.dict()
            rooms_db[room.name] = room_dict
            logger.info(f"Room '{room.name}' stored")

        return {
            "status": "success",
            "message": f"{len(request.rooms)} room(s) created/updated successfully",
            "count": len(rooms_db),
            "rooms": list(rooms_db.values())
        }

    except Exception as e:
        logger.error(f"Error creating rooms: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=Dict[str, Any])
async def list_rooms() -> Dict[str, Any]:
    """
    List all rooms
    """
    try:
        rooms = list(rooms_db.values())
        classrooms = [r for r in rooms if r["type"] == "classroom"]
        labs = [r for r in rooms if r["type"] == "lab"]

        return {
            "status": "success",
            "count": len(rooms),
            "classrooms_count": len(classrooms),
            "labs_count": len(labs),
            "rooms": rooms,
            "classrooms": classrooms,
            "labs": labs
        }

    except Exception as e:
        logger.error(f"Error listing rooms: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{room_name}", response_model=Dict[str, Any])
async def get_room(room_name: str) -> Dict[str, Any]:
    """
    Get room details by name
    """
    try:
        if room_name not in rooms_db:
            raise HTTPException(
                status_code=404,
                detail=f"Room '{room_name}' not found"
            )

        return {
            "status": "success",
            "room": rooms_db[room_name]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving room: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{room_name}", response_model=Dict[str, Any])
async def update_room(room_name: str, room: Room) -> Dict[str, Any]:
    """
    Update room details
    """
    try:
        if room_name not in rooms_db:
            raise HTTPException(
                status_code=404,
                detail=f"Room '{room_name}' not found"
            )

        logger.info(f"Updating room: {room_name}")

        rooms_db[room_name] = room.dict()

        return {
            "status": "success",
            "message": f"Room '{room_name}' updated successfully",
            "room": rooms_db[room_name]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating room: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{room_name}", response_model=Dict[str, Any])
async def delete_room(room_name: str) -> Dict[str, Any]:
    """
    Delete a room
    """
    try:
        if room_name not in rooms_db:
            raise HTTPException(
                status_code=404,
                detail=f"Room '{room_name}' not found"
            )

        logger.info(f"Deleting room: {room_name}")

        del rooms_db[room_name]

        return {
            "status": "success",
            "message": f"Room '{room_name}' deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting room: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/type/{room_type}", response_model=Dict[str, Any])
async def get_rooms_by_type(room_type: str) -> Dict[str, Any]:
    """
    Get all rooms of a specific type (classroom or lab)
    """
    try:
        if room_type not in ["classroom", "lab"]:
            raise HTTPException(
                status_code=400,
                detail="Room type must be 'classroom' or 'lab'"
            )

        filtered_rooms = [r for r in rooms_db.values() if r["type"] == room_type]

        return {
            "status": "success",
            "type": room_type,
            "count": len(filtered_rooms),
            "rooms": filtered_rooms
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error filtering rooms: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/location/{location}", response_model=Dict[str, Any])
async def get_rooms_by_location(location: str) -> Dict[str, Any]:
    """
    Get all rooms in a specific location
    """
    try:
        filtered_rooms = [r for r in rooms_db.values() if r["location"] == location]

        return {
            "status": "success",
            "location": location,
            "count": len(filtered_rooms),
            "rooms": filtered_rooms
        }

    except Exception as e:
        logger.error(f"Error filtering rooms by location: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subject/{subject_name}", response_model=Dict[str, Any])
async def get_labs_for_subject(subject_name: str) -> Dict[str, Any]:
    """
    Get all labs available for a specific subject
    """
    try:
        filtered_labs = [
            r for r in rooms_db.values()
            if r["type"] == "lab" and (r.get("for_subject") == subject_name or r.get("for_subject") is None)
        ]

        return {
            "status": "success",
            "subject": subject_name,
            "count": len(filtered_labs),
            "labs": filtered_labs
        }

    except Exception as e:
        logger.error(f"Error retrieving labs for subject: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
