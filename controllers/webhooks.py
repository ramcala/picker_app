from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from models import get_db
from .schemas import WebhookOrderPayload
import models as crud
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter(tags=["webhooks"])


@router.post("/packer-order/create")
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

    # Extract order/customer details
    customer_id = order_data.get("customerId") or order_data.get("customer", {}).get("id")
    customer_name = order_data.get("customer", {}).get("name", "")

    # Prepare order-level payload dict matching models.create_order
    try:
        amount = float(order_data.get("amount") or 0)
    except Exception:
        amount = 0.0
    try:
        discount = float(order_data.get("discount") or 0)
    except Exception:
        discount = 0.0
    try:
        shipping = float(order_data.get("shipping") or 0)
    except Exception:
        shipping = 0.0

    order_payload = {
        "order_id": order_id,
        "reference_number": reference_number,
        "customer_id": customer_id,
        "customer_name": customer_name,
        "amount": amount,
        "discount": discount,
        "shipping": shipping,
        "status": order_data.get("status", "PENDING"),
        "order_type": order_data.get("type", {}).get("name") if isinstance(order_data.get("type"), dict) else order_data.get("type"),
        "pickup_location_id": (order_data.get("pickupLocation", {}).get("id") if isinstance(order_data.get("pickupLocation"), dict) else order_data.get("pickupLocationId")),
        "preferred_date": order_data.get("preferredDate"),
        "slot_type": order_data.get("slotType"),
        "slot_start_time": order_data.get("slotStartTime"),
        "slot_end_time": order_data.get("slotEndTime"),
        "raw_payload": order_data
    }

    # Create order in DB
    db_order = crud.create_order(db, order_payload)

    # Process items and create products if needed
    items_list = []
    for item_data in order_data.get("items", []):
        try:
            ordered_qty = float(item_data.get("orderDetails", {}).get("orderedQuantity", 0) or 0)
            mrp = float(item_data.get("orderDetails", {}).get("mrp", 0) or 0)
            discount_item = float(item_data.get("orderDetails", {}).get("discount", 0) or 0)

            # Create or get product
            product = _get_or_create_product(db, item_data)
            if product:
                items_list.append({
                    "product_id": product.product_id,
                    "ordered_quantity": ordered_qty,
                    "mrp": mrp,
                    "discount": discount_item
                })
        except Exception as e:
            logger.error(f"Error processing item {item_data.get('id')}: {str(e)}")

    if not items_list:
        # If there are no valid items, rollback the created order to avoid orphan rows
        try:
            db.delete(db_order)
            db.commit()
        except Exception:
            pass
        raise ValueError("Order has no valid items")

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

    # Create new product dict matching models.create_product
    product_payload = {
        "product_id": product_id,
        "client_item_id": item_data.get("clientItemId") or item_data.get("client_item_id"),
        "name": item_data.get("name"),
        "slug": item_data.get("slug"),
        "images": item_data.get("images") or item_data.get("imagesExtra"),
        "status": item_data.get("status", "ENABLED"),
        "average_rating": float(item_data.get("averageRating") or 0),
        "total_reviews": int(item_data.get("totalReviews") or 0),
        "sold_by_weight": bool(item_data.get("soldByWeight") or False)
    }

    try:
        product = crud.create_product(db, product_payload)

        # Create inventory entries from store-specific data (if provided)
        store_data_list = item_data.get("storeSpecificData", []) or []
        for store_data in store_data_list:
            try:
                store_id = store_data.get("storeId") or store_data.get("store_id") or 0
                inventory_payload = {
                    "product_id": product_id,
                    "store_id": store_id,
                    "stock": float(store_data.get("stock", 0) or 0),
                    "tax": store_data.get("tax"),
                    "mrp": float(store_data.get("mrp", 0) or 0),
                    "discount": float(store_data.get("discount", 0) or 0),
                    "aisle": (store_data.get("location") or {}).get("aisle") if isinstance(store_data.get("location"), dict) else store_data.get("aisle"),
                    "rack": (store_data.get("location") or {}).get("rack") if isinstance(store_data.get("location"), dict) else store_data.get("rack"),
                    "shelf": (store_data.get("location") or {}).get("position") if isinstance(store_data.get("location"), dict) else store_data.get("shelf"),
                    "unit": store_data.get("unit", 1),
                    "status": store_data.get("status", "ENABLED"),
                    "location_data": store_data.get("location")
                }
                crud.create_or_update_inventory(db, inventory_payload)
            except Exception as e:
                logger.warning(f"Error creating inventory for product {product_id}: {str(e)}")

        return product
    except Exception as e:
        logger.error(f"Error creating product {product_id}: {str(e)}")
        return None


@router.post("/webhook/product")
async def webhook_product(request: Request, db: Session = Depends(get_db)):
    """Create or update product(s) via webhook. Accepts a product dict, {'product': {...}} wrapper or a list."""
    payload = await request.json()
    if isinstance(payload, dict) and payload.get("product"):
        products = payload.get("product")
    elif isinstance(payload, list):
        products = payload
    else:
        products = [payload]

    results = []
    for p in products:
        try:
            product_payload = {
                "product_id": p.get("id") or p.get("product_id"),
                "client_item_id": p.get("clientItemId") or p.get("client_item_id"),
                "name": p.get("name"),
                "slug": p.get("slug"),
                "images": p.get("images"),
                "status": p.get("status", "ENABLED"),
                "average_rating": p.get("averageRating", 0),
                "total_reviews": p.get("totalReviews", 0),
                "sold_by_weight": p.get("soldByWeight", False)
            }
            db_product = crud.create_product(db, product_payload)
            results.append({"product_id": db_product.product_id, "id": db_product.id})

            # Optionally process store-specific inventory if provided
            for store_data in p.get("storeSpecificData", []) or []:
                try:
                    inv = {
                        "product_id": p.get("id"),
                        "store_id": store_data.get("storeId") or store_data.get("store_id") or 0,
                        "stock": float(store_data.get("stock", 0) or 0),
                        "tax": store_data.get("tax"),
                        "mrp": float(store_data.get("mrp", 0) or 0),
                        "discount": float(store_data.get("discount", 0) or 0),
                        "aisle": (store_data.get("location") or {}).get("aisle") if isinstance(store_data.get("location"), dict) else store_data.get("aisle"),
                        "rack": (store_data.get("location") or {}).get("rack") if isinstance(store_data.get("location"), dict) else store_data.get("rack"),
                        "shelf": (store_data.get("location") or {}).get("position") if isinstance(store_data.get("location"), dict) else store_data.get("shelf"),
                        "unit": store_data.get("unit", 1),
                        "status": store_data.get("status", "ENABLED"),
                        "location_data": store_data.get("location")
                    }
                    crud.create_or_update_inventory(db, inv)
                except Exception as e:
                    logger.warning(f"Error creating inventory for product webhook: {str(e)}")

        except Exception as e:
            logger.error(f"Error processing product webhook entry: {str(e)}")
            results.append({"error": str(e), "payload": p})

    return {"status": "ok", "processed": len(results), "results": results}


@router.post("/webhook/inventory")
async def webhook_inventory(request: Request, db: Session = Depends(get_db)):
    """Create or update inventory via webhook. Accepts JSON payload for single or multiple inventory items."""
    payload = await request.json()
    items = payload if isinstance(payload, list) else (payload.get("inventory") or [payload])
    results = []
    for it in items:
        try:
            inv_payload = {
                "product_id": it.get("product_id") or it.get("productId") or it.get("id"),
                "store_id": it.get("store_id") or it.get("storeId") or it.get("store") or 0,
                "stock": float(it.get("stock") or 0),
                "tax": it.get("tax"),
                "mrp": float(it.get("mrp") or 0),
                "discount": float(it.get("discount") or 0),
                "aisle": it.get("aisle"),
                "rack": it.get("rack"),
                "shelf": it.get("shelf"),
                "unit": it.get("unit", 1),
                "status": it.get("status", "ENABLED"),
                "location_data": it.get("location")
            }
            db_inv = crud.create_or_update_inventory(db, inv_payload)
            results.append({"product_id": it.get("product_id") or it.get("productId") or it.get("id"), "store_id": db_inv.store_id, "stock": db_inv.stock})
        except Exception as e:
            logger.error(f"Error processing inventory webhook entry: {str(e)}")
            results.append({"error": str(e), "payload": it})
    return {"status": "ok", "processed": len(results), "results": results}


@router.post("/webhook/customer")
async def webhook_customer(request: Request, db: Session = Depends(get_db)):
    """Create or update customer via webhook. Accepts single customer dict or list."""
    payload = await request.json()
    customers = payload if isinstance(payload, list) else (payload.get("customer") or [payload])
    results = []
    for c in customers:
        try:
            cust_payload = {
                "customer_id": c.get("id") or c.get("customerId") or c.get("customer_id"),
                "name": c.get("name"),
                "email": (c.get("email") or (c.get("defaultEmail") or {}).get("email")),
                "phone": (c.get("phone") or (c.get("defaultPhone") or {}).get("phone")),
                "address": (c.get("defaultAddress") or {}).get("address"),
                "city": (c.get("defaultAddress") or {}).get("city"),
                "pincode": (c.get("defaultAddress") or {}).get("pincode"),
                "customer_metadata": c.get("metaData") or c.get("meta_data")
            }
            db_cust = crud.create_customer(db, cust_payload)
            results.append({"customer_id": db_cust.customer_id, "id": db_cust.id})
        except Exception as e:
            logger.error(f"Error processing customer webhook entry: {str(e)}")
            results.append({"error": str(e), "payload": c})
    return {"status": "ok", "processed": len(results), "results": results}


@router.post("/webhook/order/update")
async def webhook_order_update(request: Request, db: Session = Depends(get_db)):
    """Update an order partially (status/details) via webhook."""
    payload = await request.json()
    # Accept either {"order": {...}} or list or direct dict
    orders = payload if isinstance(payload, list) else (payload.get("order") or [payload])
    results = []
    for o in orders:
        try:
            ref = o.get("referenceNumber") or o.get("reference_number") or o.get("reference")
            # Try find by reference or external id
            order_obj = None
            if ref:
                order_obj = crud.get_order_by_reference(db, ref)
            if not order_obj and o.get("id"):
                order_obj = crud.get_order_by_external_id(db, o.get("id"))
            if not order_obj:
                results.append({"error": "order_not_found", "payload": o})
                continue

            update_fields = {}
            if o.get("status"):
                update_fields["status"] = o.get("status")
            if o.get("picking_status"):
                update_fields["picking_status"] = o.get("picking_status")
            if o.get("packed_at"):
                update_fields["packed_at"] = o.get("packed_at")
            if o.get("packageMetaData"):
                update_fields["raw_payload"] = {**(order_obj.raw_payload or {}), "packageMetaData": o.get("packageMetaData")}

            # Apply updates
            if update_fields:
                for k, v in update_fields.items():
                    setattr(order_obj, k, v)
                db.add(order_obj)
                db.commit()
                db.refresh(order_obj)
            results.append({"reference": order_obj.reference_number, "id": order_obj.order_id, "status": order_obj.status})
        except Exception as e:
            logger.error(f"Error processing order update webhook entry: {str(e)}")
            results.append({"error": str(e), "payload": o})
    return {"status": "ok", "processed": len(results), "results": results}
