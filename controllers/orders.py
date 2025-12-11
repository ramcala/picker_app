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
    try:
        existing = crud.get_order_by_external_id(db, order.order_id)
        if existing:
            raise HTTPException(status_code=409, detail="Order already exists")
        db_order = crud.create_order(db, order)
        return db_order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


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

