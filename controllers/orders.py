from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import get_db
from .schemas import OrderCreate, OrderResponse
import models as crud
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["orders"])


@router.post("/orders", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Creation of orders is handled via webhook only to keep canonical data source centralized.
    raise HTTPException(status_code=405, detail="Orders must be created via webhook: POST /packer-order/create")


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/orders", response_model=list[OrderResponse])
async def list_orders(skip: int = 0, limit: int = 100, status: str = None, db: Session = Depends(get_db)):
    orders = crud.get_all_orders(db, skip=skip, limit=limit, status=status)
    return orders


@router.get("/orders/{order_id}/items")
async def get_order_items(order_id: int, db: Session = Depends(get_db)):
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    items = crud.get_order_items(db, order_id)
    return {"order_id": order_id, "items": items}
