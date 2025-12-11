"""
Picking Activity and Crate Label Models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship, Session
from datetime import datetime
from .database import Base
import logging

logger = logging.getLogger(__name__)


class PickingActivity(Base):
    """Picking Activity log table"""
    __tablename__ = "picking_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    product_id = Column(Integer, index=True)
    quantity = Column(Float)
    picking_method = Column(String)
    picker_agent_id = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    picked_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="picking_activities")


class CrateLabel(Base):
    """Crate Label table"""
    __tablename__ = "crate_labels"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    crate_label = Column(String, unique=True, index=True)
    weight = Column(Float, nullable=True)
    items_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="crate_labels")


# ==================== Picking Activity CRUD Operations ====================

def create_picking_activity(
    db: Session,
    order_id: int,
    action: str,
    product_id: int = None,
    quantity: float = None,
    agent_id: int = None,
    details: dict = None
) -> PickingActivity:
    """Create a picking activity log entry"""
    activity = PickingActivity(
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
        picking_method=action,
        picker_agent_id=agent_id,
        details=details or {}
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def get_picking_activities(db: Session, order_id: int) -> list:
    """Get all picking activities for an order"""
    return db.query(PickingActivity).filter(PickingActivity.order_id == order_id).all()


# ==================== Crate Label CRUD Operations ====================

def create_crate_label(
    db: Session,
    order_id: int,
    crate_label: str,
    weight: float = None,
    items_data: dict = None
) -> CrateLabel:
    """Create a crate label"""
    label = CrateLabel(
        order_id=order_id,
        crate_label=crate_label,
        weight=weight,
        items_data=items_data or {}
    )
    db.add(label)
    db.commit()
    db.refresh(label)
    return label


def get_crate_labels(db: Session, order_id: int) -> list:
    """Get all crate labels for an order"""
    return db.query(CrateLabel).filter(CrateLabel.order_id == order_id).all()


def get_crate_label_by_label(db: Session, crate_label: str) -> CrateLabel:
    """Get a crate label by label string"""
    return db.query(CrateLabel).filter(CrateLabel.crate_label == crate_label).first()
