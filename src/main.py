"""Main FastAPI application"""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.database import db_manager
from .api import chapters, search, literature, workflow, research, health

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle"""
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    
    # Startup
    health = await db_manager.health_check()
    if not health:
        logger.error("Database health check failed")
    
    yield
    
    # Shutdown
    await db_manager.close()
    logger.info("Application shutdown complete")

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chapters.router, prefix="/api/chapters", tags=["chapters"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(literature.router, prefix="/api/literature", tags=["literature"])
app.include_router(workflow.router, prefix="/api/workflow", tags=["workflow"])
app.include_router(research.router, prefix="/api/research", tags=["research"])
app.include_router(health.router, prefix="/api/health", tags=["health"])

@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": settings.version,
        "status": "running"
    }
