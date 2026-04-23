from pydantic import BaseModel
from typing import Dict, Any, List

class HomeTileBase(BaseModel):
    type: str
    size: str
    order: int
    is_active: bool
    content: Dict[str, Any]

class HomeTileCreate(HomeTileBase):
    pass

class HomeTileUpdate(BaseModel):
    type: str | None = None
    size: str | None = None
    order: int | None = None
    is_active: bool | None = None
    content: Dict[str, Any] | None = None

class HomeTileResponse(HomeTileBase):
    id: int

    class Config:
        from_attributes = True

class TileOrderUpdate(BaseModel):
    id: int
    order: int