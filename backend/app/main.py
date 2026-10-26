import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import get_settings
from backend.app.api.routes.paypal import router as paypal_router

# Configure clean logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("resolveai.app")

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="ResolveAI Backend Service with Policy-Governed PayPal Sandbox Integration",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(paypal_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "environment": settings.PAYPAL_ENV,
        "status": "online",
        "docs": "/docs",
        "paypal_health": "/api/paypal/health"
    }
