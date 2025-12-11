"""
Agent Model for Picker/Packer agents
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import Session
from datetime import datetime
from .database import Base
import logging

logger = logging.getLogger(__name__)


class Agent(Base):
    """Agent table"""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    status = Column(String, default="ACTIVE")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== CRUD Operations ====================

def create_agent(db: Session, username: str, hashed_password: str, full_name: str = None,
                 email: str = None, phone: str = None) -> Agent:
    """Create a new agent"""
    agent = Agent(
        username=username,
        password_hash=hashed_password,
        full_name=full_name,
        email=email,
        phone=phone,
        status="ACTIVE"
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


def get_agent(db: Session, agent_id: int) -> Agent:
    """Get an agent by ID"""
    return db.query(Agent).filter(Agent.id == agent_id).first()


def get_agent_by_username(db: Session, username: str) -> Agent:
    """Get an agent by username"""
    return db.query(Agent).filter(Agent.username == username).first()


def get_all_agents(db: Session, skip: int = 0, limit: int = 100) -> list:
    """Get all agents with pagination"""
    return db.query(Agent).offset(skip).limit(limit).all()


def update_agent_status(db: Session, agent_id: int, status: str) -> Agent:
    """Update agent status"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if agent:
        agent.status = status
        agent.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(agent)
    return agent


def update_agent_password(db: Session, agent_id: int, hashed_password: str) -> Agent:
    """Update agent password"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if agent:
        agent.password_hash = hashed_password
        agent.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(agent)
    return agent

