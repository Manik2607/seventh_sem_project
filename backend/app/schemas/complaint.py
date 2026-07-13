from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.models.complaint import ComplaintPriorityEnum, ComplaintStatusEnum
from app.schemas.complaint_image import ComplaintImageResponse
from app.schemas.status_history import StatusHistoryResponse

class ComplaintBase(BaseModel):
    title: str
    description: str
    category: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    address: str | None = None

class ComplaintCreate(ComplaintBase):
    citizen_id: int
    image_url: str | None = None
    image_type: str | None = None
    priority: ComplaintPriorityEnum | None = None
    department_id: int | None = None

class ComplaintUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    status: ComplaintStatusEnum | None = None
    priority: ComplaintPriorityEnum | None = None
    latitude: float | None = None
    longitude: float | None = None
    address: str | None = None
    department_id: int | None = None
    updated_by: int | None = None
    remarks: str | None = None

class ComplaintResponse(ComplaintBase):
    complaint_id: int
    citizen_id: int
    department_id: int | None
    priority: ComplaintPriorityEnum | None
    status: ComplaintStatusEnum | None
    created_at: datetime | None
    updated_at: datetime | None
    images: list[ComplaintImageResponse] = []
    status_histories: list[StatusHistoryResponse] = []

    model_config = ConfigDict(from_attributes=True)
