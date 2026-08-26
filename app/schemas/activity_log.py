from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ActivityLogResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    action: str
    details: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ActivityLogListResponse(BaseModel):
    items: list[ActivityLogResponse]
    total: int
