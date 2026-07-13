from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, BigInteger, Text, func, Enum
import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.complaint import Complaint
    from app.models.user import User

class AssignmentStatusEnum(str, enum.Enum):
    ASSIGNED = "Assigned"
    ACCEPTED = "Accepted"
    COMPLETED = "Completed"

class Assignment(Base):
    __tablename__ = "assignments"

    assignment_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.complaint_id"), nullable=False)
    official_id: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"), nullable=True)
    engineer_id: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"), nullable=True)
    assignment_status: Mapped[AssignmentStatusEnum | None] = mapped_column(
        Enum(AssignmentStatusEnum, name="assignment_status", native_enum=True, values_callable=lambda x: [e.value for e in x]),
        nullable=True
    )
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime, default=func.now(), nullable=True)

    # Relationships
    complaint: Mapped[Complaint] = relationship("Complaint", back_populates="assignments")
    official: Mapped[User | None] = relationship("User", foreign_keys=[official_id], back_populates="assigned_official_tasks")
    engineer: Mapped[User | None] = relationship("User", foreign_keys=[engineer_id], back_populates="assigned_engineer_tasks")
