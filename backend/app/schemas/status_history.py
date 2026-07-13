from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.models.complaint import ComplaintStatusEnum

class StatusHistoryBase(BaseModel):
    complaint_id: int
    status: ComplaintStatusEnum
    remarks: str | None = None
    updated_by: int | None = None

class StatusHistoryCreate(StatusHistoryBase):
    pass

class StatusHistoryResponse(StatusHistoryBase):
    status_id: int
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

class StatusHistoryUpdate(BaseModel):
    status: ComplaintStatusEnum | None = None
    remarks: str | None = None
    updated_by: int | None = None
