"""
Pydantic schemas for request/response validation - Controllers schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# ==================== Product Schemas ====================
class ProductCreate(BaseModel):
    product_id: int
    client_item_id: Optional[str] = None
    name: str
    slug: str
    images: Optional[List[str]] = None
    status: str = "ENABLED"
    average_rating: Optional[float] = 0
    total_reviews: Optional[int] = 0
    sold_by_weight: Optional[bool] = False

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    id: Optional[int] = None
    product_id: int
    name: str
    slug: str

    class Config:
        from_attributes = True


# ==================== Inventory Schemas ====================
class InventoryCreate(BaseModel):
    product_id: int
    store_id: int
    stock: float = 0
    mrp: Optional[float] = None
    discount: Optional[float] = None


class InventoryResponse(BaseModel):
    id: Optional[int] = None
    product_id: int
    store_id: int
    stock: float


# ==================== Order Schemas ====================
class OrderCreate(BaseModel):
    order_id: int
    reference_number: str
    customer_id: str
    status: str = "PENDING"
    amount: Optional[str] = None


class OrderResponse(BaseModel):
    id: Optional[int] = None
    order_id: int
    reference_number: str
    customer_id: str
    status: str

    class Config:
        from_attributes = True


# ==================== Agent Schemas ====================
class AgentRegister(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class AgentLogin(BaseModel):
    username: str
    password: str


class AgentResponse(BaseModel):
    id: Optional[int] = None
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    agent: AgentResponse


# ==================== Picking Schemas ====================
class AddItemRequest(BaseModel):
    order_id: int
    product_id: int
    method: str = "manual"
    quantity: Optional[float] = None


class PickingCompleteResponse(BaseModel):
    status: str
    message: str
    order_id: int
    reference_number: str


# ==================== Webhook Schemas ====================
class WebhookOrderPayload(BaseModel):
    code: int
    status: str
    data: Dict[str, Any]


# ==================== Health Check ====================
class HealthResponse(BaseModel):
    status: str
    version: Optional[str] = None

