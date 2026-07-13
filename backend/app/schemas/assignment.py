from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.assignment import AssignmentStatusEnum

class AssignmentBase(BaseModel):
    complaint_id: int
    official_id: int | None = None
    engineer_id: int | None = None
    remarks: str | None = None

class AssignmentCreate(AssignmentBase):
    assignment_status: AssignmentStatusEnum = AssignmentStatusEnum.ASSIGNED

class AssignmentUpdate(BaseModel):
    official_id: int | None = None
    engineer_id: int | None = None
    assignment_status: AssignmentStatusEnum | None = None
    remarks: str | None = None

class AssignmentResponse(AssignmentBase):
    assignment_id: int
    assignment_status: AssignmentStatusEnum | None
    assigned_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
