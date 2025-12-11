import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./picker_app.db")

# External Services
ORDER_SERVICE_HOST = os.getenv("ORDER_SERVICE_HOST", "http://localhost:8001")
ORDER_SERVICE_USER_ID = os.getenv("ORDER_SERVICE_USER_ID", "1")
ORGANIZATION_ID = os.getenv("ORGANIZATION_ID", "5")

# Application
DEBUG = os.getenv("DEBUG", "True") == "True"
APP_NAME = "Picker App"
API_VERSION = "1.0.0"

# JWT / Auth
# SECRET_KEY should be set in environment for production
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-to-a-strong-secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24)))  # default 24 hours

# Misc
FRONTEND_DIR = os.getenv("FRONTEND_DIR", "frontend")
