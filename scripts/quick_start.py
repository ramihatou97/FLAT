"""Quick start version of Medical Knowledge Platform without database dependencies"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Medical Knowledge Platform",
    version="3.0.0",
    description="Personal medical encyclopedia with AI-powered content synthesis",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "app": "Medical Knowledge Platform",
        "version": "3.0.0",
        "status": "running",
        "message": "Welcome to the Medical Knowledge Platform! (Quick Start Mode)",
        "docs_url": "/docs",
        "features": [
            "✅ Basic FastAPI server running",
            "✅ API documentation available",
            "✅ CORS configured",
            "📚 Ready for library uploads",
            "🔑 API keys configured in .env",
            "🌐 Web interface access available"
        ],
        "next_steps": [
            "1. Check API documentation at /docs",
            "2. Test health endpoint at /api/health",
            "3. Start uploading documents to reference_library/",
            "4. Use web interfaces for AI providers",
            "5. Import content via content_import_interface.html"
        ]
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Medical Knowledge Platform",
        "version": "3.0.0",
        "mode": "quick_start",
        "database": "not connected (quick start mode)",
        "api_keys": "configured",
        "ready_for": [
            "Document uploads",
            "Web interface content import",
            "AI provider integration testing"
        ]
    }

@app.get("/api/status")
async def status():
    return {
        "platform": "operational",
        "features": {
            "ai_providers": "ready (check .env for keys)",
            "content_integration": "available",
            "web_interfaces": "accessible",
            "document_library": "ready for uploads"
        },
        "access_points": {
            "api_docs": "http://localhost:8000/docs",
            "content_import": "content_import_interface.html",
            "ai_dashboard": "ai_providers_dashboard.html"
        }
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("🏥 Starting Medical Knowledge Platform in Quick Start Mode...")
    logger.info("📖 API Documentation: http://localhost:8000/docs")
    logger.info("🌐 Platform Status: http://localhost:8000/")
    logger.info("💻 Content Import: Open content_import_interface.html")
    uvicorn.run(app, host="0.0.0.0", port=8000)