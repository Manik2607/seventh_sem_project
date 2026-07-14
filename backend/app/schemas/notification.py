from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.notification import NotificationStatusEnum

class NotificationBase(BaseModel):
    user_id: int
    complaint_id: int | None = None
    title: str | None = None
    message: str | None = None

class NotificationCreate(NotificationBase):
    status: NotificationStatusEnum = NotificationStatusEnum.UNREAD

class NotificationUpdate(BaseModel):
    title: str | None = None
    message: str | None = None
    status: NotificationStatusEnum | None = None

class NotificationResponse(NotificationBase):
    notification_id: int
    status: NotificationStatusEnum | None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
