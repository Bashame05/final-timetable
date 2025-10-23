"""
Routes for department management
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
import logging

from models.data_models import DepartmentRequest, Subject
from hardcoded_data import HARDCODED_DEPARTMENTS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/departments", tags=["departments"])

# In-memory storage (replace with database in production)
departments_db: Dict[str, Dict[str, Any]] = {}

# Initialize with hardcoded departments
for dept in HARDCODED_DEPARTMENTS:
    departments_db[dept['name']] = dept


@router.post("/", response_model=Dict[str, Any])
async def create_department(request: DepartmentRequest) -> Dict[str, Any]:
    """
    Create a new department with subjects
    
    Request body:
    {
        "department_name": "Computer Engineering",
        "subjects": [
            {"name": "DBMS", "type": "theory+lab", "hours_per_week": 3},
            {"name": "CN", "type": "theory", "hours_per_week": 3}
        ]
    }
    """
    try:
        logger.info(f"Creating department: {request.department_name}")

        if request.department_name in departments_db:
            raise HTTPException(
                status_code=400,
                detail=f"Department '{request.department_name}' already exists"
            )

        # Store department
        departments_db[request.department_name] = {
            "name": request.department_name,
            "subjects": [s.dict() for s in request.subjects],
            "created_at": str(__import__("datetime").datetime.now())
        }

        return {
            "status": "success",
            "message": f"Department '{request.department_name}' created successfully",
            "department": departments_db[request.department_name]
        }

    except Exception as e:
        logger.error(f"Error creating department: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{department_name}", response_model=Dict[str, Any])
async def get_department(department_name: str) -> Dict[str, Any]:
    """
    Get department details by name
    """
    try:
        if department_name not in departments_db:
            raise HTTPException(
                status_code=404,
                detail=f"Department '{department_name}' not found"
            )

        return {
            "status": "success",
            "department": departments_db[department_name]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving department: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=Dict[str, Any])
async def list_departments() -> Dict[str, Any]:
    """
    List all departments
    """
    try:
        departments = list(departments_db.values())
        return {
            "status": "success",
            "count": len(departments),
            "departments": departments
        }

    except Exception as e:
        logger.error(f"Error listing departments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{department_name}", response_model=Dict[str, Any])
async def update_department(
    department_name: str,
    request: DepartmentRequest
) -> Dict[str, Any]:
    """
    Update department subjects
    """
    try:
        if department_name not in departments_db:
            raise HTTPException(
                status_code=404,
                detail=f"Department '{department_name}' not found"
            )

        logger.info(f"Updating department: {department_name}")

        departments_db[department_name]["subjects"] = [s.dict() for s in request.subjects]

        return {
            "status": "success",
            "message": f"Department '{department_name}' updated successfully",
            "department": departments_db[department_name]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating department: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{department_name}", response_model=Dict[str, Any])
async def delete_department(department_name: str) -> Dict[str, Any]:
    """
    Delete a department
    """
    try:
        if department_name not in departments_db:
            raise HTTPException(
                status_code=404,
                detail=f"Department '{department_name}' not found"
            )

        logger.info(f"Deleting department: {department_name}")

        del departments_db[department_name]

        return {
            "status": "success",
            "message": f"Department '{department_name}' deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting department: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{department_name}/subjects", response_model=Dict[str, Any])
async def add_subject(
    department_name: str,
    subject: Subject
) -> Dict[str, Any]:
    """
    Add a subject to a department
    """
    try:
        if department_name not in departments_db:
            raise HTTPException(
                status_code=404,
                detail=f"Department '{department_name}' not found"
            )

        logger.info(f"Adding subject '{subject.name}' to department '{department_name}'")

        # Check if subject already exists
        existing_subjects = [s["name"] for s in departments_db[department_name]["subjects"]]
        if subject.name in existing_subjects:
            raise HTTPException(
                status_code=400,
                detail=f"Subject '{subject.name}' already exists in this department"
            )

        departments_db[department_name]["subjects"].append(subject.dict())

        return {
            "status": "success",
            "message": f"Subject '{subject.name}' added successfully",
            "department": departments_db[department_name]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding subject: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{department_name}/subjects/{subject_name}", response_model=Dict[str, Any])
async def remove_subject(
    department_name: str,
    subject_name: str
) -> Dict[str, Any]:
    """
    Remove a subject from a department
    """
    try:
        if department_name not in departments_db:
            raise HTTPException(
                status_code=404,
                detail=f"Department '{department_name}' not found"
            )

        logger.info(f"Removing subject '{subject_name}' from department '{department_name}'")

        subjects = departments_db[department_name]["subjects"]
        departments_db[department_name]["subjects"] = [
            s for s in subjects if s["name"] != subject_name
        ]

        return {
            "status": "success",
            "message": f"Subject '{subject_name}' removed successfully",
            "department": departments_db[department_name]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing subject: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
