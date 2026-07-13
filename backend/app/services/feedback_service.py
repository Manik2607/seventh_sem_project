from sqlalchemy.orm import Session
from app.models.feedback import Feedback
from app.models.complaint import Complaint, ComplaintStatusEnum
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate

def get_feedbacks(db: Session):
    """
    Get all feedback.
    """
    return db.query(Feedback).all()

def get_feedback_by_id(db: Session, feedback_id: int):
    """
    Get a feedback entry by unique ID.
    """
    return db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()

def get_feedback_by_complaint(db: Session, complaint_id: int):
    """
    Get all feedback entries associated with a specific complaint.
    """
    return db.query(Feedback).filter(Feedback.complaint_id == complaint_id).all()

def create_feedback(db: Session, feedback_in: FeedbackCreate):
    """
    Submit new feedback for a complaint.
    Validates that the complaint is currently in the 'Resolved' status.
    """
    # Verify complaint status is "Resolved"
    db_complaint = db.query(Complaint).filter(Complaint.complaint_id == feedback_in.complaint_id).first()
    if not db_complaint:
        raise ValueError(f"Complaint with ID {feedback_in.complaint_id} does not exist.")
        
    if db_complaint.status != ComplaintStatusEnum.RESOLVED:
        raise ValueError("Feedback is only allowed for resolved complaints.")
        
    try:
        db_feedback = Feedback(
            complaint_id=feedback_in.complaint_id,
            citizen_id=feedback_in.citizen_id,
            rating=feedback_in.rating,
            comments=feedback_in.comments
        )
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        return db_feedback
    except Exception as e:
        db.rollback()
        raise e

def update_feedback(db: Session, db_feedback: Feedback, feedback_in: FeedbackUpdate):
    """
    Update details of a feedback entry.
    """
    try:
        if feedback_in.rating is not None:
            db_feedback.rating = feedback_in.rating
        if feedback_in.comments is not None:
            db_feedback.comments = feedback_in.comments
            
        db.commit()
        db.refresh(db_feedback)
        return db_feedback
    except Exception as e:
        db.rollback()
        raise e

def delete_feedback(db: Session, db_feedback: Feedback):
    """
    Delete a feedback entry.
    """
    try:
        db.delete(db_feedback)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
