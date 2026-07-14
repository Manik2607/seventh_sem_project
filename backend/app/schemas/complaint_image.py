from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ComplaintImageBase(BaseModel):
    complaint_id: int
    image_url: str
    image_type: str | None = None
    uploaded_by: int | None = None

class ComplaintImageCreate(ComplaintImageBase):
    pass

class ComplaintImageResponse(ComplaintImageBase):
    image_id: int
    uploaded_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
