import os
from datetime import timedelta

# Load config from environment
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./backend/dev.db")

# Secret for JWT - override in production
SECRET_KEY = os.environ.get("SECRET_KEY", "p4stdiscm-distrib-ft")
ALGORITHM = "HS256"

# Magic numbers and timeouts (centralized)
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.environ.get("ACCESS_TOKEN_EXPIRE_SECONDS", 900))  # 15 minutes
REFRESH_TOKEN_EXPIRE_SECONDS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_SECONDS", 7 * 24 * 3600))  # 7 days
MAX_LOGIN_ATTEMPTS = int(os.environ.get("MAX_LOGIN_ATTEMPTS", 5))
LOCKOUT_DURATION_SECONDS = int(os.environ.get("LOCKOUT_DURATION_SECONDS", 15 * 60))  # 15 minutes

# Rate limit config (used if you add slowapi + redis)
RATE_LIMIT = os.environ.get("RATE_LIMIT", "5/minute")

# CORS origins - set the frontend origin here in production
# For development, allow common ports (5173 for Vite, 8080 for build servers, localhost)
CORS_ORIGINS = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:8080,http://127.0.0.1:5173,http://127.0.0.1:8080"
).split(",")
