from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.domain.constants import POStatusEnum, POCategoryEnum
from .user_schema import UserResponse

# Items
class POLineItemBase(BaseModel):
    name: str = Field (min_length=2, max_length=100)
    quantity: int = Field(gt=0, description="Cantitatea trebuie sa fie mai mare ca zero")
    unit_price: float = Field(gt=0, description="Pretul trebuie sa fie strcit pozitiv")

class POLineItemCreate(POLineItemBase):
    pass

class POLineItemResponse(POLineItemBase):
    id: int
    po_id: int

    class Config:
        orm_mode = True

class POLineItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = Field(None, gt=0)
    unit_price: Optional[float] = Field(None, gt=0)

# Audit Logs
class AuditLogResponse(BaseModel):
    id: int
    po_id: int
    action: str
    from_status: POStatusEnum
    to_status: POStatusEnum
    comments: Optional[str] = None
    created_at: datetime
    actor: UserResponse 

    class Config:
        orm_mode = True

# Purchase Orders
class POBase(BaseModel):
    title: str
    description: Optional[str] = None
    currency: str = "USD"
    category: POCategoryEnum

class POCreate(POBase):
    items: List[POLineItemCreate] = Field(..., min_length=1, description="Comanda trebuie sa contina cel putin un item")

class POUpdate(POBase):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[POCategoryEnum] = None
    items: List[POLineItemCreate]

class POResponse(POBase):
    id: int
    total_amount: float
    status: POStatusEnum
    created_at: datetime
    updated_at: datetime
    
    creator_id: int
    items: List[POLineItemResponse] = []
    
    class Config:
        orm_mode = True

class PODetailResponse(POResponse):
    creator: UserResponse
    audit_logs: List[AuditLogResponse] = []

class GenericMessageResponse(BaseModel):
    message: str
    
    id: Optional[int] = None 