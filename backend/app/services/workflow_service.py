from app.domain.models import PurchaseOrder, AuditLog
from app.domain.constants import POStatusEnum, POCategoryEnum

class POWorkflowEngine:
    
    @staticmethod
    def calculate_submit_transition(po: PurchaseOrder) -> str:
        """Calculeaza urmatorul pas pe baza sumei si categoriei"""
        if po.total_amount < 100:
            # Bypass Manager
            if po.category == POCategoryEnum.IT_EQUIPMENT:
                return POStatusEnum.PENDING_IT
            return POStatusEnum.PENDING_FINANCE
        
        # >= 100 USD merge la manager
        return POStatusEnum.PENDING_MANAGER

    @staticmethod
    def calculate_approve_transition(po: PurchaseOrder) -> str:
        """Calculeaza urmatorul pas dupa o aprobare in functie de pasul curent"""
        if po.status == POStatusEnum.PENDING_MANAGER:
            if po.category == POCategoryEnum.IT_EQUIPMENT:
                return POStatusEnum.PENDING_IT
            return POStatusEnum.PENDING_FINANCE
            
        if po.status == POStatusEnum.PENDING_IT:
            return POStatusEnum.PENDING_FINANCE
            
        if po.status == POStatusEnum.PENDING_FINANCE:
            return POStatusEnum.APPROVED
            
        return po.status

    @staticmethod
    def create_audit_log(po_id: int, actor_id: int, action: str, from_status: str, to_status: str, comments: str = None) -> AuditLog:
        """Creeaza intrarea pentru bucla de review / rework."""
        return AuditLog(
            po_id=po_id,
            actor_id=actor_id,
            action=action,
            from_status=from_status,
            to_status=to_status,
            comments=comments
        )