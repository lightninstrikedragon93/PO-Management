from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.domain.models import PurchaseOrder, POLineItem, User
from app.domain.schemas.po_schema import POCreate, POUpdate
from app.domain.constants import POStatusEnum
from app.services.workflow_service import POWorkflowEngine
from app.services.permission_service import PermissionService

class POService:
    
    @staticmethod
    def get_po_by_id(db: Session, po_id: int, user: User) -> PurchaseOrder:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        if not po:
            raise ValueError("PO not found")

        if user.role == "requester" and po.creator_id != user.id:
            raise PermissionError("You don't have acces to this purchase order.")
            
        elif user.role == "manager":
            if po.creator_id != user.id and po.status != POStatusEnum.PENDING_MANAGER:
                 raise PermissionError("You don't have acces to this purchase order.")
                 
        elif user.role == "it_rep":
            if po.creator_id != user.id and po.status != POStatusEnum.PENDING_IT:
                 raise PermissionError("You don't have acces to this purchase order.")
                 
        return po
    
    @staticmethod
    def get_pos_for_user(db: Session, user: User):
        """Returneaza lista de PO-uri in functie de rolul utilizatorului"""
        query = db.query(PurchaseOrder)

        if user.role == "requester":
            # Requester-ul vede doar propriile PO-uri
            query = query.filter(PurchaseOrder.creator_id == user.id)
            
        elif user.role == "manager":
            # Managerul vede PO-urile lui sau cele care asteapta aprobare de la el
            query = query.filter(
                or_(
                    PurchaseOrder.creator_id == user.id,
                    PurchaseOrder.status == POStatusEnum.PENDING_MANAGER
                )
            )
            
        elif user.role == "it_rep":
            # IT-ul vede PO-urile lui sau cele care asteapta aprobare IT
            query = query.filter(
                or_(
                    PurchaseOrder.creator_id == user.id,
                    PurchaseOrder.status == POStatusEnum.PENDING_IT
                )
            )
            
        elif user.role in ["finance", "admin"]:
            pass 

        return query.order_by(PurchaseOrder.id.desc()).all()
    
    @staticmethod
    def create_po(db: Session, po_in: POCreate, user_id: int) -> PurchaseOrder:
        calculated_total = sum(item.quantity * item.unit_price for item in po_in.items)

        new_po = PurchaseOrder(
            title=po_in.title,
            description=po_in.description,
            currency=po_in.currency,
            category=po_in.category,
            total_amount=calculated_total,
            status=POStatusEnum.DRAFT, 
            creator_id=user_id
        )
        db.add(new_po)
        db.flush()

        for item_in in po_in.items:
            new_item = POLineItem(
                po_id=new_po.id,
                name=item_in.name,
                quantity=item_in.quantity,
                unit_price=item_in.unit_price
            )
            db.add(new_item)
            
        db.commit()
        db.refresh(new_po)
        return new_po

    @staticmethod
    def update_po(db: Session, po_id: int, po_in: POCreate, user_id: int) -> PurchaseOrder:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        if not po:
            raise ValueError("PO not found")
            
        if po.creator_id != user_id:
            raise PermissionError("Not authorized to edit this PO")
            
        if po.status not in [POStatusEnum.DRAFT, POStatusEnum.NEEDS_REWORK]:
            raise ValueError("Only DRAFT or NEEDS_REWORK POs can be edited")

        calculated_total = sum(item.quantity * item.unit_price for item in po_in.items)

        po.title = po_in.title
        po.description = po_in.description
        po.category = po_in.category
        po.currency = po_in.currency
        po.total_amount = calculated_total
        
        if po.status == POStatusEnum.NEEDS_REWORK:
            po.status = POStatusEnum.DRAFT 

        db.query(POLineItem).filter(POLineItem.po_id == po_id).delete()
        
        for item_in in po_in.items:
            new_item = POLineItem(
                po_id=po.id,
                name=item_in.name,
                quantity=item_in.quantity,
                unit_price=item_in.unit_price
            )
            db.add(new_item)

        db.commit()
        db.refresh(po)
        
        return po

    @staticmethod
    def submit_po(db: Session, po_id: int, user: User) -> PurchaseOrder:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        if not po:
            raise ValueError("PO not found")

        if po.creator_id != user.id:
            raise PermissionError("Just the creator of this PO can submit it")

        if po.status not in [POStatusEnum.DRAFT, POStatusEnum.NEEDS_REWORK]:
            raise ValueError("Just the PO that are in DRAF or NEED REWORK can be submitted.")

        if user.role == "manager":
            if po.category == "IT Equipment":
                po.status = POStatusEnum.PENDING_IT
            else:
                po.status = POStatusEnum.PENDING_FINANCE
        else:
            po.status = POStatusEnum.PENDING_MANAGER

        db.commit()
        db.refresh(po)
        return po

    @staticmethod
    def approve_po(db: Session, po_id: int, user: User, comments: str = None) -> PurchaseOrder:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        if not po:
            raise ValueError("PO not found")

        # Stare corecta PO
        if user.role == "manager" and po.status != POStatusEnum.PENDING_MANAGER:
            raise PermissionError("This PO should'n wait manager's approvel.")
            
        elif user.role == "it_rep" and po.status != POStatusEnum.PENDING_IT:
            raise PermissionError("This PO should'n wait IT's approvel.")
            
        elif user.role == "finance" and po.status != POStatusEnum.PENDING_FINANCE:
            raise PermissionError("This PO should'n wait finance's approvel.")

        # Managerul nu poate aproba propria comanda
        if po.creator_id == user.id and user.role != "finance":
            raise PermissionError("You can't approve your own submition.")

        if user.role == "manager":
             if po.category == "IT Equipment":
                 po.status = POStatusEnum.PENDING_IT
             else:
                 po.status = POStatusEnum.PENDING_FINANCE
                 
        elif user.role == "it_rep":
             po.status = POStatusEnum.PENDING_FINANCE
             
        elif user.role == "finance":
             po.status = POStatusEnum.APPROVED

        db.commit()
        db.refresh(po)
        return po

    @staticmethod
    def reject_po(db: Session, po_id: int, user: User, reason: str) -> PurchaseOrder:
        po = POService.get_po_by_id(db, po_id)
        PermissionService.verify_can_review(po, user)
        
        old_status = po.status
        po.status = POStatusEnum.NEEDS_REWORK
        
        audit = POWorkflowEngine.create_audit_log(po.id, user.id, "REJECT", old_status, POStatusEnum.NEEDS_REWORK, reason)
        db.add(audit)
        db.commit()
        db.refresh(po)
        return po

    @staticmethod
    def invoice_po(db: Session, po_id: int, user: User) -> PurchaseOrder:
        po = POService.get_po_by_id(db, po_id)
        PermissionService.verify_can_invoice(po, user)
        
        old_status = po.status
        po.status = POStatusEnum.INVOICED
        
        audit = POWorkflowEngine.create_audit_log(po.id, user.id, "INVOICE", old_status, POStatusEnum.INVOICED)
        db.add(audit)
        db.commit()
        db.refresh(po)
        return po