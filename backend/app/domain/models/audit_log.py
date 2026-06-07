from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Enum, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.domain.constants import POStatusEnum

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False) 
    
    action = Column(String, nullable=False)
    from_status = Column(Enum(POStatusEnum), nullable=False)
    to_status = Column(Enum(POStatusEnum), nullable=False)
    
    comments = Column(String) # motiv reject
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    po = relationship("PurchaseOrder", back_populates="audit_logs")
    actor = relationship("User")