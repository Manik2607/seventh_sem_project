from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.complaint import Complaint

class Department(Base):
    __tablename__ = "departments"

    department_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    department_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    users: Mapped[List[User]] = relationship("User", back_populates="department")
    complaints: Mapped[List[Complaint]] = relationship("Complaint", back_populates="department")
