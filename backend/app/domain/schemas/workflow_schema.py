from pydantic import BaseModel, Field
from typing import Optional

class ApprovePayload(BaseModel):
    comment: Optional[str] = None

class RejectPayload(BaseModel):
    reason: str = Field(..., min_length=3, description="Trebuie sa oferi un motiv pentru Reject (Needs Rework)")