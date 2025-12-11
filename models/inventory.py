"""
Inventory Model
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship, Session
from datetime import datetime
from .database import Base
import logging

logger = logging.getLogger(__name__)


class Inventory(Base):
    """Inventory table"""
    __tablename__ = "inventories"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    store_id = Column(Integer, index=True)
    stock = Column(Float, default=0)
    tax = Column(String, nullable=True)
    mrp = Column(Float, nullable=True)
    discount = Column(Float, nullable=True)
    unit = Column(Integer, default=1)
    aisle = Column(String, nullable=True)
    rack = Column(String, nullable=True)
    shelf = Column(String, nullable=True)
    status = Column(String, default="ENABLED")
    location_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="inventories")


# ==================== CRUD Operations ====================

def create_or_update_inventory(db: Session, inventory_data: dict) -> Inventory:
    """Create or update inventory"""
    from .product import get_product_by_external_id
    
    product_id = inventory_data.get("product_id")
    store_id = inventory_data.get("store_id")
    
    product = get_product_by_external_id(db, product_id)
    if not product:
        raise ValueError(f"Product {product_id} not found")
    
    db_inventory = db.query(Inventory).filter(
        Inventory.product_id == product.id,
        Inventory.store_id == store_id
    ).first()
    
    if db_inventory:
        for key, value in inventory_data.items():
            if key != 'product_id':
                setattr(db_inventory, key, value)
        db_inventory.product_id = product.id
    else:
        db_inventory = Inventory(product_id=product.id, **{k: v for k, v in inventory_data.items() if k != 'product_id'})
    
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


def get_inventory(db: Session, product_id: int, store_id: int) -> Inventory:
    """Get inventory for a specific product and store"""
    from .product import get_product_by_external_id
    
    product = get_product_by_external_id(db, product_id)
    if not product:
        return None
    
    return db.query(Inventory).filter(
        Inventory.product_id == product.id,
        Inventory.store_id == store_id
    ).first()


def update_inventory_stock(db: Session, product_id: int, store_id: int, new_stock: float) -> Inventory:
    """Update inventory stock"""
    from .product import get_product_by_external_id
    
    product = get_product_by_external_id(db, product_id)
    if not product:
        raise ValueError(f"Product {product_id} not found")
    
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product.id,
        Inventory.store_id == store_id
    ).first()
    
    if not inventory:
        raise ValueError(f"Inventory not found for product {product_id} and store {store_id}")
    
    inventory.stock = new_stock
    inventory.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(inventory)
    return inventory
