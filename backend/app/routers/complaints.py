from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.complaint import ComplaintCreate, ComplaintUpdate, ComplaintResponse
from app.schemas.response import StandardResponse
from app.services import complaint_service, user_service, department_service
from app.models.complaint import ComplaintStatusEnum

router = APIRouter(prefix="/complaints", tags=["Complaints"])

@router.post("", response_model=StandardResponse[ComplaintResponse], status_code=status.HTTP_201_CREATED)
def create_complaint(complaint_in: ComplaintCreate, db: Session = Depends(get_db)):
    """
    Create a new complaint.
    Validates that the citizen exists, and the department exists if specified.
    """
    # Validate citizen existence
    citizen = user_service.get_user_by_id(db, complaint_in.citizen_id)
    if not citizen:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Citizen with ID {complaint_in.citizen_id} does not exist."
        )

    # Validate department existence if provided
    if complaint_in.department_id is not None:
        dept = department_service.get_department_by_id(db, complaint_in.department_id)
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Department with ID {complaint_in.department_id} does not exist."
            )

    db_complaint = complaint_service.create_complaint(db, complaint_in)
    return StandardResponse(
        success=True,
        message="Complaint created successfully.",
        data=db_complaint
    )

@router.get("", response_model=StandardResponse[List[ComplaintResponse]])
def get_complaints(db: Session = Depends(get_db)):
    """
    List all complaints.
    """
    complaints = complaint_service.get_complaints(db)
    return StandardResponse(
        success=True,
        message="Complaints retrieved successfully.",
        data=complaints
    )

@router.get("/citizen/{citizen_id}", response_model=StandardResponse[List[ComplaintResponse]])
def get_complaints_by_citizen(citizen_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all complaints filed by a specific citizen.
    """
    citizen = user_service.get_user_by_id(db, citizen_id)
    if not citizen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Citizen with ID {citizen_id} not found."
        )
    complaints = complaint_service.get_complaints_by_citizen(db, citizen_id)
    return StandardResponse(
        success=True,
        message=f"Complaints for citizen {citizen_id} retrieved successfully.",
        data=complaints
    )

@router.get("/status/{status}", response_model=StandardResponse[List[ComplaintResponse]])
def get_complaints_by_status(status: ComplaintStatusEnum, db: Session = Depends(get_db)):
    """
    Retrieve all complaints filtered by status.
    """
    complaints = complaint_service.get_complaints_by_status(db, status)
    return StandardResponse(
        success=True,
        message=f"Complaints with status '{status.value}' retrieved successfully.",
        data=complaints
    )

@router.get("/department/{department_id}", response_model=StandardResponse[List[ComplaintResponse]])
def get_complaints_by_department(department_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all complaints assigned to a specific department.
    """
    dept = department_service.get_department_by_id(db, department_id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {department_id} not found."
        )
    complaints = complaint_service.get_complaints_by_department(db, department_id)
    return StandardResponse(
        success=True,
        message=f"Complaints for department {department_id} retrieved successfully.",
        data=complaints
    )

@router.get("/{id}", response_model=StandardResponse[ComplaintResponse])
def get_complaint(id: int, db: Session = Depends(get_db)):
    """
    Retrieve details of a specific complaint by ID.
    """
    db_complaint = complaint_service.get_complaint_by_id(db, id)
    if not db_complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID {id} not found."
        )
    return StandardResponse(
        success=True,
        message="Complaint details retrieved successfully.",
        data=db_complaint
    )

@router.put("/{id}", response_model=StandardResponse[ComplaintResponse])
def update_complaint(id: int, complaint_in: ComplaintUpdate, db: Session = Depends(get_db)):
    """
    Update details of a complaint. If status is updated, a history log is automatically appended.
    """
    db_complaint = complaint_service.get_complaint_by_id(db, id)
    if not db_complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID {id} not found."
        )

    # Validate department if provided in the update payload
    if complaint_in.department_id is not None:
        dept = department_service.get_department_by_id(db, complaint_in.department_id)
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Department with ID {complaint_in.department_id} does not exist."
            )

    # Validate updated_by user if provided
    if complaint_in.updated_by is not None:
        updater = user_service.get_user_by_id(db, complaint_in.updated_by)
        if not updater:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with ID {complaint_in.updated_by} does not exist."
            )

    updated_complaint = complaint_service.update_complaint(db, db_complaint, complaint_in)
    return StandardResponse(
        success=True,
        message="Complaint updated successfully.",
        data=updated_complaint
    )

@router.delete("/{id}", response_model=StandardResponse[dict])
def delete_complaint(id: int, db: Session = Depends(get_db)):
    """
    Delete a specific complaint by ID.
    """
    db_complaint = complaint_service.get_complaint_by_id(db, id)
    if not db_complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID {id} not found."
        )
    complaint_service.delete_complaint(db, db_complaint)
    return StandardResponse(
        success=True,
        message="Complaint deleted successfully.",
        data={}
    )
