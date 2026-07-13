from __future__ import annotations
from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, BigInteger, func, Enum
import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.complaint import Complaint
    from app.models.assignment import Assignment
    from app.models.status_history import StatusHistory
    from app.models.notification import Notification
    from app.models.feedback import Feedback

class UserRoleEnum(str, enum.Enum):
    Citizen = "Citizen"
    Official = "Official"
    Engineer = "Engineer"
    Admin = "Admin"

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRoleEnum] = mapped_column(
        Enum(UserRoleEnum, name="user_role", native_enum=True, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.department_id"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=func.now(), nullable=True)

    # Relationships
    department: Mapped[Department | None] = relationship("Department", back_populates="users")
    
    # Complaints reported by this citizen
    reported_complaints: Mapped[List[Complaint]] = relationship(
        "Complaint", 
        foreign_keys="[Complaint.citizen_id]", 
        back_populates="reporter"
    )
    
    # Tasks where user is the assigned Official
    assigned_official_tasks: Mapped[List[Assignment]] = relationship(
        "Assignment", 
        foreign_keys="[Assignment.official_id]", 
        back_populates="official"
    )

    # Tasks where user is the assigned Engineer
    assigned_engineer_tasks: Mapped[List[Assignment]] = relationship(
        "Assignment", 
        foreign_keys="[Assignment.engineer_id]", 
        back_populates="engineer"
    )
    
    notifications: Mapped[List[Notification]] = relationship("Notification", back_populates="user")
    feedbacks: Mapped[List[Feedback]] = relationship("Feedback", foreign_keys="[Feedback.citizen_id]", back_populates="user")
    status_updates: Mapped[List[StatusHistory]] = relationship("StatusHistory", foreign_keys="[StatusHistory.updated_by]", back_populates="updater")
