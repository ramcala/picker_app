"""
Order and OrderItem Models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship, Session
from datetime import datetime
from .database import Base
import logging

logger = logging.getLogger(__name__)


class Order(Base):
    """Order table"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, unique=True, index=True)
    reference_number = Column(String, unique=True, index=True)
    customer_id = Column(String, index=True)
    customer_name = Column(String)
    amount = Column(Float)
    discount = Column(Float, default=0)
    shipping = Column(Float, default=0)
    extra_charges = Column(Float, default=0)
    status = Column(String, default="PENDING")
    payment_status = Column(String, default="PENDING")
    order_type = Column(String, default="PICKUP")
    pickup_location_id = Column(Integer, nullable=True)
    preferred_date = Column(String, nullable=True)
    slot_type = Column(String, default="ASAP")
    slot_start_time = Column(String, nullable=True)
    slot_end_time = Column(String, nullable=True)
    picking_status = Column(String, default="NOT_STARTED")
    packed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    raw_payload = Column(JSON, nullable=True)
    
    # Relationships
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    picking_activities = relationship("PickingActivity", back_populates="order", cascade="all, delete-orphan")
    crate_labels = relationship("CrateLabel", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """Order Item table"""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    product_item_id = Column(Integer)
    ordered_quantity = Column(Float)
    picked_quantity = Column(Float, default=0)
    status = Column(String, default="PENDING")
    mrp = Column(Float)
    discount = Column(Float, default=0)
    unit = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


# ==================== Order CRUD Operations ====================

def create_order(db: Session, order_data: dict) -> Order:
    """Create a new order"""
    db_order = Order(**order_data)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def get_order(db: Session, order_id: int) -> Order:
    """Get an order by database ID"""
    return db.query(Order).filter(Order.id == order_id).first()


def get_order_by_external_id(db: Session, external_order_id: int) -> Order:
    """Get an order by external order_id"""
    return db.query(Order).filter(Order.order_id == external_order_id).first()


def get_order_by_reference(db: Session, reference_number: str) -> Order:
    """Get an order by reference number"""
    return db.query(Order).filter(Order.reference_number == reference_number).first()


def get_all_orders(db: Session, skip: int = 0, limit: int = 100, status: str = None) -> list:
    """Get all orders with optional status filter"""
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    return query.offset(skip).limit(limit).all()


def get_orders_by_status(db: Session, status: str, skip: int = 0, limit: int = 100) -> list:
    """Get orders by status"""
    return db.query(Order).filter(Order.status == status).offset(skip).limit(limit).all()


def update_order_status(db: Session, order_id: int, status: str) -> Order:
    """Update order status"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = status
        order.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(order)
    return order


def update_order_picking_status(db: Session, order_id: int, picking_status: str) -> Order:
    """Update order picking status"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.picking_status = picking_status
        order.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(order)
    return order


def pack_order(db: Session, order_id: int) -> Order:
    """Mark order as packed"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = "PACKED"
        order.picking_status = "COMPLETED"
        order.packed_at = datetime.utcnow()
        order.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(order)
    return order


# ==================== Order Item CRUD Operations ====================

def create_order_item(db: Session, order_id: int, item_data: dict) -> OrderItem:
    """Create an order item from dict"""
    from .product import get_product_by_external_id
    
    product_id = item_data.get("product_id")
    product = get_product_by_external_id(db, product_id)
    if not product:
        raise ValueError(f"Product {product_id} not found")
    
    db_item = OrderItem(
        order_id=order_id,
        product_id=product.id,
        product_item_id=product_id,
        ordered_quantity=item_data.get("ordered_quantity", 0),
        mrp=item_data.get("mrp", 0),
        discount=item_data.get("discount", 0)
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_order_items(db: Session, order_id: int) -> list:
    """Get all items for an order"""
    return db.query(OrderItem).filter(OrderItem.order_id == order_id).all()


def get_order_item(db: Session, order_item_id: int) -> OrderItem:
    """Get a specific order item"""
    return db.query(OrderItem).filter(OrderItem.id == order_item_id).first()


def update_order_item_picked_quantity(db: Session, order_item_id: int, picked_quantity: float) -> OrderItem:
    """Update the picked quantity of an order item"""
    item = db.query(OrderItem).filter(OrderItem.id == order_item_id).first()
    if item:
        item.picked_quantity = picked_quantity
        item.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(item)
    return item
