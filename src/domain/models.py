"""Core domain models - simplified from all platforms"""

from typing import List, Optional
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, JSON, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import DomainBase

class Chapter(DomainBase):
    """Core content model with alive chapter features"""
    __tablename__ = "chapters"

    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    specialty = Column(String(100), index=True)
    tags = Column(ARRAY(String), default=list, nullable=False)

    # Alive chapter features
    is_alive = Column(Boolean, default=False, nullable=False)
    active_users = Column(JSON, default=list)  # List of active user IDs
    last_activity = Column(DateTime, default=datetime.utcnow)
    conflict_resolution = Column(JSON, default=dict)

    # Metrics
    word_count = Column(Integer, default=0, nullable=False)
    quality_score = Column(Float, default=0.0, nullable=False)
    confidence_score = Column(Float, default=0.0, nullable=False)

    # AI Enhancement
    ai_generated = Column(Boolean, default=False, nullable=False)
    ai_model_used = Column(String(50))
    synthesis_metadata = Column(JSON, default=dict)

    # Relationships
    concepts = relationship("MedicalConcept", back_populates="chapter")
    search_results = relationship("SearchResult", back_populates="chapter")

class MedicalConcept(DomainBase):
    """Medical concept model"""
    __tablename__ = "medical_concepts"
    
    term = Column(String(200), nullable=False, index=True)
    definition = Column(Text, nullable=False)
    concept_type = Column(String(50))  # anatomy, disease, procedure, drug
    specialty = Column(String(100))
    
    # Medical relevance
    clinical_relevance = Column(Float, default=0.5, nullable=False)
    evidence_level = Column(String(20))
    
    # Relationships
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"))
    chapter = relationship("Chapter", back_populates="concepts")

class ResearchPaper(DomainBase):
    """Research paper model"""
    __tablename__ = "research_papers"
    
    pmid = Column(String(20), unique=True, index=True)
    doi = Column(String(100))
    title = Column(String(500), nullable=False)
    abstract = Column(Text)
    authors = Column(ARRAY(String), default=list)
    
    # Medical metrics
    evidence_level = Column(String(10))
    clinical_relevance = Column(Float, default=0.0)
    specialty_scores = Column(JSON, default=dict)  # {specialty: score}
    
    # Integration
    cited_in_chapters = Column(ARRAY(UUID(as_uuid=True)), default=list)
    key_findings = Column(JSON, default=dict)

class User(DomainBase):
    """User model for authentication and preferences"""
    __tablename__ = "users"

    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Profile
    full_name = Column(String(200))
    specialty = Column(String(100))
    institution = Column(String(200))

    # Permissions
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    permissions = Column(ARRAY(String), default=list)

    # Preferences
    search_preferences = Column(JSON, default=dict)
    ui_preferences = Column(JSON, default=dict)

    # Activity tracking
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)

class SearchResult(DomainBase):
    """Search result model for caching and analytics"""
    __tablename__ = "search_results"

    query_text = Column(String(1000), nullable=False, index=True)
    query_hash = Column(String(64), nullable=False, index=True)  # MD5 hash of query

    # Results
    results_data = Column(JSON, nullable=False)  # Serialized search results
    total_found = Column(Integer, default=0)
    processing_time_ms = Column(Float, default=0.0)

    # Metadata
    content_types_searched = Column(ARRAY(String), default=list)
    specialty_filter = Column(String(100))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Analytics
    click_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"))
    chapter = relationship("Chapter", back_populates="search_results")

class SynthesisTask(DomainBase):
    """Background synthesis task tracking"""
    __tablename__ = "synthesis_tasks"

    task_id = Column(String(100), unique=True, nullable=False, index=True)
    topic = Column(String(500), nullable=False)

    # Configuration
    sources = Column(JSON, default=list)
    specialty = Column(String(100))
    ai_model = Column(String(50))
    include_research = Column(Boolean, default=True)

    # Status
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    current_step = Column(String(200))
    error_message = Column(Text)

    # Results
    result_chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"))
    result_metadata = Column(JSON, default=dict)

    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    estimated_completion = Column(DateTime)

    # User
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User")
    result_chapter = relationship("Chapter")

class AliveChapterActivity(DomainBase):
    """Track activity in alive chapters"""
    __tablename__ = "alive_chapter_activities"

    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Activity details
    activity_type = Column(String(50), nullable=False)  # edit, view, comment, sync
    activity_data = Column(JSON, default=dict)

    # Content changes
    content_before = Column(Text)
    content_after = Column(Text)
    change_summary = Column(String(500))

    # Metadata
    session_id = Column(String(100))
    ip_address = Column(String(45))
    user_agent = Column(String(500))

    # Relationships
    chapter = relationship("Chapter")
    user = relationship("User")
