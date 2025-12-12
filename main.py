import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path

from config import APP_NAME, API_VERSION, DEBUG, DATABASE_URL
from models import Base, engine, Product, Inventory, Order, OrderItem, PickingActivity, CrateLabel, Agent as AgentModel, Customer
from controllers.schemas import HealthResponse
import controllers.products as controllers_products
import controllers.orders as controllers_orders
import controllers.picking as controllers_picking
import controllers.webhooks as controllers_webhooks
import controllers.agents as controllers_agents

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Startup/Shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {APP_NAME} v{API_VERSION}")
    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {APP_NAME}")


# Create FastAPI app
app = FastAPI(
    title=APP_NAME,
    version=API_VERSION,
    description="A full-featured picker app for managing order picking and packing workflow",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from controllers
app.include_router(controllers_products.router)
app.include_router(controllers_orders.router)
app.include_router(controllers_picking.router)
app.include_router(controllers_webhooks.router)
app.include_router(controllers_agents.router)

# Mount static and templates folders
from fastapi.staticfiles import StaticFiles
app.mount('/static', StaticFiles(directory='frontend/static'), name='static')


# ===== UI Routes =====
@app.get("/ui")
async def serve_ui():
    """Serve the main UI page"""
    ui_path = Path(__file__).parent / "frontend" / "templates" / "index.html"
    return FileResponse(ui_path)


@app.get("/")
async def root():
    """Redirect root to the UI."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/ui")


# ===== Health Check =====
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=API_VERSION,
        database="connected"
    )


# ===== Exception Handlers =====
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(status_code=exc.status_code, content={
        "code": exc.status_code,
        "status": "ERROR",
        "message": exc.detail
    })


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(status_code=500, content={
        "code": 500,
        "status": "ERROR",
        "message": "Internal server error"
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=80,
        reload=DEBUG,
        log_level="debug" if DEBUG else "info"
    )
