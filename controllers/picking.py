from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import get_db
from .schemas import AddItemRequest, PickingCompleteResponse
from services import OrderServiceClient
import models as crud
import logging
from datetime import datetime
from utils.auth import get_current_agent

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["picking"])
order_client = OrderServiceClient()


@router.post("/picking/start/{order_id}")
async def start_picking(order_id: int, db: Session = Depends(get_db)):
    """Start picking for an order"""
    try:
        order = crud.get_order(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.picking_status != "NOT_STARTED":
            raise HTTPException(status_code=400, detail="Picking already started or completed")
        order = crud.update_order_picking_status(db, order_id, "IN_PROGRESS")
        crud.create_picking_activity(db, order_id, "PICKING_STARTED")
        return {"status": "success", "message": "Picking started", "order_id": order_id, "reference_number": order.reference_number}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting picking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/picking/add-item")
async def add_item_to_picking(request: AddItemRequest, db: Session = Depends(get_db)):
    """Add item to picking"""
    try:
        order = crud.get_order(db, request.order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.picking_status != "IN_PROGRESS":
            raise HTTPException(status_code=400, detail="Order picking not in progress")
        
        items = crud.get_order_items(db, request.order_id)
        order_item = next((item for item in items if item.product_id == request.product_id), None)
        if not order_item:
            raise HTTPException(status_code=404, detail="Product not in this order")
        
        quantity = request.quantity or 1.0
        new_quantity = order_item.picked_quantity + quantity
        if new_quantity > order_item.ordered_quantity:
            raise HTTPException(status_code=400, detail=f"Picked quantity ({new_quantity}) exceeds ordered quantity ({order_item.ordered_quantity})")
        
        crud.update_order_item_picked_quantity(db, order_item.id, new_quantity)
        crud.create_picking_activity(db, request.order_id, f"ITEM_PICKED", details={"product_id": request.product_id, "method": request.method, "quantity": quantity})
        
        return {
            "status": "success",
            "message": "Item added to picking",
            "order_id": request.order_id,
            "product_id": request.product_id,
            "picked_quantity": new_quantity,
            "ordered_quantity": order_item.ordered_quantity,
            "remaining": order_item.ordered_quantity - new_quantity
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/picking/complete/{order_id}", response_model=PickingCompleteResponse)
async def complete_picking(order_id: int, db: Session = Depends(get_db)):
    """Complete picking and pack order"""
    try:
        order = crud.get_order(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.picking_status != "IN_PROGRESS":
            raise HTTPException(status_code=400, detail="Order not in picking progress")
        
        items = crud.get_order_items(db, order_id)
        unpicked_items = [item for item in items if item.picked_quantity < item.ordered_quantity]
        if unpicked_items:
            raise HTTPException(status_code=400, detail=f"{len(unpicked_items)} items not fully picked")
        
        # Create crate label
        items_dict = {str(item.product_id): int(item.picked_quantity) for item in items}
        crud.create_crate_label(db, order_id, f"CRATE-{order.reference_number}", weight=None, items_data=items_dict)
        
        # Update order status to PACKED
        crud.update_order_status(db, order_id, "PACKED")
        crud.update_order_picking_status(db, order_id, "COMPLETED")
        crud.create_picking_activity(db, order_id, "PICKING_COMPLETED")
        
        # Send update to order service
        crates_list = [f"CRATE-{order.reference_number}"]
        package_metadata = {
            "packages": {
                f"CRATE-{order.reference_number}": {
                    "weight": 0,
                    "items": items_dict
                }
            }
        }
        
        order_service_success = order_client.update_order_status(
            order.reference_number,
            "PACKED",
            crates_list,
            package_metadata
        )
        
        # Update inventory
        for item in items:
            try:
                product = crud.get_product_by_external_id(db, item.product_id)
                if product:
                    inventory = crud.get_inventory(db, product.product_id, order.pickup_location_id)
                    if inventory:
                        new_stock = max(0, inventory.stock - item.picked_quantity)
                        crud.update_inventory_stock(db, product.product_id, order.pickup_location_id, new_stock)
                        order_client.update_inventory(product.product_id, order.pickup_location_id, new_stock)
            except Exception as e:
                logger.error(f"Error updating inventory for item {item.product_id}: {str(e)}")
        
        return PickingCompleteResponse(
            status="PACKED",
            message="Order packed and sent to order service",
            order_id=order_id,
            reference_number=order.reference_number
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing picking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/picking/{order_id}/activities")
async def get_picking_activities(order_id: int, db: Session = Depends(get_db)):
    """Get picking activities for an order"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    activities = crud.get_picking_activities(db, order_id)
    return {"order_id": order_id, "reference_number": order.reference_number, "activities": activities}
