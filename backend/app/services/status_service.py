from sqlalchemy.orm import Session
from app.models.status_history import StatusHistory
from app.models.complaint import Complaint
from app.schemas.status_history import StatusHistoryCreate

def get_status_history_by_complaint(db: Session, complaint_id: int):
    """
    Get all status history logs for a specific complaint, ordered by update time.
    """
    return db.query(StatusHistory).filter(StatusHistory.complaint_id == complaint_id).order_by(StatusHistory.updated_at.asc()).all()

def get_status_by_id(db: Session, status_id: int):
    """
    Get status history log by unique status_id.
    """
    return db.query(StatusHistory).filter(StatusHistory.status_id == status_id).first()

def create_status_history(db: Session, status_in: StatusHistoryCreate):
    """
    Create a new status history record and synchronize the complaint's main status.
    Executes in a single database transaction.
    """
    try:
        # Create status history record
        db_status = StatusHistory(
            complaint_id=status_in.complaint_id,
            status=status_in.status,
            remarks=status_in.remarks,
            updated_by=status_in.updated_by
        )
        db.add(db_status)
        
        # Update complaint main status
        db_complaint = db.query(Complaint).filter(Complaint.complaint_id == status_in.complaint_id).first()
        if db_complaint:
            db_complaint.status = status_in.status
            
        db.commit()
        db.refresh(db_status)
        return db_status
    except Exception as e:
        db.rollback()
        raise e

def update_status_history(db: Session, db_status: StatusHistory, remarks: str | None, status_val = None, updated_by: int | None = None):
    """
    Update status history details. If status value changes, sync the complaint's main status too.
    """
    try:
        status_changed = False
        if status_val is not None and status_val != db_status.status:
            db_status.status = status_val
            status_changed = True
            
        if remarks is not None:
            db_status.remarks = remarks
        if updated_by is not None:
            db_status.updated_by = updated_by
            
        if status_changed:
            db_complaint = db.query(Complaint).filter(Complaint.complaint_id == db_status.complaint_id).first()
            if db_complaint:
                db_complaint.status = status_val
                
        db.commit()
        db.refresh(db_status)
        return db_status
    except Exception as e:
        db.rollback()
        raise e
