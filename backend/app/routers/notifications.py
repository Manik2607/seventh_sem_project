from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.notification import NotificationCreate, NotificationUpdate, NotificationResponse
from app.schemas.response import StandardResponse
from app.services import notification_service, user_service, complaint_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("", response_model=StandardResponse[NotificationResponse], status_code=status.HTTP_201_CREATED)
def create_notification(notification_in: NotificationCreate, db: Session = Depends(get_db)):
    """
    Create a new notification record.
    Validates that the target user and associated complaint (if provided) exist.
    """
    # Validate target user existence
    user = user_service.get_user_by_id(db, notification_in.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Target user with ID {notification_in.user_id} does not exist."
        )

    # Validate complaint existence if provided
    if notification_in.complaint_id is not None:
        complaint = complaint_service.get_complaint_by_id(db, notification_in.complaint_id)
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Associated complaint with ID {notification_in.complaint_id} does not exist."
            )

    db_notification = notification_service.create_notification(db, notification_in)
    return StandardResponse(
        success=True,
        message="Notification created successfully.",
        data=db_notification
    )

@router.get("", response_model=StandardResponse[List[NotificationResponse]])
def get_notifications(db: Session = Depends(get_db)):
    """
    List all notifications.
    """
    notifications = notification_service.get_notifications(db)
    return StandardResponse(
        success=True,
        message="Notifications retrieved successfully.",
        data=notifications
    )

@router.get("/{user_id}", response_model=StandardResponse[List[NotificationResponse]])
def get_notifications_by_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all notifications targeting a specific user.
    """
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found."
        )
    notifications = notification_service.get_notifications_by_user(db, user_id)
    return StandardResponse(
        success=True,
        message=f"Notifications for user {user_id} retrieved successfully.",
        data=notifications
    )

@router.put("/{id}", response_model=StandardResponse[NotificationResponse])
def update_notification(id: int, notification_in: NotificationUpdate, db: Session = Depends(get_db)):
    """
    Update details of an existing notification (e.g. marking it as Read).
    """
    db_notification = notification_service.get_notification_by_id(db, id)
    if not db_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with ID {id} not found."
        )
    updated_notification = notification_service.update_notification(db, db_notification, notification_in)
    return StandardResponse(
        success=True,
        message="Notification updated successfully.",
        data=updated_notification
    )

@router.delete("/{id}", response_model=StandardResponse[dict])
def delete_notification(id: int, db: Session = Depends(get_db)):
    """
    Delete a specific notification by ID.
    """
    db_notification = notification_service.get_notification_by_id(db, id)
    if not db_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with ID {id} not found."
        )
    notification_service.delete_notification(db, db_notification)
    return StandardResponse(
        success=True,
        message="Notification deleted successfully.",
        data={}
    )
