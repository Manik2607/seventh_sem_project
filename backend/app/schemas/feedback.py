from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class FeedbackBase(BaseModel):
    complaint_id: int
    citizen_id: int
    rating: int | None = Field(None, ge=1, le=5)
    comments: str | None = None

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackUpdate(BaseModel):
    rating: int | None = Field(None, ge=1, le=5)
    comments: str | None = None

class FeedbackResponse(FeedbackBase):
    feedback_id: int
    submitted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
