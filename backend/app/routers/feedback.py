from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackResponse
from app.schemas.response import StandardResponse
from app.services import feedback_service, user_service, complaint_service

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.post("", response_model=StandardResponse[FeedbackResponse], status_code=status.HTTP_201_CREATED)
def create_feedback(feedback_in: FeedbackCreate, db: Session = Depends(get_db)):
    """
    Submit new feedback for a complaint.
    Validates that the complaint, and citizen user exist, and that the complaint status is 'Resolved'.
    """
    # Validate complaint existence
    complaint = complaint_service.get_complaint_by_id(db, feedback_in.complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Complaint with ID {feedback_in.complaint_id} does not exist."
        )

    # Validate citizen user existence
    citizen = user_service.get_user_by_id(db, feedback_in.citizen_id)
    if not citizen:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Citizen with ID {feedback_in.citizen_id} does not exist."
        )

    try:
        db_feedback = feedback_service.create_feedback(db, feedback_in)
        return StandardResponse(
            success=True,
            message="Feedback submitted successfully.",
            data=db_feedback
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("", response_model=StandardResponse[List[FeedbackResponse]])
def get_feedbacks(db: Session = Depends(get_db)):
    """
    List all feedback.
    """
    feedbacks = feedback_service.get_feedbacks(db)
    return StandardResponse(
        success=True,
        message="Feedbacks retrieved successfully.",
        data=feedbacks
    )

@router.get("/{complaint_id}", response_model=StandardResponse[List[FeedbackResponse]])
def get_feedback_by_complaint(complaint_id: int, db: Session = Depends(get_db)):
    """
    Retrieve feedback entries for a specific complaint.
    """
    complaint = complaint_service.get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID {complaint_id} not found."
        )
    feedbacks = feedback_service.get_feedback_by_complaint(db, complaint_id)
    return StandardResponse(
        success=True,
        message=f"Feedback entries for complaint {complaint_id} retrieved successfully.",
        data=feedbacks
    )

@router.put("/{id}", response_model=StandardResponse[FeedbackResponse])
def update_feedback(id: int, feedback_in: FeedbackUpdate, db: Session = Depends(get_db)):
    """
    Update details of a feedback entry.
    """
    db_feedback = feedback_service.get_feedback_by_id(db, id)
    if not db_feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback with ID {id} not found."
        )
    updated_feedback = feedback_service.update_feedback(db, db_feedback, feedback_in)
    return StandardResponse(
        success=True,
        message="Feedback updated successfully.",
        data=updated_feedback
    )

@router.delete("/{id}", response_model=StandardResponse[dict])
def delete_feedback(id: int, db: Session = Depends(get_db)):
    """
    Delete a specific feedback entry by ID.
    """
    db_feedback = feedback_service.get_feedback_by_id(db, id)
    if not db_feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback with ID {id} not found."
        )
    feedback_service.delete_feedback(db, db_feedback)
    return StandardResponse(
        success=True,
        message="Feedback deleted successfully.",
        data={}
    )
