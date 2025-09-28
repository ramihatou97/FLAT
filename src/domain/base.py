"""Base model with medical validation hooks"""

from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel, Field

from ..core.database import Base

class DomainBase(Base):
    """SQLAlchemy base with medical features"""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Medical validation
    medical_context = Column(JSON, default=dict, nullable=False)
    confidence_score = Column(Float, default=0.0, nullable=False)
    validation_status = Column(String(20), default='pending', nullable=False)
    
    def validate_medical_context(self) -> bool:
        """Override in subclasses for specific validation"""
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'medical_context': self.medical_context,
            'confidence_score': self.confidence_score,
            'validation_status': self.validation_status
        }

class BaseSchema(BaseModel):
    """Pydantic base schema"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    medical_context: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    validation_status: str = Field(default="pending")
    
    class Config:
        from_attributes = True
