import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

DUMMYJSON_URL = os.getenv("DUMMYJSON_URL", "https://dummyjson.com")
DUMMYJSON_TIMEOUT = float(os.getenv("DUMMYJSON_TIMEOUT", "10"))

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60

# A product with this many units or fewer is "low on stock" (see docs/PRODUCTS.md)
LOW_STOCK_THRESHOLD = max(0, int(os.getenv("LOW_STOCK_THRESHOLD", "10")))

CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
