from pydantic import BaseModel, Field
from typing import Optional, List


class CategoryCreate(BaseModel):
    parent_id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None
    status: Optional[str] = None


class CategoryInfo(BaseModel):
    id: int
    parent_id: Optional[int]
    name: str
    description: str
    sort_order: int
    status: str
    children: List["CategoryInfo"] = []

    class Config:
        from_attributes = True
