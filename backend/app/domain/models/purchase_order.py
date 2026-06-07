from sqlalchemy import Column, DateTime, Enum, Integer, Numeric, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.domain.constants import POCategoryEnum, POStatusEnum
from datetime import datetime, timezone

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    total_amount = Column(Numeric(10, 2), nullable=False) 
    currency = Column(String, default="USD")
    category = Column(Enum(POCategoryEnum), nullable=False) 
    
    status = Column(Enum(POStatusEnum), default=POStatusEnum.DRAFT, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    creator_id = Column(Integer, ForeignKey("users.id"))
    
    creator = relationship("User", back_populates="created_pos")
    items = relationship("POLineItem", back_populates="po", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="po")

class POLineItem(Base):
    __tablename__ = "po_line_items"
    
    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    
    po = relationship("PurchaseOrder", back_populates="items")