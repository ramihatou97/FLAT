"""Production database manager - KOO patterns + UUP medical awareness"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Dict, Any
import logging

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import event

from .config import settings
from .exceptions import DatabaseError

logger = logging.getLogger(__name__)

Base = declarative_base()

class UnifiedDatabaseManager:
    """Single database manager for the platform"""
    
    def __init__(self, database_url: str = settings.database_url):
        self.database_url = database_url
        self.engine = create_async_engine(
            database_url,
            pool_size=settings.database_pool_size,
            pool_pre_ping=True,
            echo=settings.db_echo
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
    @asynccontextmanager
    async def get_session(
        self, 
        medical_context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[AsyncSession, None]:
        """Get database session with optional medical context"""
        async with self.session_factory() as session:
            try:
                # Add medical context to session if provided
                if medical_context:
                    session.info["medical_context"] = medical_context
                    
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Database error: {e}")
                raise DatabaseError(f"Database operation failed: {e}")
            finally:
                await session.close()
    
    async def health_check(self) -> bool:
        """Check database health"""
        try:
            async with self.engine.begin() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def close(self):
        """Close database connections"""
        await self.engine.dispose()

# Global instance
db_manager = UnifiedDatabaseManager()
