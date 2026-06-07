from sqlalchemy import Boolean, Column, Enum, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.domain.constants import RoleEnum

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.REQUESTER, nullable=False)
    is_active = Column(Boolean, default=True)

    created_pos = relationship("PurchaseOrder", back_populates="creator")