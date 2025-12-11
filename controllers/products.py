from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from models import get_db, create_product, get_product, get_all_products, create_or_update_inventory, get_inventory
from .schemas import ProductCreate, ProductResponse, InventoryCreate, InventoryResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["products"])


@router.post("/products", response_model=ProductResponse)
async def create_product_endpoint(product: ProductCreate, db: Session = Depends(get_db)):
    try:
        db_product = create_product(db, product.dict())
        return db_product
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/products", response_model=list[ProductResponse])
async def list_products(skip: int = Query(0), limit: int = Query(100), db: Session = Depends(get_db)):
    products = get_all_products(db, skip=skip, limit=limit)
    return products


@router.post("/inventory", response_model=InventoryResponse)
async def create_inventory_endpoint(inventory: InventoryCreate, db: Session = Depends(get_db)):
    try:
        db_inventory = create_or_update_inventory(db, inventory.dict())
        return db_inventory
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating inventory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inventory/{product_id}/{store_id}", response_model=InventoryResponse)
async def get_inventory_endpoint(product_id: int, store_id: int, db: Session = Depends(get_db)):
    inventory = get_inventory(db, product_id, store_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory

