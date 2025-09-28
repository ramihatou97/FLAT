"""
Monitoring API Endpoints
Real-time system health, metrics, and performance monitoring
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
import asyncio
from datetime import datetime, timedelta
import psutil
import json

from ..services.monitoring_service import monitoring_service
from ..core.database import get_async_session

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health/detailed")
async def get_detailed_health():
    """Get comprehensive system health status"""

    try:
        health_data = await monitoring_service.get_system_health()
        return {
            "status": "healthy" if health_data["overall_healthy"] else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "details": health_data
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.get("/metrics/system")
async def get_system_metrics():
    """Get real-time system resource metrics"""

    try:
        metrics = await monitoring_service.get_system_metrics()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"System metrics failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system metrics")

@router.get("/metrics/database")
async def get_database_metrics():
    """Get database connection pool and performance metrics"""

    try:
        db_metrics = await monitoring_service.get_database_metrics()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "database": db_metrics
        }
    except Exception as e:
        logger.error(f"Database metrics failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get database metrics")

@router.get("/metrics/ai-services")
async def get_ai_service_metrics():
    """Get AI service health, performance, and cost metrics"""

    try:
        ai_metrics = await monitoring_service.get_ai_service_metrics()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "ai_services": ai_metrics
        }
    except Exception as e:
        logger.error(f"AI service metrics failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AI service metrics")

@router.get("/metrics/api-endpoints")
async def get_api_metrics():
    """Get API endpoint performance and usage metrics"""

    try:
        api_metrics = await monitoring_service.get_api_metrics()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "api_endpoints": api_metrics
        }
    except Exception as e:
        logger.error(f"API metrics failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get API metrics")

@router.get("/metrics/cache")
async def get_cache_metrics():
    """Get Redis cache performance metrics"""

    try:
        cache_metrics = await monitoring_service.get_cache_metrics()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cache": cache_metrics
        }
    except Exception as e:
        logger.error(f"Cache metrics failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cache metrics")

@router.get("/metrics/tasks")
async def get_task_metrics():
    """Get background task queue metrics"""

    try:
        task_metrics = await monitoring_service.get_task_metrics()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "tasks": task_metrics
        }
    except Exception as e:
        logger.error(f"Task metrics failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get task metrics")

@router.get("/dashboard")
async def get_monitoring_dashboard():
    """Get comprehensive monitoring dashboard data"""

    try:
        dashboard_data = await monitoring_service.get_dashboard_data()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "dashboard": dashboard_data
        }
    except Exception as e:
        logger.error(f"Dashboard data failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")

@router.get("/alerts")
async def get_active_alerts():
    """Get active system alerts and warnings"""

    try:
        alerts = await monitoring_service.get_active_alerts()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "alerts": alerts
        }
    except Exception as e:
        logger.error(f"Alerts retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alerts")

@router.get("/circuit-breakers")
async def get_circuit_breaker_status():
    """Get circuit breaker status for all services"""

    try:
        circuit_status = await monitoring_service.get_circuit_breaker_status()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "circuit_breakers": circuit_status
        }
    except Exception as e:
        logger.error(f"Circuit breaker status failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get circuit breaker status")

@router.get("/performance/history")
async def get_performance_history(hours: int = 24):
    """Get historical performance data"""

    try:
        if hours > 168:  # Max 1 week
            hours = 168

        history = await monitoring_service.get_performance_history(hours)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "hours": hours,
            "history": history
        }
    except Exception as e:
        logger.error(f"Performance history failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance history")

@router.post("/alerts/acknowledge/{alert_id}")
async def acknowledge_alert(alert_id: str):
    """Acknowledge a specific alert"""

    try:
        result = await monitoring_service.acknowledge_alert(alert_id)
        return {
            "acknowledged": result,
            "alert_id": alert_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Alert acknowledgment failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to acknowledge alert")

@router.get("/status/summary")
async def get_status_summary():
    """Get high-level system status summary"""

    try:
        summary = await monitoring_service.get_status_summary()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Status summary failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get status summary")

@router.get("/diagnostics/ai-provider/{provider}")
async def run_ai_provider_diagnostic(provider: str):
    """Run diagnostic test for specific AI provider"""

    try:
        if provider not in ["openai", "gemini", "claude", "perplexity"]:
            raise HTTPException(status_code=400, detail="Invalid AI provider")

        diagnostic_result = await monitoring_service.run_ai_provider_diagnostic(provider)
        return {
            "provider": provider,
            "timestamp": datetime.utcnow().isoformat(),
            "diagnostic": diagnostic_result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI provider diagnostic failed: {e}")
        raise HTTPException(status_code=500, detail="Diagnostic test failed")

@router.get("/logs/recent")
async def get_recent_logs(level: str = "ERROR", limit: int = 100):
    """Get recent application logs"""

    try:
        if limit > 1000:
            limit = 1000

        logs = await monitoring_service.get_recent_logs(level, limit)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "limit": limit,
            "logs": logs
        }
    except Exception as e:
        logger.error(f"Log retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recent logs")