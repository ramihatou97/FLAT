"""
FastAPI Dependencies
Authentication, database sessions, and other shared dependencies
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import logging

from .database import db_manager

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)

async def get_db() -> AsyncSession:
    """
    Get database session dependency
    """
    try:
        async with db_manager.get_session() as session:
            yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable"
        )

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Get current authenticated user
    For now, this is a simplified implementation
    In production, this would validate JWT tokens
    """
    if not credentials:
        # For development, return a default user
        return {
            "id": "dev_user_1",
            "username": "developer",
            "email": "dev@medical-platform.com",
            "is_admin": True,
            "specialty": "neurosurgery",
            "permissions": ["read", "write", "admin"]
        }
    
    try:
        # In production, this would:
        # 1. Validate the JWT token
        # 2. Extract user information
        # 3. Check token expiration
        # 4. Verify user permissions
        
        token = credentials.credentials
        
        # Placeholder token validation
        if token == "dev_token":
            return {
                "id": "dev_user_1",
                "username": "developer",
                "email": "dev@medical-platform.com",
                "is_admin": True,
                "specialty": "neurosurgery",
                "permissions": ["read", "write", "admin"]
            }
        elif token == "test_token":
            return {
                "id": "test_user_1",
                "username": "test_user",
                "email": "test@medical-platform.com",
                "is_admin": False,
                "specialty": "general",
                "permissions": ["read", "write"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency that requires admin privileges
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

async def get_user_with_permission(permission: str):
    """
    Factory function to create permission-based dependencies
    """
    async def check_permission(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        user_permissions = current_user.get("permissions", [])
        if permission not in user_permissions and not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    
    return check_permission

# Specific permission dependencies
get_read_permission = get_user_with_permission("read")
get_write_permission = get_user_with_permission("write")
get_delete_permission = get_user_with_permission("delete")

async def get_specialty_access(
    specialty: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Check if user has access to specific medical specialty
    """
    user_specialty = current_user.get("specialty")
    
    # Admin users have access to all specialties
    if current_user.get("is_admin", False):
        return current_user
    
    # Users can access their own specialty or general content
    if user_specialty == specialty or specialty == "general":
        return current_user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Access to {specialty} specialty not authorized"
    )

class RateLimiter:
    """
    Simple rate limiter for API endpoints
    In production, this would use Redis or similar
    """
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # In production, use Redis
    
    async def check_rate_limit(
        self,
        user_id: str,
        current_user: Dict[str, Any] = Depends(get_current_user)
    ):
        """
        Check if user has exceeded rate limit
        """
        import time
        
        now = time.time()
        user_id = current_user.get("id", "anonymous")
        
        # Clean old requests
        if user_id in self.requests:
            self.requests[user_id] = [
                req_time for req_time in self.requests[user_id]
                if now - req_time < self.window_seconds
            ]
        else:
            self.requests[user_id] = []
        
        # Check rate limit
        if len(self.requests[user_id]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Add current request
        self.requests[user_id].append(now)
        
        return current_user

# Rate limiter instances
search_rate_limiter = RateLimiter(max_requests=50, window_seconds=60)
synthesis_rate_limiter = RateLimiter(max_requests=10, window_seconds=300)  # 5 minutes

async def check_search_rate_limit(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Rate limit for search endpoints"""
    return await search_rate_limiter.check_rate_limit(
        current_user.get("id", "anonymous"), current_user
    )

async def check_synthesis_rate_limit(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Rate limit for synthesis endpoints"""
    return await synthesis_rate_limiter.check_rate_limit(
        current_user.get("id", "anonymous"), current_user
    )

# Type alias for current user
CurrentUser = Dict[str, Any]
