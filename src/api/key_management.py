"""
API Key Management Endpoints
Monitor, rotate, and manage API keys for neurosurgical AI services
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
from pydantic import BaseModel

from ..core.api_key_manager import api_key_manager

logger = logging.getLogger(__name__)
router = APIRouter()

class KeyRotationRequest(BaseModel):
    service: str
    key_id: str
    reason: str = "manual_rotation"

@router.get("/services/health")
async def get_all_service_health():
    """Get health status for all AI services"""

    try:
        health_data = await api_key_manager.get_all_service_health()

        # Convert ServiceMetrics objects to dictionaries
        result = {}
        for service, metrics in health_data.items():
            result[service] = {
                "service": metrics.service,
                "health": metrics.health.value,
                "total_keys": metrics.total_keys,
                "active_keys": metrics.active_keys,
                "primary_key_id": metrics.primary_key_id,
                "backup_key_ids": metrics.backup_key_ids,
                "daily_cost": metrics.daily_cost,
                "daily_requests": metrics.daily_requests,
                "success_rate": metrics.success_rate,
                "avg_response_time_ms": metrics.avg_response_time_ms,
                "last_health_check": metrics.last_health_check.isoformat(),
                "circuit_breaker_open": metrics.circuit_breaker_open,
                "estimated_monthly_cost": metrics.estimated_monthly_cost
            }

        return {
            "success": True,
            "services": result,
            "total_services": len(result),
            "healthy_services": len([s for s in result.values() if s["health"] == "healthy"])
        }

    except Exception as e:
        logger.error(f"Failed to get service health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get service health")

@router.get("/service/{service}/health")
async def get_service_health(service: str):
    """Get detailed health status for a specific service"""

    try:
        if service not in ["openai", "gemini", "claude", "perplexity"]:
            raise HTTPException(status_code=400, detail="Invalid service name")

        metrics = await api_key_manager.get_service_health(service)

        return {
            "success": True,
            "service": service,
            "health": {
                "status": metrics.health.value,
                "total_keys": metrics.total_keys,
                "active_keys": metrics.active_keys,
                "primary_key_id": metrics.primary_key_id,
                "backup_key_ids": metrics.backup_key_ids,
                "daily_cost": metrics.daily_cost,
                "daily_requests": metrics.daily_requests,
                "success_rate": metrics.success_rate,
                "avg_response_time_ms": metrics.avg_response_time_ms,
                "last_health_check": metrics.last_health_check.isoformat(),
                "circuit_breaker_open": metrics.circuit_breaker_open,
                "estimated_monthly_cost": metrics.estimated_monthly_cost
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get health for {service}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get health for {service}")

@router.get("/service/{service}/budget")
async def get_service_budget(service: str):
    """Get budget status for a specific service"""

    try:
        if service not in ["openai", "gemini", "claude", "perplexity"]:
            raise HTTPException(status_code=400, detail="Invalid service name")

        budget_status = await api_key_manager.check_daily_budget(service)

        return {
            "success": True,
            "budget": budget_status
        }

    except Exception as e:
        logger.error(f"Failed to get budget for {service}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get budget for {service}")

@router.get("/budgets/all")
async def get_all_budgets():
    """Get budget status for all services"""

    try:
        services = ["openai", "gemini", "claude", "perplexity"]
        budgets = {}

        for service in services:
            budget_status = await api_key_manager.check_daily_budget(service)
            budgets[service] = budget_status

        # Calculate totals
        total_cost = sum(budget["daily_cost"] for budget in budgets.values() if budget.get("daily_cost"))
        total_budget = sum(budget["budget_limit"] for budget in budgets.values() if budget.get("budget_limit"))
        total_remaining = total_budget - total_cost

        return {
            "success": True,
            "services": budgets,
            "totals": {
                "daily_cost": round(total_cost, 2),
                "total_budget": round(total_budget, 2),
                "remaining_budget": round(total_remaining, 2),
                "budget_used_percent": round((total_cost / total_budget) * 100, 1) if total_budget > 0 else 0,
                "estimated_monthly_cost": round(total_cost * 30, 2)
            }
        }

    except Exception as e:
        logger.error(f"Failed to get all budgets: {e}")
        raise HTTPException(status_code=500, detail="Failed to get budget information")

@router.post("/service/{service}/rotate")
async def rotate_service_key(service: str, request: KeyRotationRequest):
    """Rotate API key for a specific service"""

    try:
        if service not in ["openai", "gemini", "claude", "perplexity"]:
            raise HTTPException(status_code=400, detail="Invalid service name")

        if request.service != service:
            raise HTTPException(status_code=400, detail="Service name mismatch")

        success = await api_key_manager.rotate_key(service, request.key_id)

        if success:
            return {
                "success": True,
                "message": f"API key rotated successfully for {service}",
                "service": service,
                "key_id": request.key_id,
                "reason": request.reason
            }
        else:
            raise HTTPException(status_code=400, detail="Key rotation failed")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to rotate key for {service}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to rotate key for {service}")

@router.get("/keys/summary")
async def get_keys_summary():
    """Get summary of all API keys and their status"""

    try:
        services = ["openai", "gemini", "claude", "perplexity"]
        summary = {
            "total_services": len(services),
            "healthy_services": 0,
            "degraded_services": 0,
            "unhealthy_services": 0,
            "total_daily_cost": 0.0,
            "total_daily_requests": 0,
            "services": {}
        }

        for service in services:
            try:
                metrics = await api_key_manager.get_service_health(service)

                service_data = {
                    "health": metrics.health.value,
                    "active_keys": metrics.active_keys,
                    "daily_cost": metrics.daily_cost,
                    "daily_requests": metrics.daily_requests,
                    "success_rate": metrics.success_rate,
                    "circuit_breaker_open": metrics.circuit_breaker_open
                }

                summary["services"][service] = service_data
                summary["total_daily_cost"] += metrics.daily_cost
                summary["total_daily_requests"] += metrics.daily_requests

                # Count service health
                if metrics.health.value == "healthy":
                    summary["healthy_services"] += 1
                elif metrics.health.value == "degraded":
                    summary["degraded_services"] += 1
                else:
                    summary["unhealthy_services"] += 1

            except Exception as e:
                logger.warning(f"Failed to get metrics for {service}: {e}")
                summary["services"][service] = {
                    "health": "unknown",
                    "active_keys": 0,
                    "daily_cost": 0.0,
                    "daily_requests": 0,
                    "success_rate": 0.0,
                    "circuit_breaker_open": True
                }
                summary["unhealthy_services"] += 1

        # Calculate overall health
        if summary["unhealthy_services"] > 0:
            summary["overall_health"] = "unhealthy"
        elif summary["degraded_services"] > 0:
            summary["overall_health"] = "degraded"
        else:
            summary["overall_health"] = "healthy"

        summary["total_daily_cost"] = round(summary["total_daily_cost"], 2)

        return {
            "success": True,
            "summary": summary
        }

    except Exception as e:
        logger.error(f"Failed to get keys summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get keys summary")

@router.get("/neurosurgical/costs")
async def get_neurosurgical_operation_costs():
    """Get cost breakdown for neurosurgical operations"""

    try:
        # This would read from Redis in a real implementation
        operation_costs = {
            "chapter_generation": {
                "cost_per_operation": 0.50,
                "daily_operations": 0,
                "daily_cost": 0.0,
                "description": "AI-generated neurosurgical chapters"
            },
            "literature_analysis": {
                "cost_per_operation": 0.25,
                "daily_operations": 0,
                "daily_cost": 0.0,
                "description": "PubMed/research analysis"
            },
            "case_review": {
                "cost_per_operation": 0.30,
                "daily_operations": 0,
                "daily_cost": 0.0,
                "description": "Clinical case analysis"
            },
            "image_analysis": {
                "cost_per_operation": 0.40,
                "daily_operations": 0,
                "daily_cost": 0.0,
                "description": "Medical image interpretation"
            },
            "diagnosis_support": {
                "cost_per_operation": 0.35,
                "daily_operations": 0,
                "daily_cost": 0.0,
                "description": "Diagnostic assistance"
            }
        }

        total_daily_cost = sum(op["daily_cost"] for op in operation_costs.values())
        total_operations = sum(op["daily_operations"] for op in operation_costs.values())

        return {
            "success": True,
            "neurosurgical_costs": {
                "operations": operation_costs,
                "totals": {
                    "daily_operations": total_operations,
                    "daily_cost": round(total_daily_cost, 2),
                    "estimated_monthly_cost": round(total_daily_cost * 30, 2)
                }
            }
        }

    except Exception as e:
        logger.error(f"Failed to get neurosurgical costs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get neurosurgical operation costs")

@router.post("/health-check/{service}")
async def run_service_health_check(service: str):
    """Run a manual health check for a specific service"""

    try:
        if service not in ["openai", "gemini", "claude", "perplexity"]:
            raise HTTPException(status_code=400, detail="Invalid service name")

        # This would trigger a health check in the API key manager
        metrics = await api_key_manager.get_service_health(service)

        return {
            "success": True,
            "service": service,
            "health_check_result": {
                "health": metrics.health.value,
                "active_keys": metrics.active_keys,
                "success_rate": metrics.success_rate,
                "avg_response_time_ms": metrics.avg_response_time_ms,
                "circuit_breaker_open": metrics.circuit_breaker_open
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check failed for {service}: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed for {service}")

@router.get("/cost-optimization/recommendations")
async def get_cost_optimization_recommendations():
    """Get recommendations for optimizing AI service costs"""

    try:
        recommendations = []

        # Get all service health data
        health_data = await api_key_manager.get_all_service_health()

        for service, metrics in health_data.items():
            # High cost services
            if metrics.daily_cost > 10.0:
                recommendations.append({
                    "type": "cost_warning",
                    "service": service,
                    "message": f"High daily cost for {service}: ${metrics.daily_cost}",
                    "suggestion": "Consider reducing usage or switching to a more cost-effective model"
                })

            # Poor performance services
            if metrics.success_rate < 90.0:
                recommendations.append({
                    "type": "performance_warning",
                    "service": service,
                    "message": f"Low success rate for {service}: {metrics.success_rate}%",
                    "suggestion": "Check API key validity and service status"
                })

            # High response time
            if metrics.avg_response_time_ms > 3000:
                recommendations.append({
                    "type": "latency_warning",
                    "service": service,
                    "message": f"High response time for {service}: {metrics.avg_response_time_ms}ms",
                    "suggestion": "Consider using a faster model or checking network connectivity"
                })

            # Circuit breaker open
            if metrics.circuit_breaker_open:
                recommendations.append({
                    "type": "availability_error",
                    "service": service,
                    "message": f"Circuit breaker is open for {service}",
                    "suggestion": "Service is experiencing failures. Check API key and service status"
                })

        # Cost efficiency recommendations
        total_monthly_cost = sum(m.estimated_monthly_cost for m in health_data.values())
        if total_monthly_cost > 1500:  # Budget threshold
            recommendations.append({
                "type": "budget_warning",
                "service": "all",
                "message": f"High estimated monthly cost: ${total_monthly_cost}",
                "suggestion": "Review usage patterns and consider optimizing prompts or models"
            })

        return {
            "success": True,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "cost_analysis": {
                "estimated_monthly_cost": round(total_monthly_cost, 2),
                "budget_limit": 1800,
                "budget_utilization": round((total_monthly_cost / 1800) * 100, 1)
            }
        }

    except Exception as e:
        logger.error(f"Failed to get cost optimization recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")