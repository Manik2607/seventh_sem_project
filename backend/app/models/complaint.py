from __future__ import annotations
from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import String, DateTime, Text, Numeric, BigInteger, ForeignKey, func, Enum
import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.department import Department
    from app.models.complaint_image import ComplaintImage
    from app.models.assignment import Assignment
    from app.models.status_history import StatusHistory
    from app.models.feedback import Feedback

class ComplaintPriorityEnum(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class ComplaintStatusEnum(str, enum.Enum):
    SUBMITTED = "Submitted"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "In Progress"
    VERIFIED = "Verified"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

class Complaint(Base):
    __tablename__ = "complaints"

    complaint_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    citizen_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.department_id"), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    priority: Mapped[ComplaintPriorityEnum | None] = mapped_column(
        Enum(ComplaintPriorityEnum, name="complaint_priority", native_enum=True, values_callable=lambda x: [e.value for e in x]),
        nullable=True
    )
    status: Mapped[ComplaintStatusEnum | None] = mapped_column(
        Enum(ComplaintStatusEnum, name="complaint_status", native_enum=True, values_callable=lambda x: [e.value for e in x]),
        nullable=True
    )
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=func.now(), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )

    # Relationships
    reporter: Mapped[User] = relationship("User", foreign_keys=[citizen_id], back_populates="reported_complaints")
    department: Mapped[Department | None] = relationship("Department", back_populates="complaints")
    images: Mapped[List[ComplaintImage]] = relationship("ComplaintImage", back_populates="complaint", cascade="all, delete-orphan")
    assignments: Mapped[List[Assignment]] = relationship("Assignment", back_populates="complaint", cascade="all, delete-orphan")
    status_histories: Mapped[List[StatusHistory]] = relationship("StatusHistory", back_populates="complaint", cascade="all, delete-orphan")
    feedbacks: Mapped[List[Feedback]] = relationship("Feedback", foreign_keys="[Feedback.complaint_id]", back_populates="complaint", cascade="all, delete-orphan")
