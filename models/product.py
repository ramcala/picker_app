"""
Product Model
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship, Session
from datetime import datetime
from .database import Base
import logging

logger = logging.getLogger(__name__)


class Product(Base):
    """Product table"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, unique=True, index=True)
    client_item_id = Column(String, index=True)
    name = Column(String, index=True)
    slug = Column(String, unique=True, index=True)
    images = Column(JSON, nullable=True)
    status = Column(String, default="ENABLED")
    average_rating = Column(Float, default=0)
    total_reviews = Column(Integer, default=0)
    sold_by_weight = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = relationship("OrderItem", back_populates="product")
    inventories = relationship("Inventory", back_populates="product")


# ==================== CRUD Operations ====================

def create_product(db: Session, product_data: dict) -> Product:
    """Create or update a product"""
    db_product = db.query(Product).filter(Product.product_id == product_data.get("product_id")).first()
    if db_product:
        for key, value in product_data.items():
            setattr(db_product, key, value)
        db_product.updated_at = datetime.utcnow()
    else:
        db_product = Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_product(db: Session, product_id: int) -> Product:
    """Get a product by database ID"""
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_external_id(db: Session, external_product_id: int) -> Product:
    """Get a product by external product_id"""
    return db.query(Product).filter(Product.product_id == external_product_id).first()


def get_all_products(db: Session, skip: int = 0, limit: int = 100) -> list:
    """Get all products with pagination"""
    return db.query(Product).offset(skip).limit(limit).all()


def delete_product(db: Session, product_id: int) -> bool:
    """Delete a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
        return True
    return False
