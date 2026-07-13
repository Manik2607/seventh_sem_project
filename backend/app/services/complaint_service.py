from sqlalchemy.orm import Session
from app.models.complaint import Complaint, ComplaintStatusEnum
from app.models.complaint_image import ComplaintImage
from app.models.status_history import StatusHistory
from app.schemas.complaint import ComplaintCreate, ComplaintUpdate

def get_complaints(db: Session):
    """
    Get all registered complaints.
    """
    return db.query(Complaint).all()

def get_complaint_by_id(db: Session, complaint_id: int):
    """
    Get a complaint by unique ID.
    """
    return db.query(Complaint).filter(Complaint.complaint_id == complaint_id).first()

def get_complaints_by_citizen(db: Session, citizen_id: int):
    """
    Get all complaints filed by a specific citizen.
    """
    return db.query(Complaint).filter(Complaint.citizen_id == citizen_id).all()

def get_complaints_by_status(db: Session, status: ComplaintStatusEnum):
    """
    Get all complaints filtered by status.
    """
    return db.query(Complaint).filter(Complaint.status == status).all()

def get_complaints_by_department(db: Session, department_id: int):
    """
    Get all complaints assigned to a specific department.
    """
    return db.query(Complaint).filter(Complaint.department_id == department_id).all()

def create_complaint(db: Session, complaint_in: ComplaintCreate):
    """
    Create a new complaint, upload image details, and log the initial 'Submitted' status history.
    All operations are executed inside a single database transaction.
    """
    try:
        # 1. Insert into complaints table
        db_complaint = Complaint(
            citizen_id=complaint_in.citizen_id,
            department_id=complaint_in.department_id,
            title=complaint_in.title,
            description=complaint_in.description,
            category=complaint_in.category,
            address=complaint_in.address,
            latitude=complaint_in.latitude,
            longitude=complaint_in.longitude,
            priority=complaint_in.priority,
            status=ComplaintStatusEnum.SUBMITTED
        )
        db.add(db_complaint)
        db.flush()  # Acquire complaint_id for relationships

        # 2. Insert complaint image if image_url is provided
        if complaint_in.image_url:
            db_image = ComplaintImage(
                complaint_id=db_complaint.complaint_id,
                image_url=complaint_in.image_url,
                image_type=complaint_in.image_type,
                uploaded_by=complaint_in.citizen_id
            )
            db.add(db_image)

        # 3. Insert initial status history
        db_history = StatusHistory(
            complaint_id=db_complaint.complaint_id,
            status=ComplaintStatusEnum.SUBMITTED,
            updated_by=complaint_in.citizen_id,
            remarks="Complaint submitted."
        )
        db.add(db_history)

        db.commit()
        db.refresh(db_complaint)
        return db_complaint
    except Exception as e:
        db.rollback()
        raise e

def update_complaint(db: Session, db_complaint: Complaint, complaint_in: ComplaintUpdate):
    """
    Update a complaint's details. If status changes, automatically create a StatusHistory entry.
    All operations are executed inside a single transaction.
    """
    try:
        status_changed = False
        old_status = db_complaint.status
        new_status = complaint_in.status

        if new_status is not None and new_status != old_status:
            status_changed = True

        # Update base fields
        if complaint_in.title is not None:
            db_complaint.title = complaint_in.title
        if complaint_in.description is not None:
            db_complaint.description = complaint_in.description
        if complaint_in.category is not None:
            db_complaint.category = complaint_in.category
        if complaint_in.latitude is not None:
            db_complaint.latitude = complaint_in.latitude
        if complaint_in.longitude is not None:
            db_complaint.longitude = complaint_in.longitude
        if complaint_in.address is not None:
            db_complaint.address = complaint_in.address
        if complaint_in.priority is not None:
            db_complaint.priority = complaint_in.priority
        if complaint_in.department_id is not None:
            db_complaint.department_id = complaint_in.department_id

        # Update status and status history
        if status_changed:
            db_complaint.status = new_status
            db_history = StatusHistory(
                complaint_id=db_complaint.complaint_id,
                status=new_status,
                updated_by=complaint_in.updated_by,
                remarks=complaint_in.remarks or f"Status changed from {old_status.value if old_status else 'None'} to {new_status.value}."
            )
            db.add(db_history)

        db.commit()
        db.refresh(db_complaint)
        return db_complaint
    except Exception as e:
        db.rollback()
        raise e

def delete_complaint(db: Session, db_complaint: Complaint):
    """
    Delete a complaint. Related complaint_images and status_histories are cascade-deleted by SQLAlchemy.
    """
    try:
        db.delete(db_complaint)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
