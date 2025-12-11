"""
Customer Model
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import Session
from datetime import datetime
from .database import Base
import logging

logger = logging.getLogger(__name__)


class Customer(Base):
    """Customer table"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True)
    name = Column(String)
    email = Column(String, index=True)
    phone = Column(String)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    customer_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== CRUD Operations ====================

def create_customer(db: Session, customer_data: dict) -> Customer:
    """Create or update a customer"""
    db_customer = db.query(Customer).filter(Customer.customer_id == customer_data.get("customer_id")).first()
    if db_customer:
        for key, value in customer_data.items():
            setattr(db_customer, key, value)
        db_customer.updated_at = datetime.utcnow()
    else:
        db_customer = Customer(**customer_data)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def get_customer(db: Session, customer_id: int) -> Customer:
    """Get a customer by database ID"""
    return db.query(Customer).filter(Customer.id == customer_id).first()


def get_customer_by_external_id(db: Session, external_customer_id: str) -> Customer:
    """Get a customer by external customer_id"""
    return db.query(Customer).filter(Customer.customer_id == external_customer_id).first()


def get_all_customers(db: Session, skip: int = 0, limit: int = 100) -> list:
    """Get all customers with pagination"""
    return db.query(Customer).offset(skip).limit(limit).all()


def delete_customer(db: Session, customer_id: int) -> bool:
    """Delete a customer"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer:
        db.delete(customer)
        db.commit()
        return True
    return False
