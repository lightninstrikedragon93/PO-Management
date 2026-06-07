from fastapi import HTTPException
from app.domain.models import PurchaseOrder, User
from app.domain.constants import POStatusEnum, RoleEnum

class PermissionService:
    
    @staticmethod
    def verify_can_edit_or_submit(po: PurchaseOrder, user: User) -> None:
        """Doar creatorul poate edita/trimite, si doar dac este in DRAFT sau NEEDS_REWORK"""
        if po.creator_id != user.id:
            raise HTTPException(status_code=403, detail="You can only submit or edit your own Purchase Orders.")
        
        if po.status not in [POStatusEnum.DRAFT, POStatusEnum.NEEDS_REWORK]:
            raise HTTPException(status_code=403, detail=f"Cannot edit or submit PO in status {po.status}.")

    @staticmethod
    def verify_can_review(po: PurchaseOrder, user: User) -> None:
        """Verifica daca utilizatorul curent are rolul necesar pentru stadiul curent de aprobare"""
        if po.status == POStatusEnum.PENDING_MANAGER:
            if user.role != RoleEnum.MANAGER:
                raise HTTPException(status_code=403, detail="Manager privileges required for this stage.")
                
        elif po.status == POStatusEnum.PENDING_IT:
            if user.role != RoleEnum.IT_REP:
                raise HTTPException(status_code=403, detail="IT Representative privileges required for this stage.")
                
        elif po.status == POStatusEnum.PENDING_FINANCE:
            if user.role != RoleEnum.FINANCE:
                raise HTTPException(status_code=403, detail="Finance privileges required for this stage.")
                
        else:
            raise HTTPException(status_code=400, detail="PO is not currently pending any review.")

    @staticmethod
    def verify_can_invoice(po: PurchaseOrder, user: User) -> None:
        """Doar Finance poate factura si doar dupa aprobarea final"""
        if po.status != POStatusEnum.APPROVED:
            raise HTTPException(status_code=400, detail="PO must be APPROVED before invoicing.")
            
        if user.role != RoleEnum.FINANCE:
            raise HTTPException(status_code=403, detail="Only Finance can invoice Purchase Orders.")