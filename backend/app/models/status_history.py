from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, BigInteger, Text, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.complaint import ComplaintStatusEnum

if TYPE_CHECKING:
    from app.models.complaint import Complaint
    from app.models.user import User

class StatusHistory(Base):
    __tablename__ = "status_history"

    status_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.complaint_id"), nullable=False)
    status: Mapped[ComplaintStatusEnum | None] = mapped_column(
        Enum(ComplaintStatusEnum, name="complaint_status", native_enum=True, values_callable=lambda x: [e.value for e in x]),
        nullable=True
    )
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"), nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)

    # Relationships
    complaint: Mapped[Complaint] = relationship("Complaint", back_populates="status_histories")
    updater: Mapped[User | None] = relationship("User", foreign_keys=[updated_by], back_populates="status_updates")
