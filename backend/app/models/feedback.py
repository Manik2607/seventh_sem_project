from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, BigInteger, Text, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.complaint import Complaint
    from app.models.user import User

class Feedback(Base):
    __tablename__ = "feedback"

    feedback_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.complaint_id"), nullable=False)
    citizen_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, default=func.now(), nullable=True)

    # Relationships
    complaint: Mapped[Complaint] = relationship("Complaint", back_populates="feedbacks")
    user: Mapped[User] = relationship("User", foreign_keys=[citizen_id], back_populates="feedbacks")
