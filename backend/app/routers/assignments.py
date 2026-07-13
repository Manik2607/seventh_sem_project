from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate, AssignmentResponse
from app.schemas.response import StandardResponse
from app.services import assignment_service, user_service, complaint_service

router = APIRouter(prefix="/assignments", tags=["Assignments"])

@router.post("", response_model=StandardResponse[AssignmentResponse], status_code=status.HTTP_201_CREATED)
def create_assignment(assignment_in: AssignmentCreate, db: Session = Depends(get_db)):
    """
    Create a new assignment.
    Validates that the complaint, official (if specified), and engineer (if specified) exist.
    Also automatically updates the complaint status to 'Assigned' and logs it to status history.
    """
    # Validate complaint existence
    complaint = complaint_service.get_complaint_by_id(db, assignment_in.complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Complaint with ID {assignment_in.complaint_id} does not exist."
        )
        
    # Validate official existence
    if assignment_in.official_id is not None:
        official = user_service.get_user_by_id(db, assignment_in.official_id)
        if not official:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Official with ID {assignment_in.official_id} does not exist."
            )
            
    # Validate engineer existence
    if assignment_in.engineer_id is not None:
        engineer = user_service.get_user_by_id(db, assignment_in.engineer_id)
        if not engineer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Engineer with ID {assignment_in.engineer_id} does not exist."
            )

    db_assignment = assignment_service.create_assignment(db, assignment_in)
    return StandardResponse(
        success=True,
        message="Assignment created successfully.",
        data=db_assignment
    )

@router.get("", response_model=StandardResponse[List[AssignmentResponse]])
def get_assignments(db: Session = Depends(get_db)):
    """
    List all assignments.
    """
    assignments = assignment_service.get_assignments(db)
    return StandardResponse(
        success=True,
        message="Assignments retrieved successfully.",
        data=assignments
    )

@router.get("/engineer/{engineer_id}", response_model=StandardResponse[List[AssignmentResponse]])
def get_assignments_by_engineer(engineer_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all assignments for a specific engineer.
    """
    engineer = user_service.get_user_by_id(db, engineer_id)
    if not engineer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Engineer with ID {engineer_id} not found."
        )
    assignments = assignment_service.get_assignments_by_engineer(db, engineer_id)
    return StandardResponse(
        success=True,
        message=f"Assignments for engineer {engineer_id} retrieved successfully.",
        data=assignments
    )

@router.get("/official/{official_id}", response_model=StandardResponse[List[AssignmentResponse]])
def get_assignments_by_official(official_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all assignments for a specific official.
    """
    official = user_service.get_user_by_id(db, official_id)
    if not official:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Official with ID {official_id} not found."
        )
    assignments = assignment_service.get_assignments_by_official(db, official_id)
    return StandardResponse(
        success=True,
        message=f"Assignments for official {official_id} retrieved successfully.",
        data=assignments
    )

@router.get("/{id}", response_model=StandardResponse[AssignmentResponse])
def get_assignment(id: int, db: Session = Depends(get_db)):
    """
    Retrieve details of a specific assignment by ID.
    """
    db_assignment = assignment_service.get_assignment_by_id(db, id)
    if not db_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID {id} not found."
        )
    return StandardResponse(
        success=True,
        message="Assignment details retrieved successfully.",
        data=db_assignment
    )

@router.put("/{id}", response_model=StandardResponse[AssignmentResponse])
def update_assignment(id: int, assignment_in: AssignmentUpdate, db: Session = Depends(get_db)):
    """
    Update details of an assignment.
    """
    db_assignment = assignment_service.get_assignment_by_id(db, id)
    if not db_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID {id} not found."
        )

    # Validate official if provided in the update payload
    if assignment_in.official_id is not None:
        official = user_service.get_user_by_id(db, assignment_in.official_id)
        if not official:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Official with ID {assignment_in.official_id} does not exist."
            )

    # Validate engineer if provided in the update payload
    if assignment_in.engineer_id is not None:
        engineer = user_service.get_user_by_id(db, assignment_in.engineer_id)
        if not engineer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Engineer with ID {assignment_in.engineer_id} does not exist."
            )

    updated_assignment = assignment_service.update_assignment(db, db_assignment, assignment_in)
    return StandardResponse(
        success=True,
        message="Assignment updated successfully.",
        data=updated_assignment
    )

@router.delete("/{id}", response_model=StandardResponse[dict])
def delete_assignment(id: int, db: Session = Depends(get_db)):
    """
    Delete a specific assignment by ID.
    """
    db_assignment = assignment_service.get_assignment_by_id(db, id)
    if not db_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID {id} not found."
        )
    assignment_service.delete_assignment(db, db_assignment)
    return StandardResponse(
        success=True,
        message="Assignment deleted successfully.",
        data={}
    )
