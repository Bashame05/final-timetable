"""
Routes for timetable generation and management
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from models.data_models import TimetableRequest, TimetableResponse, TimetableSlot, Conflict
from solver.solver_relaxed import solve_relaxed as solve_timetable

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/timetable", tags=["timetable"])


@router.post("/generate", response_model=TimetableResponse)
async def generate_timetable_endpoint(request: TimetableRequest) -> TimetableResponse:
    """
    Generate a complete timetable based on provided configuration
    
    Request body:
    {
        "department": "Computer Engineering",
        "week_config": {
            "week_start_time": "09:00",
            "week_end_time": "16:00",
            "lunch_start": "13:00",
            "lunch_end": "14:00",
            "working_days": ["Mon", "Tue", "Wed", "Thu", "Fri"]
        },
        "rooms": [...],
        "subjects": [...],
        "special_sessions": {...}
    }
    """
    try:
        logger.info(f"Generating timetable for department: {request.department}")

        # Convert Pydantic models to dictionaries
        week_config = request.week_config.dict()
        rooms = [room.dict() for room in request.rooms]
        subjects = [subject.dict() for subject in request.subjects]
        special_sessions = (
            {k: v.dict() for k, v in request.special_sessions.items()}
            if request.special_sessions
            else {}
        )

        # Use modular solver
        result = solve_timetable(
            week_config=week_config,
            subjects=subjects,
            rooms=rooms,
            batches=["Batch A", "Batch B", "Batch C"]
        )
        
        success = result["status"] == "success"
        timetable_data = result.get("timetable", [])
        conflicts = [] if success else [{"reason": result.get("reason", "Unknown error")}]

        if success:
            # Convert to TimetableSlot objects
            timetable_slots = []
            for slot in timetable_data:
                try:
                    timetable_slots.append(
                        TimetableSlot(
                            day=slot["day"],
                            slot=f"{slot['start_time']}-{slot['end_time']}",
                            subject=slot["subject"],
                            room=slot["room"],
                            type=slot["type"],
                            teacher=slot.get("teacher", "")
                        )
                    )
                except Exception as e:
                    logger.error(f"Error creating slot: {slot}, Error: {str(e)}")
                    continue

            return TimetableResponse(
                status="success",
                message="✅ Timetable generated successfully",
                timetable=timetable_slots,
                conflicts=[],
                metadata={
                    "department": request.department,
                    "total_slots": len(timetable_slots),
                    "working_days": request.week_config.working_days
                }
            )
        else:
            conflict_objs = [
                Conflict(
                    type="feasibility",
                    entity="problem",
                    day="",
                    slot="",
                    reason=c.get("reason", "Unknown error")
                )
                for c in conflicts
            ]

            return TimetableResponse(
                status="failed",
                message="❌ Failed to generate timetable",
                timetable=[],
                conflicts=conflict_objs,
                metadata={"department": request.department}
            )

    except Exception as e:
        logger.error(f"Error generating timetable: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/status")
async def get_timetable_status() -> Dict[str, Any]:
    """
    Get current timetable generation status
    """
    return {
        "status": "ready",
        "message": "Timetable generator is ready to accept requests"
    }


@router.post("/validate")
async def validate_timetable(request: TimetableRequest) -> Dict[str, Any]:
    """
    Validate timetable request without generating
    """
    try:
        # Check if all required fields are present
        if not request.department:
            raise ValueError("Department name is required")

        if not request.week_config:
            raise ValueError("Week configuration is required")

        if not request.rooms or len(request.rooms) == 0:
            raise ValueError("At least one room is required")

        if not request.subjects or len(request.subjects) == 0:
            raise ValueError("At least one subject is required")

        # Check feasibility
        total_hours = sum(s.hours_per_week for s in request.subjects)
        available_slots = len(request.week_config.working_days) * 8  # Approximate

        if total_hours > available_slots:
            return {
                "valid": False,
                "message": f"Not enough slots: {total_hours} hours required, ~{available_slots} slots available",
                "errors": ["Insufficient time slots for all subjects"]
            }

        return {
            "valid": True,
            "message": "Request is valid and feasible",
            "errors": []
        }

    except Exception as e:
        logger.error(f"Error validating timetable: {str(e)}")
        return {
            "valid": False,
            "message": str(e),
            "errors": [str(e)]
        }
