"""
SERP-Master API - Main Application
FastAPI application for SEO auditing and analysis
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.routes import router
from app.api.strategy_routes import router as strategy_router
from app.api.platform_routes import router as platform_router
from app.api.competitive_routes import router as competitive_router
from app.api.content_routes import router as content_router
from app.api.automation_routes import router as automation_router
from app.api.generation_routes import router as generation_router
from app.api.entity_routes import router as entity_router
from app.services.dataforseo_client import DataForSEOClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events for FastAPI app
    Runs on startup and shutdown
    """
    # Startup
    logger.info("Starting SERP-Master API")

    # Test DataForSEO connection
    try:
        client = DataForSEOClient()
        logger.info("DataForSEO client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize DataForSEO client: {str(e)}")

    yield

    # Shutdown
    logger.info("Shutting down SERP-Master API")


# Create FastAPI app
app = FastAPI(
    title="SERP-Master API",
    description="AI-Powered SEO Auditing and Analysis Tool",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3005").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)
app.include_router(strategy_router)
app.include_router(platform_router)
app.include_router(competitive_router)
app.include_router(content_router)
app.include_router(automation_router)
app.include_router(generation_router)
app.include_router(entity_router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return {
        "error": "Internal server error",
        "detail": str(exc)
    }


# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """
    Log all incoming requests
    """
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} - {response.status_code}")
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
