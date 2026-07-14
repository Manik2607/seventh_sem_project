from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.status_history import StatusHistoryCreate, StatusHistoryUpdate, StatusHistoryResponse
from app.schemas.response import StandardResponse
from app.services import status_service, user_service, complaint_service

router = APIRouter(prefix="/status", tags=["Status History"])

@router.post("", response_model=StandardResponse[StatusHistoryResponse], status_code=status.HTTP_201_CREATED)
def create_status_history(status_in: StatusHistoryCreate, db: Session = Depends(get_db)):
    """
    Create a new status history entry for a complaint.
    Updates the complaint's main status and logs the history in a database transaction.
    """
    # Validate complaint existence
    complaint = complaint_service.get_complaint_by_id(db, status_in.complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Complaint with ID {status_in.complaint_id} does not exist."
        )

    # Validate updated_by user existence if specified
    if status_in.updated_by is not None:
        updater = user_service.get_user_by_id(db, status_in.updated_by)
        if not updater:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with ID {status_in.updated_by} does not exist."
            )

    db_status = status_service.create_status_history(db, status_in)
    return StandardResponse(
        success=True,
        message="Status history created and complaint status updated successfully.",
        data=db_status
    )

@router.get("/{complaint_id}", response_model=StandardResponse[List[StatusHistoryResponse]])
def get_status_history_by_complaint(complaint_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all status history logs for a specific complaint.
    """
    complaint = complaint_service.get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID {complaint_id} not found."
        )
    status_logs = status_service.get_status_history_by_complaint(db, complaint_id)
    return StandardResponse(
        success=True,
        message=f"Status history logs retrieved for complaint {complaint_id}.",
        data=status_logs
    )

@router.put("/{status_id}", response_model=StandardResponse[StatusHistoryResponse])
def update_status_history(status_id: int, status_in: StatusHistoryUpdate, db: Session = Depends(get_db)):
    """
    Update details of an existing status history log.
    If the status changes, it updates the associated complaint status as well.
    """
    db_status = status_service.get_status_by_id(db, status_id)
    if not db_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Status history log with ID {status_id} not found."
        )

    # Validate updated_by user if provided
    if status_in.updated_by is not None:
        updater = user_service.get_user_by_id(db, status_in.updated_by)
        if not updater:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with ID {status_in.updated_by} does not exist."
            )

    updated_status = status_service.update_status_history(
        db=db,
        db_status=db_status,
        remarks=status_in.remarks,
        status_val=status_in.status,
        updated_by=status_in.updated_by
    )
    return StandardResponse(
        success=True,
        message="Status history updated successfully.",
        data=updated_status
    )
