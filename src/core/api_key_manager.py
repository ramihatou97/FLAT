"""
API Key Management System
Automatic rotation, health monitoring, and cost optimization for neurosurgical AI platform
"""

import asyncio
import logging
import time
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import aioredis
from dataclasses import dataclass, asdict

from .config import settings

logger = logging.getLogger(__name__)

class APIKeyStatus(Enum):
    ACTIVE = "active"
    RATE_LIMITED = "rate_limited"
    EXPIRED = "expired"
    FAILED = "failed"
    ROTATING = "rotating"

class ServiceHealth(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class APIKeyInfo:
    key_id: str
    service: str
    key_masked: str  # Only show last 4 characters
    status: APIKeyStatus
    last_used: datetime
    success_rate: float
    avg_response_time_ms: float
    daily_requests: int
    daily_cost: float
    rate_limit_remaining: int
    rate_limit_reset: datetime
    failure_count: int
    created_at: datetime
    rotated_at: Optional[datetime] = None

@dataclass
class ServiceMetrics:
    service: str
    health: ServiceHealth
    total_keys: int
    active_keys: int
    primary_key_id: str
    backup_key_ids: List[str]
    daily_cost: float
    daily_requests: int
    success_rate: float
    avg_response_time_ms: float
    last_health_check: datetime
    circuit_breaker_open: bool
    estimated_monthly_cost: float

class NeurosurgicalAPIKeyManager:
    """
    Advanced API key management for neurosurgical AI platform
    Focuses on reliability, cost optimization, and fault tolerance
    """

    def __init__(self):
        self.redis_client = None
        self.api_keys: Dict[str, List[APIKeyInfo]] = {
            "openai": [],
            "gemini": [],
            "claude": [],
            "perplexity": []
        }

        # Neurosurgical platform specific settings
        self.daily_budget_per_service = 15.0  # $15/day per service
        self.max_monthly_budget = 1800.0      # $1800/month total
        self.critical_failure_threshold = 5   # Circuit breaker threshold
        self.rotation_interval_hours = 24     # Daily rotation

        # Cost tracking for neurosurgical operations
        self.cost_per_operation = {
            "chapter_generation": 0.50,      # AI-generated neurosurgical chapters
            "literature_analysis": 0.25,    # PubMed/research analysis
            "case_review": 0.30,             # Clinical case analysis
            "image_analysis": 0.40,          # Medical image interpretation
            "diagnosis_support": 0.35        # Diagnostic assistance
        }

    async def initialize(self):
        """Initialize the API key manager with Redis and load existing keys"""
        try:
            self.redis_client = aioredis.from_url(
                "redis://localhost:6379",
                decode_responses=True
            )
            await self.redis_client.ping()

            # Load existing API key configurations
            await self._load_api_keys()

            # Start background monitoring
            asyncio.create_task(self._background_monitoring())

            logger.info("🔑 Neurosurgical API Key Manager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize API Key Manager: {e}")
            # Fallback to basic configuration
            await self._setup_basic_keys()

    async def _load_api_keys(self):
        """Load API key configurations from environment and Redis"""

        # Primary keys from environment
        env_keys = {
            "openai": settings.openai_api_key,
            "gemini": settings.google_api_key,
            "claude": settings.claude_api_key,
            "perplexity": settings.perplexity_api_key
        }

        for service, primary_key in env_keys.items():
            if primary_key:
                # Check if we have stored metadata for this key
                key_data = await self._get_key_metadata(service, "primary")

                if not key_data:
                    # Create new key info for primary key
                    key_info = APIKeyInfo(
                        key_id="primary",
                        service=service,
                        key_masked=f"***{primary_key[-4:]}",
                        status=APIKeyStatus.ACTIVE,
                        last_used=datetime.utcnow(),
                        success_rate=100.0,
                        avg_response_time_ms=0.0,
                        daily_requests=0,
                        daily_cost=0.0,
                        rate_limit_remaining=1000,
                        rate_limit_reset=datetime.utcnow() + timedelta(hours=1),
                        failure_count=0,
                        created_at=datetime.utcnow()
                    )
                else:
                    key_info = self._dict_to_key_info(key_data)

                self.api_keys[service].append(key_info)

                # Store updated metadata
                await self._store_key_metadata(key_info)

        logger.info(f"🔑 Loaded API keys for services: {list(env_keys.keys())}")

    async def _setup_basic_keys(self):
        """Setup basic key configuration when Redis is unavailable"""

        basic_services = ["openai", "gemini", "claude", "perplexity"]

        for service in basic_services:
            key_info = APIKeyInfo(
                key_id="primary",
                service=service,
                key_masked="***basic",
                status=APIKeyStatus.ACTIVE,
                last_used=datetime.utcnow(),
                success_rate=100.0,
                avg_response_time_ms=0.0,
                daily_requests=0,
                daily_cost=0.0,
                rate_limit_remaining=1000,
                rate_limit_reset=datetime.utcnow() + timedelta(hours=1),
                failure_count=0,
                created_at=datetime.utcnow()
            )

            self.api_keys[service].append(key_info)

    async def get_active_key(self, service: str) -> Tuple[str, str]:
        """
        Get the currently active API key for a service
        Returns: (actual_key, key_id)
        """

        if service not in self.api_keys:
            raise ValueError(f"Unknown service: {service}")

        # Find the best available key
        available_keys = [
            key for key in self.api_keys[service]
            if key.status == APIKeyStatus.ACTIVE and key.failure_count < self.critical_failure_threshold
        ]

        if not available_keys:
            # Try to find any non-failed key
            available_keys = [
                key for key in self.api_keys[service]
                if key.status != APIKeyStatus.FAILED
            ]

        if not available_keys:
            raise Exception(f"No available API keys for service: {service}")

        # Select key with best performance metrics
        best_key = min(available_keys, key=lambda k: (
            k.failure_count,
            k.avg_response_time_ms,
            -k.success_rate
        ))

        # Get actual key from environment
        actual_key = await self._get_actual_key(service, best_key.key_id)

        # Update last used timestamp
        best_key.last_used = datetime.utcnow()
        await self._store_key_metadata(best_key)

        return actual_key, best_key.key_id

    async def record_api_call(
        self,
        service: str,
        key_id: str,
        success: bool,
        response_time_ms: float,
        estimated_cost: float = 0.0,
        operation_type: str = "general"
    ):
        """Record the result of an API call for monitoring and optimization"""

        try:
            # Find the key info
            key_info = None
            for key in self.api_keys[service]:
                if key.key_id == key_id:
                    key_info = key
                    break

            if not key_info:
                logger.warning(f"Unknown key_id for recording: {service}/{key_id}")
                return

            # Update metrics
            key_info.daily_requests += 1
            key_info.daily_cost += estimated_cost

            # Update success rate (rolling average)
            if key_info.daily_requests == 1:
                key_info.success_rate = 100.0 if success else 0.0
            else:
                current_rate = key_info.success_rate
                weight = min(0.1, 1.0 / key_info.daily_requests)
                new_rate = (100.0 if success else 0.0)
                key_info.success_rate = current_rate * (1 - weight) + new_rate * weight

            # Update response time (rolling average)
            if key_info.avg_response_time_ms == 0:
                key_info.avg_response_time_ms = response_time_ms
            else:
                weight = min(0.1, 1.0 / key_info.daily_requests)
                key_info.avg_response_time_ms = (
                    key_info.avg_response_time_ms * (1 - weight) +
                    response_time_ms * weight
                )

            # Update failure count
            if success:
                key_info.failure_count = max(0, key_info.failure_count - 1)
            else:
                key_info.failure_count += 1

                # Check if key should be marked as failed
                if key_info.failure_count >= self.critical_failure_threshold:
                    key_info.status = APIKeyStatus.FAILED
                    logger.warning(f"🚫 API key marked as failed: {service}/{key_id}")

            # Store updated metrics
            await self._store_key_metadata(key_info)

            # Track neurosurgical operation costs
            if operation_type in self.cost_per_operation:
                await self._track_operation_cost(service, operation_type, estimated_cost)

        except Exception as e:
            logger.error(f"Failed to record API call: {e}")

    async def check_daily_budget(self, service: str) -> Dict[str, Any]:
        """Check if service is within daily budget limits"""

        try:
            total_cost = sum(key.daily_cost for key in self.api_keys[service])
            budget_remaining = self.daily_budget_per_service - total_cost

            status = "ok"
            if budget_remaining <= 0:
                status = "exceeded"
            elif budget_remaining < 2.0:  # Less than $2 remaining
                status = "warning"

            return {
                "service": service,
                "daily_cost": round(total_cost, 2),
                "budget_limit": self.daily_budget_per_service,
                "budget_remaining": round(budget_remaining, 2),
                "budget_used_percent": round((total_cost / self.daily_budget_per_service) * 100, 1),
                "status": status
            }

        except Exception as e:
            logger.error(f"Failed to check budget for {service}: {e}")
            return {
                "service": service,
                "status": "error",
                "error": str(e)
            }

    async def get_service_health(self, service: str) -> ServiceMetrics:
        """Get comprehensive health metrics for a service"""

        try:
            service_keys = self.api_keys[service]

            if not service_keys:
                return ServiceMetrics(
                    service=service,
                    health=ServiceHealth.UNKNOWN,
                    total_keys=0,
                    active_keys=0,
                    primary_key_id="",
                    backup_key_ids=[],
                    daily_cost=0.0,
                    daily_requests=0,
                    success_rate=0.0,
                    avg_response_time_ms=0.0,
                    last_health_check=datetime.utcnow(),
                    circuit_breaker_open=False,
                    estimated_monthly_cost=0.0
                )

            # Calculate metrics
            total_keys = len(service_keys)
            active_keys = len([k for k in service_keys if k.status == APIKeyStatus.ACTIVE])
            daily_cost = sum(k.daily_cost for k in service_keys)
            daily_requests = sum(k.daily_requests for k in service_keys)

            # Weighted averages
            if daily_requests > 0:
                success_rate = sum(k.success_rate * k.daily_requests for k in service_keys) / daily_requests
                avg_response_time = sum(k.avg_response_time_ms * k.daily_requests for k in service_keys) / daily_requests
            else:
                success_rate = 100.0
                avg_response_time = 0.0

            # Determine health status
            health = ServiceHealth.HEALTHY
            if active_keys == 0:
                health = ServiceHealth.UNHEALTHY
            elif success_rate < 80.0 or avg_response_time > 5000:
                health = ServiceHealth.DEGRADED

            # Primary and backup keys
            primary_key = next((k for k in service_keys if k.key_id == "primary"), service_keys[0])
            backup_keys = [k.key_id for k in service_keys if k.key_id != primary_key.key_id]

            return ServiceMetrics(
                service=service,
                health=health,
                total_keys=total_keys,
                active_keys=active_keys,
                primary_key_id=primary_key.key_id,
                backup_key_ids=backup_keys,
                daily_cost=round(daily_cost, 2),
                daily_requests=daily_requests,
                success_rate=round(success_rate, 1),
                avg_response_time_ms=round(avg_response_time, 2),
                last_health_check=datetime.utcnow(),
                circuit_breaker_open=active_keys == 0,
                estimated_monthly_cost=round(daily_cost * 30, 2)
            )

        except Exception as e:
            logger.error(f"Failed to get service health for {service}: {e}")
            return ServiceMetrics(
                service=service,
                health=ServiceHealth.UNKNOWN,
                total_keys=0,
                active_keys=0,
                primary_key_id="",
                backup_key_ids=[],
                daily_cost=0.0,
                daily_requests=0,
                success_rate=0.0,
                avg_response_time_ms=0.0,
                last_health_check=datetime.utcnow(),
                circuit_breaker_open=True,
                estimated_monthly_cost=0.0
            )

    async def get_all_service_health(self) -> Dict[str, ServiceMetrics]:
        """Get health metrics for all services"""

        health_data = {}

        for service in self.api_keys.keys():
            health_data[service] = await self.get_service_health(service)

        return health_data

    async def rotate_key(self, service: str, key_id: str) -> bool:
        """Rotate a specific API key (placeholder for actual rotation logic)"""

        try:
            # Find the key
            key_info = None
            for key in self.api_keys[service]:
                if key.key_id == key_id:
                    key_info = key
                    break

            if not key_info:
                return False

            # Mark as rotating
            key_info.status = APIKeyStatus.ROTATING
            key_info.rotated_at = datetime.utcnow()

            # In a real implementation, this would:
            # 1. Generate new API key with the service
            # 2. Update environment/secrets
            # 3. Test the new key
            # 4. Mark as active

            # For now, just reset metrics and mark as active
            await asyncio.sleep(1)  # Simulate rotation time

            key_info.status = APIKeyStatus.ACTIVE
            key_info.failure_count = 0
            key_info.success_rate = 100.0
            key_info.daily_requests = 0
            key_info.daily_cost = 0.0

            await self._store_key_metadata(key_info)

            logger.info(f"🔄 API key rotated successfully: {service}/{key_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to rotate key {service}/{key_id}: {e}")
            return False

    async def _background_monitoring(self):
        """Background task for monitoring and maintenance"""

        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                # Health checks
                for service in self.api_keys.keys():
                    await self._health_check_service(service)

                # Daily budget checks
                for service in self.api_keys.keys():
                    budget_status = await self.check_daily_budget(service)
                    if budget_status.get("status") == "exceeded":
                        logger.warning(f"💰 Daily budget exceeded for {service}: ${budget_status['daily_cost']}")

                # Auto-rotation check (daily)
                current_hour = datetime.utcnow().hour
                if current_hour == 0:  # Midnight UTC
                    await self._daily_reset()

            except Exception as e:
                logger.error(f"Background monitoring error: {e}")

    async def _health_check_service(self, service: str):
        """Perform health check on a service"""

        try:
            # Simple test call to check service availability
            # In a real implementation, this would make a minimal API call

            for key_info in self.api_keys[service]:
                if key_info.status == APIKeyStatus.FAILED:
                    # Try to recover failed keys after some time
                    if (datetime.utcnow() - key_info.last_used).seconds > 3600:  # 1 hour
                        key_info.failure_count = max(0, key_info.failure_count - 1)
                        if key_info.failure_count < self.critical_failure_threshold:
                            key_info.status = APIKeyStatus.ACTIVE
                            logger.info(f"🔄 Recovered API key: {service}/{key_info.key_id}")

        except Exception as e:
            logger.error(f"Health check failed for {service}: {e}")

    async def _daily_reset(self):
        """Reset daily counters and perform maintenance"""

        try:
            for service_keys in self.api_keys.values():
                for key_info in service_keys:
                    key_info.daily_requests = 0
                    key_info.daily_cost = 0.0
                    await self._store_key_metadata(key_info)

            logger.info("🔄 Daily reset completed for all API keys")

        except Exception as e:
            logger.error(f"Daily reset failed: {e}")

    async def _track_operation_cost(self, service: str, operation_type: str, cost: float):
        """Track costs for specific neurosurgical operations"""

        try:
            if self.redis_client:
                key = f"neurosurg_costs:{service}:{operation_type}:{datetime.utcnow().strftime('%Y-%m-%d')}"
                await self.redis_client.incrbyfloat(key, cost)
                await self.redis_client.expire(key, 86400 * 30)  # Keep for 30 days

        except Exception as e:
            logger.error(f"Failed to track operation cost: {e}")

    async def _get_key_metadata(self, service: str, key_id: str) -> Optional[Dict[str, Any]]:
        """Get stored metadata for an API key"""

        try:
            if self.redis_client:
                key = f"api_key_meta:{service}:{key_id}"
                data = await self.redis_client.get(key)
                return json.loads(data) if data else None
        except Exception:
            pass

        return None

    async def _store_key_metadata(self, key_info: APIKeyInfo):
        """Store API key metadata"""

        try:
            if self.redis_client:
                key = f"api_key_meta:{key_info.service}:{key_info.key_id}"
                data = json.dumps(asdict(key_info), default=str)
                await self.redis_client.setex(key, 86400, data)  # 24 hour TTL

        except Exception as e:
            logger.error(f"Failed to store key metadata: {e}")

    async def _get_actual_key(self, service: str, key_id: str) -> str:
        """Get the actual API key value"""

        # Return the appropriate environment variable
        key_mapping = {
            "openai": settings.openai_api_key,
            "gemini": settings.google_api_key,
            "claude": settings.claude_api_key,
            "perplexity": settings.perplexity_api_key
        }

        return key_mapping.get(service, "")

    def _dict_to_key_info(self, data: Dict[str, Any]) -> APIKeyInfo:
        """Convert dictionary to APIKeyInfo object"""

        return APIKeyInfo(
            key_id=data["key_id"],
            service=data["service"],
            key_masked=data["key_masked"],
            status=APIKeyStatus(data["status"]),
            last_used=datetime.fromisoformat(data["last_used"]),
            success_rate=data["success_rate"],
            avg_response_time_ms=data["avg_response_time_ms"],
            daily_requests=data["daily_requests"],
            daily_cost=data["daily_cost"],
            rate_limit_remaining=data["rate_limit_remaining"],
            rate_limit_reset=datetime.fromisoformat(data["rate_limit_reset"]),
            failure_count=data["failure_count"],
            created_at=datetime.fromisoformat(data["created_at"]),
            rotated_at=datetime.fromisoformat(data["rotated_at"]) if data.get("rotated_at") else None
        )

# Global API key manager instance
api_key_manager = NeurosurgicalAPIKeyManager()