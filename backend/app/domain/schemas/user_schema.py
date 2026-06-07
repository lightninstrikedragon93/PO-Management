from pydantic import BaseModel, EmailStr
from typing import Optional
from app.domain.constants import RoleEnum

# User
class UserBase(BaseModel):
    email: EmailStr
    role: RoleEnum = RoleEnum.REQUESTER
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True 

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

# Token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"