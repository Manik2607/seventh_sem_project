from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, BigInteger, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.complaint import Complaint
    from app.models.user import User

class ComplaintImage(Base):
    __tablename__ = "complaint_images"

    image_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.complaint_id"), nullable=False)
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    image_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    uploaded_by: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"), nullable=True)
    uploaded_at: Mapped[datetime | None] = mapped_column(DateTime, default=func.now(), nullable=True)

    # Relationships
    complaint: Mapped[Complaint] = relationship("Complaint", back_populates="images")
    uploader: Mapped[User | None] = relationship("User", foreign_keys=[uploaded_by])
