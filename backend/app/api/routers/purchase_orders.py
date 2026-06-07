from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.domain.models import User
from app.domain.schemas.po_schema import POCreate, POResponse, POUpdate, PODetailResponse
from app.domain.schemas.workflow_schema import ApprovePayload, RejectPayload
from app.services.po_service import POService
from app.domain.models.purchase_order import PurchaseOrder

router = APIRouter(prefix="/pos", tags=["Purchase Orders"])

@router.post("", response_model=POResponse, status_code=status.HTTP_201_CREATED)
def create_purchase_order(
    po_in: POCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return POService.create_po(db, po_in, current_user.id)

@router.get("/{po_id}", response_model=PODetailResponse)
def get_purchase_order(
    po_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return POService.get_po_by_id(db, po_id, current_user)

@router.get("", response_model=List[POResponse])
def get_all_pos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    return POService.get_pos_for_user(db=db, user=current_user)

@router.put("/{po_id}", response_model=POResponse)
def update_purchase_order(
    po_id: int,
    po_in: POUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return POService.update_po(db, po_id, po_in, current_user.id)


@router.post("/{po_id}/submit", response_model=POResponse)
def submit_purchase_order(
    po_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return POService.submit_po(db, po_id, current_user)

@router.post("/{po_id}/approve", response_model=POResponse)
def approve_purchase_order(
    po_id: int,
    payload: ApprovePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return POService.approve_po(db, po_id, current_user, payload.comment)

@router.post("/{po_id}/reject", response_model=POResponse)
def reject_purchase_order(
    po_id: int,
    payload: RejectPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return POService.reject_po(db, po_id, current_user, payload.reason)

@router.post("/{po_id}/invoice", response_model=POResponse)
def invoice_purchase_order(
    po_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return POService.invoice_po(db, po_id, current_user)