"""
Monitoring Service
Real-time system health monitoring, metrics collection, and alerting
"""

import asyncio
import logging
import time
import psutil
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import aioredis
import asyncpg
from sqlalchemy import text

from ..core.database import get_async_session
from ..core.config import settings
from .multi_ai_manager import multi_ai_manager
from ..core.api_key_manager import api_key_manager

logger = logging.getLogger(__name__)

class CircuitBreakerState:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call_success(self):
        """Record successful call"""
        self.failure_count = 0
        self.state = "CLOSED"

    def call_failure(self):
        """Record failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def can_call(self) -> bool:
        """Check if calls are allowed"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True

class MonitoringService:
    """Service for system monitoring and health checks"""

    def __init__(self):
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self.alerts = []
        self.circuit_breakers = {
            "database": CircuitBreakerState(),
            "redis": CircuitBreakerState(),
            "openai": CircuitBreakerState(),
            "gemini": CircuitBreakerState(),
            "claude": CircuitBreakerState(),
            "perplexity": CircuitBreakerState()
        }
        self.start_time = time.time()
        self.api_call_counts = defaultdict(int)
        self.api_response_times = defaultdict(list)

    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""

        health_checks = {}
        overall_healthy = True

        # Database health
        try:
            db_healthy = await self._check_database_health()
            health_checks["database"] = {
                "status": "healthy" if db_healthy else "unhealthy",
                "details": "Database connection and query test"
            }
            if not db_healthy:
                overall_healthy = False
        except Exception as e:
            health_checks["database"] = {
                "status": "error",
                "details": f"Database check failed: {str(e)}"
            }
            overall_healthy = False

        # Redis health
        try:
            redis_healthy = await self._check_redis_health()
            health_checks["redis"] = {
                "status": "healthy" if redis_healthy else "unhealthy",
                "details": "Redis connection and ping test"
            }
            if not redis_healthy:
                overall_healthy = False
        except Exception as e:
            health_checks["redis"] = {
                "status": "error",
                "details": f"Redis check failed: {str(e)}"
            }
            overall_healthy = False

        # AI Services health
        ai_services_health = await self._check_ai_services_health()
        health_checks["ai_services"] = ai_services_health

        # System resources
        system_health = await self._check_system_resources()
        health_checks["system_resources"] = system_health
        if not system_health["status"] == "healthy":
            overall_healthy = False

        return {
            "overall_healthy": overall_healthy,
            "checks": health_checks,
            "uptime_seconds": time.time() - self.start_time,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get real-time system resource metrics"""

        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_metrics = {
                "total_mb": round(memory.total / 1024 / 1024, 2),
                "used_mb": round(memory.used / 1024 / 1024, 2),
                "available_mb": round(memory.available / 1024 / 1024, 2),
                "percent": memory.percent
            }

            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_metrics = {
                "total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
                "used_gb": round(disk.used / 1024 / 1024 / 1024, 2),
                "free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
                "percent": round((disk.used / disk.total) * 100, 2)
            }

            # Process metrics
            process = psutil.Process()
            process_metrics = {
                "cpu_percent": process.cpu_percent(),
                "memory_mb": round(process.memory_info().rss / 1024 / 1024, 2),
                "threads": process.num_threads(),
                "open_files": len(process.open_files()),
                "connections": len(process.connections())
            }

            metrics = {
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count
                },
                "memory": memory_metrics,
                "disk": disk_metrics,
                "process": process_metrics,
                "timestamp": datetime.utcnow().isoformat()
            }

            # Store in history
            self.metrics_history["system"].append({
                "timestamp": time.time(),
                "metrics": metrics
            })

            return metrics

        except Exception as e:
            logger.error(f"System metrics collection failed: {e}")
            return {"error": str(e)}

    async def get_database_metrics(self) -> Dict[str, Any]:
        """Get database connection pool and performance metrics"""

        try:
            metrics = {
                "connection_pool": {
                    "status": "unknown",
                    "active_connections": 0,
                    "idle_connections": 0
                },
                "query_performance": {
                    "avg_response_time_ms": 0,
                    "slow_queries": 0
                }
            }

            # Test database connection and measure response time
            start_time = time.time()
            try:
                async with get_async_session() as session:
                    result = await session.execute(text("SELECT 1"))
                    await result.fetchone()

                response_time = (time.time() - start_time) * 1000
                metrics["connection_pool"]["status"] = "healthy"
                metrics["query_performance"]["avg_response_time_ms"] = round(response_time, 2)

                # Circuit breaker success
                self.circuit_breakers["database"].call_success()

            except Exception as e:
                metrics["connection_pool"]["status"] = "error"
                metrics["error"] = str(e)
                self.circuit_breakers["database"].call_failure()

            return metrics

        except Exception as e:
            logger.error(f"Database metrics collection failed: {e}")
            return {"error": str(e)}

    async def get_ai_service_metrics(self) -> Dict[str, Any]:
        """Get AI service health, performance, and cost metrics from API key manager"""

        try:
            # Get comprehensive metrics from API key manager
            api_key_health = await api_key_manager.get_all_service_health()

            metrics = {}
            for service, health_metrics in api_key_health.items():
                # Get budget information
                budget_info = await api_key_manager.check_daily_budget(service)

                service_metrics = {
                    "status": health_metrics.health.value,
                    "circuit_breaker": {
                        "state": "OPEN" if health_metrics.circuit_breaker_open else "CLOSED",
                        "failure_count": 0,  # API key manager handles this internally
                        "can_call": not health_metrics.circuit_breaker_open
                    },
                    "performance": {
                        "avg_response_time_ms": health_metrics.avg_response_time_ms,
                        "success_rate": health_metrics.success_rate,
                        "calls_today": health_metrics.daily_requests
                    },
                    "cost": {
                        "estimated_daily_cost": health_metrics.daily_cost,
                        "budget_remaining": budget_info.get("budget_remaining", 0.0),
                        "budget_used_percent": budget_info.get("budget_used_percent", 0.0)
                    },
                    "keys": {
                        "total_keys": health_metrics.total_keys,
                        "active_keys": health_metrics.active_keys,
                        "primary_key_id": health_metrics.primary_key_id
                    }
                }

                metrics[service] = service_metrics

            return metrics

        except Exception as e:
            logger.error(f"Failed to get AI service metrics from API key manager: {e}")

            # Fallback to basic metrics
            ai_services = ["openai", "gemini", "claude", "perplexity"]
            metrics = {}

            for service in ai_services:
                service_metrics = {
                    "status": "unknown",
                    "circuit_breaker": {
                        "state": "UNKNOWN",
                        "failure_count": 0,
                        "can_call": False
                    },
                    "performance": {
                        "avg_response_time_ms": 0,
                        "success_rate": 0.0,
                        "calls_today": 0
                    },
                    "cost": {
                        "estimated_daily_cost": 0.0,
                        "budget_remaining": 15.0
                    },
                    "error": "Failed to get metrics from API key manager"
                }

                metrics[service] = service_metrics

            return metrics

    async def get_cache_metrics(self) -> Dict[str, Any]:
        """Get Redis cache performance metrics"""

        try:
            # Try to connect to Redis
            try:
                redis = aioredis.from_url("redis://localhost:6379", decode_responses=True)

                # Test Redis connection
                await redis.ping()

                # Get Redis info
                info = await redis.info()

                metrics = {
                    "status": "healthy",
                    "connection": "active",
                    "memory": {
                        "used_mb": round(info.get("used_memory", 0) / 1024 / 1024, 2),
                        "peak_mb": round(info.get("used_memory_peak", 0) / 1024 / 1024, 2),
                        "fragmentation_ratio": info.get("mem_fragmentation_ratio", 0)
                    },
                    "performance": {
                        "keyspace_hits": info.get("keyspace_hits", 0),
                        "keyspace_misses": info.get("keyspace_misses", 0),
                        "hit_rate": 0
                    },
                    "clients": {
                        "connected": info.get("connected_clients", 0),
                        "blocked": info.get("blocked_clients", 0)
                    }
                }

                # Calculate hit rate
                hits = metrics["performance"]["keyspace_hits"]
                misses = metrics["performance"]["keyspace_misses"]
                if hits + misses > 0:
                    metrics["performance"]["hit_rate"] = round((hits / (hits + misses)) * 100, 2)

                await redis.close()
                self.circuit_breakers["redis"].call_success()

                return metrics

            except Exception as e:
                self.circuit_breakers["redis"].call_failure()
                return {
                    "status": "error",
                    "connection": "failed",
                    "error": str(e)
                }

        except Exception as e:
            logger.error(f"Cache metrics collection failed: {e}")
            return {"error": str(e)}

    async def get_api_metrics(self) -> Dict[str, Any]:
        """Get API endpoint performance and usage metrics"""

        try:
            # Get API call statistics
            total_calls = sum(self.api_call_counts.values())

            endpoint_metrics = {}
            for endpoint, count in self.api_call_counts.items():
                response_times = self.api_response_times.get(endpoint, [])
                avg_response_time = sum(response_times) / len(response_times) if response_times else 0

                endpoint_metrics[endpoint] = {
                    "calls_count": count,
                    "avg_response_time_ms": round(avg_response_time, 2),
                    "percentage_of_total": round((count / total_calls) * 100, 2) if total_calls > 0 else 0
                }

            return {
                "total_api_calls": total_calls,
                "endpoints": endpoint_metrics,
                "uptime_seconds": time.time() - self.start_time
            }

        except Exception as e:
            logger.error(f"API metrics collection failed: {e}")
            return {"error": str(e)}

    async def get_task_metrics(self) -> Dict[str, Any]:
        """Get background task queue metrics"""

        # For now, return placeholder metrics
        # When Celery is implemented, this will get real task queue stats
        return {
            "status": "not_implemented",
            "queue_length": 0,
            "active_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "task_types": {}
        }

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""

        try:
            # Collect all metrics concurrently
            tasks = [
                self.get_system_health(),
                self.get_system_metrics(),
                self.get_database_metrics(),
                self.get_ai_service_metrics(),
                self.get_cache_metrics(),
                self.get_api_metrics()
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            dashboard = {
                "health": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
                "system": results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])},
                "database": results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])},
                "ai_services": results[3] if not isinstance(results[3], Exception) else {"error": str(results[3])},
                "cache": results[4] if not isinstance(results[4], Exception) else {"error": str(results[4])},
                "api": results[5] if not isinstance(results[5], Exception) else {"error": str(results[5])},
                "alerts": self.alerts,
                "timestamp": datetime.utcnow().isoformat()
            }

            return dashboard

        except Exception as e:
            logger.error(f"Dashboard data collection failed: {e}")
            return {"error": str(e)}

    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active system alerts"""
        return self.alerts

    async def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get circuit breaker status for all services from API key manager"""

        try:
            # Get circuit breaker status from API key manager
            api_key_health = await api_key_manager.get_all_service_health()

            status = {}
            for service_name, health_metrics in api_key_health.items():
                status[service_name] = {
                    "state": "OPEN" if health_metrics.circuit_breaker_open else "CLOSED",
                    "health": health_metrics.health.value,
                    "active_keys": health_metrics.active_keys,
                    "success_rate": health_metrics.success_rate,
                    "avg_response_time_ms": health_metrics.avg_response_time_ms,
                    "can_call": not health_metrics.circuit_breaker_open,
                    "last_health_check": health_metrics.last_health_check.isoformat()
                }

            return status

        except Exception as e:
            logger.error(f"Failed to get circuit breaker status: {e}")

            # Fallback to local circuit breakers
            status = {}
            for service_name, breaker in self.circuit_breakers.items():
                status[service_name] = {
                    "state": breaker.state,
                    "failure_count": breaker.failure_count,
                    "can_call": breaker.can_call(),
                    "last_failure": breaker.last_failure_time
                }

            return status

    async def get_performance_history(self, hours: int) -> Dict[str, Any]:
        """Get historical performance data"""

        cutoff_time = time.time() - (hours * 3600)
        history = {}

        for metric_type, data in self.metrics_history.items():
            history[metric_type] = [
                entry for entry in data
                if entry["timestamp"] > cutoff_time
            ]

        return history

    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge a specific alert"""

        for alert in self.alerts:
            if alert.get("id") == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_at"] = datetime.utcnow().isoformat()
                return True

        return False

    async def get_status_summary(self) -> Dict[str, Any]:
        """Get high-level system status summary"""

        try:
            health = await self.get_system_health()

            summary = {
                "overall_status": "healthy" if health["overall_healthy"] else "unhealthy",
                "uptime_hours": round((time.time() - self.start_time) / 3600, 2),
                "active_alerts": len([alert for alert in self.alerts if not alert.get("acknowledged", False)]),
                "services": {
                    "database": health["checks"]["database"]["status"],
                    "redis": health["checks"]["redis"]["status"],
                    "ai_services": "healthy" if all(
                        breaker.can_call() for breaker in self.circuit_breakers.values()
                        if "ai" in str(breaker) or breaker in ["openai", "gemini", "claude", "perplexity"]
                    ) else "degraded"
                },
                "last_updated": datetime.utcnow().isoformat()
            }

            return summary

        except Exception as e:
            logger.error(f"Status summary failed: {e}")
            return {"error": str(e)}

    async def run_ai_provider_diagnostic(self, provider: str) -> Dict[str, Any]:
        """Run diagnostic test for specific AI provider"""

        try:
            start_time = time.time()

            # Simple test call to the AI provider
            test_prompt = "Test diagnostic message. Please respond with 'OK'."

            result = await multi_ai_manager.generate_content(
                prompt=test_prompt,
                provider=provider,
                context_type="medical",
                max_tokens=10,
                temperature=0.1
            )

            response_time = (time.time() - start_time) * 1000

            if result.get("success"):
                self.circuit_breakers[provider].call_success()
                return {
                    "status": "healthy",
                    "response_time_ms": round(response_time, 2),
                    "response": result.get("content", ""),
                    "provider_info": {
                        "model": result.get("model"),
                        "tokens_used": result.get("tokens_used", 0)
                    }
                }
            else:
                self.circuit_breakers[provider].call_failure()
                return {
                    "status": "unhealthy",
                    "response_time_ms": round(response_time, 2),
                    "error": result.get("error", "Unknown error")
                }

        except Exception as e:
            self.circuit_breakers[provider].call_failure()
            logger.error(f"AI provider diagnostic failed for {provider}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def get_recent_logs(self, level: str, limit: int) -> List[Dict[str, Any]]:
        """Get recent application logs"""

        # For now, return placeholder logs
        # In production, this would read from actual log files or centralized logging
        return [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "message": "Monitoring service initialized",
                "module": "monitoring_service"
            }
        ]

    # Helper methods
    async def _check_database_health(self) -> bool:
        """Check database connectivity and basic query"""
        try:
            async with get_async_session() as session:
                result = await session.execute(text("SELECT 1"))
                await result.fetchone()
                return True
        except Exception:
            return False

    async def _check_redis_health(self) -> bool:
        """Check Redis connectivity"""
        try:
            redis = aioredis.from_url("redis://localhost:6379")
            await redis.ping()
            await redis.close()
            return True
        except Exception:
            return False

    async def _check_ai_services_health(self) -> Dict[str, Any]:
        """Check AI services availability"""

        services_status = {}
        ai_services = ["openai", "gemini", "claude", "perplexity"]

        for service in ai_services:
            can_call = self.circuit_breakers[service].can_call()
            services_status[service] = {
                "status": "available" if can_call else "circuit_open",
                "circuit_state": self.circuit_breakers[service].state
            }

        overall_healthy = any(
            status["status"] == "available"
            for status in services_status.values()
        )

        return {
            "status": "healthy" if overall_healthy else "degraded",
            "services": services_status,
            "details": "At least one AI service available" if overall_healthy else "All AI services unavailable"
        }

    async def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""

        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            cpu_percent = psutil.cpu_percent(interval=1)

            # Define thresholds
            memory_threshold = 90  # 90%
            disk_threshold = 90    # 90%
            cpu_threshold = 90     # 90%

            issues = []
            if memory.percent > memory_threshold:
                issues.append(f"High memory usage: {memory.percent}%")
            if (disk.used / disk.total) * 100 > disk_threshold:
                issues.append(f"High disk usage: {(disk.used / disk.total) * 100:.1f}%")
            if cpu_percent > cpu_threshold:
                issues.append(f"High CPU usage: {cpu_percent}%")

            return {
                "status": "healthy" if not issues else "warning",
                "details": "System resources normal" if not issues else "; ".join(issues),
                "metrics": {
                    "memory_percent": memory.percent,
                    "disk_percent": round((disk.used / disk.total) * 100, 1),
                    "cpu_percent": cpu_percent
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "details": f"Resource check failed: {str(e)}"
            }

    def record_api_call(self, endpoint: str, response_time_ms: float):
        """Record API call for metrics"""
        self.api_call_counts[endpoint] += 1
        self.api_response_times[endpoint].append(response_time_ms)

        # Keep only last 1000 response times
        if len(self.api_response_times[endpoint]) > 1000:
            self.api_response_times[endpoint] = self.api_response_times[endpoint][-1000:]

    def record_ai_call(self, provider: str, success: bool, response_time_ms: float):
        """Record AI service call for metrics"""
        self.metrics_history[f"ai_{provider}"].append({
            "timestamp": time.time(),
            "success": success,
            "response_time_ms": response_time_ms
        })

# Global monitoring service instance
monitoring_service = MonitoringService()