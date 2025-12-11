from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import (
    get_db, Agent, create_agent, get_agent_by_username, 
    get_all_agents, get_agent
)
from .schemas import AgentRegister, AgentResponse, TokenResponse
from utils.auth import create_access_token, verify_password, hash_password, oauth2_scheme, get_current_agent
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


@router.post("/register", response_model=AgentResponse)
async def register_agent(agent_data: AgentRegister, db: Session = Depends(get_db)):
    """Register a new picker agent"""
    existing = get_agent_by_username(db, agent_data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = hash_password(agent_data.password)
    db_agent = create_agent(
        db,
        agent_data.username,
        hashed_password,
        agent_data.full_name,
        agent_data.email,
        agent_data.phone
    )
    return db_agent


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate picker agent and return JWT token"""
    agent = get_agent_by_username(db, form_data.username)
    if not agent or not verify_password(form_data.password, agent.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=60*24)
    access_token = create_access_token(data={"sub": agent.username}, expires_delta=access_token_expires)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        agent=agent
    )


@router.get("/", response_model=list[AgentResponse])
async def list_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all agents"""
    agents = get_all_agents(db, skip=skip, limit=limit)
    return agents


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent_by_id(agent_id: int, db: Session = Depends(get_db)):
    """Get agent by ID"""
    agent = get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.get("/me", response_model=AgentResponse)
async def read_current_agent(current_agent=Depends(get_current_agent)):
    """Get current authenticated agent info"""
    return current_agent

