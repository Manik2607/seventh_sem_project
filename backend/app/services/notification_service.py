from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationUpdate

def get_notifications(db: Session):
    """
    Get all notifications.
    """
    return db.query(Notification).all()

def get_notification_by_id(db: Session, notification_id: int):
    """
    Get a notification by unique ID.
    """
    return db.query(Notification).filter(Notification.notification_id == notification_id).first()

def get_notifications_by_user(db: Session, user_id: int):
    """
    Get all notifications for a specific user.
    """
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()

def create_notification(db: Session, notification_in: NotificationCreate):
    """
    Create a new notification record in the database.
    """
    try:
        db_notification = Notification(
            user_id=notification_in.user_id,
            complaint_id=notification_in.complaint_id,
            title=notification_in.title,
            message=notification_in.message,
            status=notification_in.status
        )
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification
    except Exception as e:
        db.rollback()
        raise e

def update_notification(db: Session, db_notification: Notification, notification_in: NotificationUpdate):
    """
    Update details of an existing notification (e.g. status from Unread to Read).
    """
    try:
        if notification_in.title is not None:
            db_notification.title = notification_in.title
        if notification_in.message is not None:
            db_notification.message = notification_in.message
        if notification_in.status is not None:
            db_notification.status = notification_in.status
            
        db.commit()
        db.refresh(db_notification)
        return db_notification
    except Exception as e:
        db.rollback()
        raise e

def delete_notification(db: Session, db_notification: Notification):
    """
    Delete a notification.
    """
    try:
        db.delete(db_notification)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
