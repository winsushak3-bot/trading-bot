from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class TicketMessageBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)

class TicketMessageCreate(TicketMessageBase):
    pass

class TicketMessageResponse(TicketMessageBase):
    id: int
    ticket_id: int
    sender: str
    created_at: datetime

    class Config:
        from_attributes = True

class TicketResponse(BaseModel):
    id: int
    user_id: int
    user_nick: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TicketWithMessages(TicketResponse):
    messages: List[TicketMessageResponse] = []

class SupportCountsResponse(BaseModel):
    new: int
    active: int
    closed: int
