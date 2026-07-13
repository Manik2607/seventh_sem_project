from sqlalchemy.orm import Session
from app.models.assignment import Assignment, AssignmentStatusEnum
from app.models.complaint import Complaint, ComplaintStatusEnum
from app.models.status_history import StatusHistory
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate

def get_assignments(db: Session):
    """
    Get all assignments.
    """
    return db.query(Assignment).all()

def get_assignment_by_id(db: Session, assignment_id: int):
    """
    Get an assignment by unique ID.
    """
    return db.query(Assignment).filter(Assignment.assignment_id == assignment_id).first()

def get_assignments_by_engineer(db: Session, engineer_id: int):
    """
    Get assignments assigned to a specific engineer.
    """
    return db.query(Assignment).filter(Assignment.engineer_id == engineer_id).all()

def get_assignments_by_official(db: Session, official_id: int):
    """
    Get assignments assigned to a specific official.
    """
    return db.query(Assignment).filter(Assignment.official_id == official_id).all()

def create_assignment(db: Session, assignment_in: AssignmentCreate):
    """
    Create a new assignment, update the complaint status to 'Assigned', 
    and log the 'Assigned' status update inside status_history.
    All operations are executed inside a single transaction.
    """
    try:
        # Create Assignment
        db_assignment = Assignment(
            complaint_id=assignment_in.complaint_id,
            official_id=assignment_in.official_id,
            engineer_id=assignment_in.engineer_id,
            assignment_status=assignment_in.assignment_status,
            remarks=assignment_in.remarks
        )
        db.add(db_assignment)
        
        # Update complaint status to "Assigned"
        db_complaint = db.query(Complaint).filter(Complaint.complaint_id == assignment_in.complaint_id).first()
        if db_complaint:
            db_complaint.status = ComplaintStatusEnum.ASSIGNED
            
        # Log to status history
        updater_id = assignment_in.official_id or assignment_in.engineer_id
        db_status = StatusHistory(
            complaint_id=assignment_in.complaint_id,
            status=ComplaintStatusEnum.ASSIGNED,
            updated_by=updater_id,
            remarks=assignment_in.remarks or "Complaint assigned to staff."
        )
        db.add(db_status)
        
        db.commit()
        db.refresh(db_assignment)
        return db_assignment
    except Exception as e:
        db.rollback()
        raise e

def update_assignment(db: Session, db_assignment: Assignment, assignment_in: AssignmentUpdate):
    """
    Update assignment details.
    """
    try:
        if assignment_in.official_id is not None:
            db_assignment.official_id = assignment_in.official_id
        if assignment_in.engineer_id is not None:
            db_assignment.engineer_id = assignment_in.engineer_id
        if assignment_in.assignment_status is not None:
            db_assignment.assignment_status = assignment_in.assignment_status
        if assignment_in.remarks is not None:
            db_assignment.remarks = assignment_in.remarks
            
        db.commit()
        db.refresh(db_assignment)
        return db_assignment
    except Exception as e:
        db.rollback()
        raise e

def delete_assignment(db: Session, db_assignment: Assignment):
    """
    Delete an assignment.
    """
    try:
        db.delete(db_assignment)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
