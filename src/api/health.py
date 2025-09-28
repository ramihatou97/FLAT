"""
Health Check API Endpoints
Simple system health monitoring
"""

from fastapi import APIRouter
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Medical Platform API",
        "version": "3.0.0",
        "environment": "development"
    }

@router.get("/status")
async def detailed_status():
    """Detailed system status"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": {
                "status": "healthy",
                "version": "3.0.0"
            },
            "ai_service": {
                "status": "healthy",
                "provider": "openai"
            },
            "search_service": {
                "status": "healthy",
                "type": "simple"
            },
            "database": {
                "status": "pending",
                "note": "Database integration in progress"
            }
        },
        "uptime": "operational",
        "features": {
            "chapter_management": True,
            "ai_content_generation": True,
            "search": True,
            "pdf_processing": False  # Not yet implemented
        }
    }