from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, BigInteger, Text, func, Enum
import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.complaint import Complaint

class NotificationStatusEnum(str, enum.Enum):
    UNREAD = "Unread"
    READ = "Read"

class Notification(Base):
    __tablename__ = "notifications"

    notification_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    complaint_id: Mapped[int | None] = mapped_column(ForeignKey("complaints.complaint_id"), nullable=True)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[NotificationStatusEnum | None] = mapped_column(
        Enum(NotificationStatusEnum, name="notification_status", native_enum=True, values_callable=lambda x: [e.value for e in x]),
        default=NotificationStatusEnum.UNREAD,
        nullable=True
    )
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=func.now(), nullable=True)

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="notifications")
    complaint: Mapped[Complaint | None] = relationship("Complaint")
