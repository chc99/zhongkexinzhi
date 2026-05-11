from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RejectRequest(BaseModel):
    reason: str = Field(..., min_length=1)


class BatchIdsRequest(BaseModel):
    ids: List[int] = Field(..., min_length=1)


class AuditLogInfo(BaseModel):
    id: int
    reviewer_id: int
    action: str
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class VersionInfo(BaseModel):
    id: int
    version: int
    change_type: str
    changed_by: int
    remark: str
    created_at: datetime

    class Config:
        from_attributes = True
