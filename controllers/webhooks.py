from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import get_db
from .schemas import WebhookOrderPayload, OrderCreate, ProductCreate, InventoryCreate
import models as crud
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter(tags=["webhooks"])


@router.post("/webhook/order")
async def receive_order(payload: WebhookOrderPayload, db: Session = Depends(get_db)):
    """Receive order from order service via webhook"""
    try:
        if payload.code != 200 or payload.status != "SUCCESS":
            return {"code": 400, "status": "INVALID_PAYLOAD", "message": "Webhook payload is invalid"}

        orders_container = None
        if isinstance(payload.data, dict) and "order" in payload.data:
            orders_container = payload.data["order"]
        elif isinstance(payload.data, dict) and "data" in payload.data and isinstance(payload.data["data"], dict) and "order" in payload.data["data"]:
            orders_container = payload.data["data"]["order"]
        else:
            return {"code": 400, "status": "INVALID_PAYLOAD", "message": "Webhook payload missing order data"}

        orders = orders_container
        if not isinstance(orders, list):
            orders = [orders]

        results = []
        for order_data in orders:
            try:
                result = _process_order(db, order_data)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing order: {str(e)}")
                results.append({"order_id": order_data.get("id"), "status": "FAILED", "error": str(e)})

        return {"code": 200, "status": "SUCCESS", "message": f"Processed {len(results)} orders", "results": results}

    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return {"code": 500, "status": "ERROR", "message": str(e)}


def _process_order(db: Session, order_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single order from webhook"""
    order_id = order_data.get("id")
    reference_number = order_data.get("referenceNumber")
    
    # Check if order already exists
    existing = crud.get_order_by_external_id(db, order_id)
    if existing:
        return {"order_id": order_id, "reference_number": reference_number, "status": "ALREADY_EXISTS"}
    
    # Extract order details
    customer_id = order_data.get("customerId", "")
    customer_name = order_data.get("customer", {}).get("name", "Unknown")
    
    # Process items and create products if needed
    items_list = []
    for item_data in order_data.get("items", []):
        try:
            ordered_qty = float(item_data.get("orderDetails", {}).get("orderedQuantity", 0))
            mrp = float(item_data.get("orderDetails", {}).get("mrp", 0))
            discount = float(item_data.get("orderDetails", {}).get("discount", 0))
            
            # Create or get product
            product = _get_or_create_product(db, item_data)
            if product:
                items_list.append({
                    "product_id": product.product_id,
                    "ordered_quantity": ordered_qty,
                    "mrp": mrp,
                    "discount": discount
                })
        except Exception as e:
            logger.error(f"Error processing item {item_data.get('id')}: {str(e)}")
    
    if not items_list:
        raise ValueError("Order has no valid items")
    
    # Create order
    order_create = OrderCreate(
        order_id=order_id,
        reference_number=reference_number,
        customer_id=customer_id,
        status=order_data.get("status", "PENDING"),
        amount=order_data.get("amount"),
        discount=order_data.get("discount"),
        shipping=order_data.get("shipping")
    )
    
    db_order = crud.create_order(db, order_create)
    
    # Create order items
    for item_info in items_list:
        try:
            crud.create_order_item(db, db_order.id, item_info)
        except Exception as e:
            logger.error(f"Error creating order item: {str(e)}")
    
    return {
        "order_id": order_id,
        "reference_number": reference_number,
        "status": "SUCCESS",
        "items_count": len(items_list)
    }


def _get_or_create_product(db: Session, item_data: Dict[str, Any]):
    """Get or create a product from item data"""
    product_id = item_data.get("id")
    
    # Check if product already exists
    existing = crud.get_product_by_external_id(db, product_id)
    if existing:
        return existing
    
    # Create new product
    try:
        product_create = ProductCreate(
            product_id=product_id,
            client_item_id=item_data.get("clientItemId", ""),
            name=item_data.get("name", ""),
            slug=item_data.get("slug", ""),
            images=item_data.get("images", []),
            status=item_data.get("status", "ENABLED"),
            average_rating=float(item_data.get("averageRating", 0)),
            total_reviews=int(item_data.get("totalReviews", 0)),
            sold_by_weight=bool(item_data.get("soldByWeight", False))
        )
        product = crud.create_product(db, product_create)
        
        # Create inventory entries from store-specific data
        store_data_list = item_data.get("storeSpecificData", [])
        if store_data_list:
            for store_data in store_data_list:
                try:
                    inventory_create = InventoryCreate(
                        product_id=product_id,
                        store_id=0,
                        stock=float(store_data.get("stock", 0)),
                        tax=store_data.get("tax"),
                        mrp=float(store_data.get("mrp", 0)),
                        discount=float(store_data.get("discount", 0))
                    )
                    crud.create_or_update_inventory(db, inventory_create)
                except Exception as e:
                    logger.warning(f"Error creating inventory for product {product_id}: {str(e)}")
        
        return product
    except Exception as e:
        logger.error(f"Error creating product {product_id}: {str(e)}")
        return None

