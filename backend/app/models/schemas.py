from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class ChatMessage(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    response: str
    tool_calls: Optional[list] = None


class Product(BaseModel):
    id: UUID
    name: str
    category: str
    current_price: float
    image_url: Optional[str] = None


class TrackedItem(BaseModel):
    id: UUID
    product_id: UUID
    target_price: float
    created_at: datetime
    product: Optional[Product] = None


class SimulateRequest(BaseModel):
    item_id: Optional[UUID] = None
