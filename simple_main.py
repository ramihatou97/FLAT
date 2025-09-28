"""FastAPI application for Medical Knowledge Platform"""

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import API routers
from src.api import chapters, search, ai, health, research, library, processing, monitoring, key_management, literature, workflow, analytics, docs, content_integration

# Import core services
from src.core.api_key_manager import api_key_manager
from src.services.monitoring_service import monitoring_service
from src.services.semantic_search_engine import semantic_search_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🏥 Starting Neurosurgical Medical Knowledge Platform...")

    try:
        # Initialize API key management system
        await api_key_manager.initialize()
        logger.info("✅ API Key Management system initialized")

        # Initialize semantic search engine with neurosurgical concepts
        logger.info("🧠 Initializing neurosurgical semantic search engine...")
        await semantic_search_engine.initialize_embeddings()
        logger.info("✅ Semantic search engine initialized with medical concepts")

    except Exception as e:
        logger.error(f"❌ Failed to initialize platform services: {e}")
        # Continue startup even if some services fail
        pass

    yield

    # Shutdown
    logger.info("🔄 Shutting down Neurosurgical Medical Platform...")

    try:
        # Cleanup Redis connections
        if api_key_manager.redis_client:
            await api_key_manager.redis_client.close()

    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

app = FastAPI(
    title="Medical Knowledge Platform",
    version="3.0.0",
    description="Personal medical encyclopedia with AI-powered content synthesis",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(chapters.router, prefix="/api/chapters", tags=["chapters"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(research.router, prefix="/api/research", tags=["research"])
app.include_router(library.router, prefix="/api/library", tags=["library"])
app.include_router(processing.router, prefix="/api/processing", tags=["processing"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])
app.include_router(key_management.router, prefix="/api/keys", tags=["key-management"])
app.include_router(literature.router, prefix="/api/literature", tags=["literature"])
app.include_router(workflow.router, prefix="/api/workflow", tags=["workflow"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(docs.router, prefix="/api/docs", tags=["documentation"])
app.include_router(content_integration.router, prefix="/api/content", tags=["content-integration"])
app.include_router(health.router, prefix="/api/health", tags=["health"])

@app.get("/")
async def root():
    return {
        "app": "Medical Knowledge Platform",
        "version": "3.0.0",
        "status": "running",
        "message": "Welcome to the Medical Knowledge Platform!",
        "docs_url": "/docs",
        "features": [
            "Chapter management",
            "Multi-provider AI content generation",
            "Medical literature search (PubMed, Google Scholar)",
            "Document library management",
            "Intelligent chapter generation",
            "Research API integration",
            "Document processing and analysis",
            "AI-powered content extraction",
            "Content enhancement",
            "AI literature analysis and synthesis",
            "Automated systematic review generation",
            "Research conflict detection",
            "Citation network analysis",
            "Evidence quality assessment",
            "Semantic search with 427+ neurosurgical concepts",
            "Research workflow automation",
            "AI-powered hypothesis generation",
            "Study design optimization",
            "Grant proposal assistance",
            "Funding source matching",
            "Predictive analytics dashboard",
            "Research trend analysis",
            "Knowledge gap identification",
            "Citation impact prediction",
            "Market intelligence insights",
            "Collaboration opportunity matching",
            "Unified content integration from all AI providers",
            "Web interface content import and processing",
            "Cross-provider content search and analysis",
            "Automated content consolidation and merging"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
