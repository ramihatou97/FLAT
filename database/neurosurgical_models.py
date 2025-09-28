"""
Neurosurgical Encyclopedia Database Models
Comprehensive SQLAlchemy models for neurosurgical knowledge management
Built on UUP Enhanced Base Model foundation
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, 
    JSON, ARRAY, ForeignKey, Index, Table, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, VECTOR
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.declarative import declarative_base

# Import UUP base model
from core.database import UUPBaseModel, Base

# Association Tables for Many-to-Many Relationships
procedure_anatomy_mapping = Table(
    'procedure_anatomy_mapping',
    Base.metadata,
    Column('procedure_id', UUID(as_uuid=True), ForeignKey('surgical_procedures.id'), primary_key=True),
    Column('anatomy_id', UUID(as_uuid=True), ForeignKey('anatomical_structures.id'), primary_key=True),
    Column('relevance_score', Float, default=1.0),
    Column('surgical_significance', String(100), nullable=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)

chapter_source_mapping = Table(
    'chapter_source_mapping',
    Base.metadata,
    Column('chapter_id', UUID(as_uuid=True), ForeignKey('alive_chapters.id'), primary_key=True),
    Column('source_id', UUID(as_uuid=True), ForeignKey('evidence_sources.id'), primary_key=True),
    Column('relevance_score', Float, default=0.0),
    Column('citation_context', Text, nullable=True),
    Column('evidence_weight', Float, default=1.0),
    Column('created_at', DateTime, default=datetime.utcnow)
)

chapter_anatomy_mapping = Table(
    'chapter_anatomy_mapping',
    Base.metadata,
    Column('chapter_id', UUID(as_uuid=True), ForeignKey('alive_chapters.id'), primary_key=True),
    Column('anatomy_id', UUID(as_uuid=True), ForeignKey('anatomical_structures.id'), primary_key=True),
    Column('relevance_score', Float, default=0.0),
    Column('created_at', DateTime, default=datetime.utcnow)
)

class AnatomicalStructure(UUPBaseModel):
    """3D anatomical structures with surgical relevance"""
    __tablename__ = "anatomical_structures"
    
    # Basic identification
    name = Column(String(200), nullable=False, index=True)
    latin_name = Column(String(200), nullable=True, index=True)
    synonyms = Column(ARRAY(String), default=list)
    abbreviations = Column(ARRAY(String), default=list)
    
    # Hierarchical organization
    parent_id = Column(UUID(as_uuid=True), ForeignKey('anatomical_structures.id'), nullable=True)
    level = Column(Integer, default=0, index=True)  # Depth in hierarchy
    path = Column(String(500), nullable=True, index=True)  # Materialized path for fast queries
    
    # 3D spatial data
    coordinates_3d = Column(JSON, default=dict)  # {center: [x,y,z], bounds: [[x1,y1,z1], [x2,y2,z2]]}
    mesh_data = Column(JSON, default=dict)  # 3D mesh information for visualization
    visualization_config = Column(JSON, default=dict)  # Rendering settings
    
    # Clinical and surgical relevance
    clinical_significance = Column(Text, nullable=True)
    surgical_approaches = Column(ARRAY(String), default=list)
    common_pathologies = Column(ARRAY(String), default=list)
    eloquent_area = Column(Boolean, default=False)  # Critical brain areas
    vascular_supply = Column(JSON, default=dict)  # Blood supply information
    
    # Anatomical properties
    tissue_type = Column(String(100), nullable=True)  # gray matter, white matter, CSF, etc.
    functional_role = Column(Text, nullable=True)
    developmental_origin = Column(String(100), nullable=True)
    
    # Relationships
    children = relationship("AnatomicalStructure", backref="parent", remote_side="AnatomicalStructure.id")
    procedures = relationship("SurgicalProcedure", secondary=procedure_anatomy_mapping, back_populates="anatomical_targets")
    chapters = relationship("AliveChapter", secondary=chapter_anatomy_mapping, back_populates="anatomical_structures")
    
    @validates('level')
    def validate_level(self, key, level):
        if level < 0 or level > 10:
            raise ValueError("Anatomical structure level must be between 0 and 10")
        return level
    
    def get_full_path(self) -> str:
        """Get full anatomical path from root to this structure"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name

class SurgicalProcedure(UUPBaseModel):
    """Comprehensive surgical procedure documentation"""
    __tablename__ = "surgical_procedures"
    
    # Basic information
    name = Column(String(300), nullable=False, index=True)
    short_name = Column(String(100), nullable=True)
    cpt_code = Column(String(10), nullable=True, index=True)
    icd_codes = Column(ARRAY(String), default=list)
    
    # Classification and complexity
    specialty = Column(String(100), default="neurosurgery", index=True)
    subspecialty = Column(String(100), nullable=True, index=True)
    complexity_score = Column(Integer, default=5, index=True)  # 1-10 scale
    duration_minutes = Column(Integer, nullable=True)
    anesthesia_type = Column(String(100), nullable=True)
    
    # Clinical context
    indications = Column(ARRAY(String), default=list)
    contraindications = Column(ARRAY(String), default=list)
    relative_contraindications = Column(ARRAY(String), default=list)
    
    # Procedure details
    step_by_step_guide = Column(JSON, default=list)  # Structured surgical steps
    equipment_required = Column(ARRAY(String), default=list)
    positioning = Column(String(200), nullable=True)
    surgical_approach = Column(String(200), nullable=True)
    
    # Complications and outcomes
    complications = Column(JSON, default=dict)  # {complication: {frequency: %, severity: str}}
    success_rate = Column(Float, nullable=True)
    mortality_rate = Column(Float, nullable=True)
    morbidity_rate = Column(Float, nullable=True)
    
    # Evidence and guidelines
    evidence_level = Column(String(10), nullable=True, index=True)  # I, II, III, IV, V
    guideline_recommendations = Column(JSON, default=dict)
    outcome_measures = Column(JSON, default=dict)
    
    # Learning and training
    learning_curve = Column(String(100), nullable=True)  # steep, moderate, gradual
    training_requirements = Column(ARRAY(String), default=list)
    simulation_available = Column(Boolean, default=False)
    
    # Relationships
    anatomical_targets = relationship("AnatomicalStructure", secondary=procedure_anatomy_mapping, back_populates="procedures")
    
    @validates('complexity_score')
    def validate_complexity(self, key, score):
        if score < 1 or score > 10:
            raise ValueError("Complexity score must be between 1 and 10")
        return score
    
    @validates('evidence_level')
    def validate_evidence_level(self, key, level):
        if level and level not in ['I', 'II', 'III', 'IV', 'V']:
            raise ValueError("Evidence level must be I, II, III, IV, or V")
        return level

class EvidenceSource(UUPBaseModel):
    """Comprehensive source tracking and validation"""
    __tablename__ = "evidence_sources"
    
    # Source identification
    source_type = Column(String(50), nullable=False, index=True)  # pubmed, textbook, guideline, conference
    external_id = Column(String(100), nullable=True, index=True)  # PMID, DOI, ISBN
    title = Column(Text, nullable=False)
    subtitle = Column(Text, nullable=True)
    
    # Authorship
    authors = Column(ARRAY(String), default=list)
    corresponding_author = Column(String(200), nullable=True)
    author_affiliations = Column(JSON, default=dict)
    
    # Publication details
    journal = Column(String(200), nullable=True, index=True)
    publisher = Column(String(200), nullable=True)
    publication_date = Column(DateTime, nullable=True, index=True)
    volume = Column(String(20), nullable=True)
    issue = Column(String(20), nullable=True)
    pages = Column(String(50), nullable=True)
    
    # Quality and impact metrics
    impact_factor = Column(Float, nullable=True, index=True)
    citation_count = Column(Integer, default=0, index=True)
    credibility_score = Column(Float, default=50.0, index=True)  # 0-100 scale
    evidence_level = Column(String(10), nullable=True, index=True)
    study_design = Column(String(100), nullable=True)  # RCT, cohort, case-control, etc.
    
    # Content analysis
    abstract = Column(Text, nullable=True)
    keywords = Column(ARRAY(String), default=list)
    mesh_terms = Column(ARRAY(String), default=list)
    medical_concepts = Column(ARRAY(String), default=list)
    
    # Validation and quality control
    last_validated = Column(DateTime, nullable=True)
    validation_notes = Column(Text, nullable=True)
    peer_reviewed = Column(Boolean, default=False)
    retracted = Column(Boolean, default=False)
    retraction_reason = Column(Text, nullable=True)
    
    # Access and availability
    open_access = Column(Boolean, default=False)
    pdf_url = Column(String(500), nullable=True)
    doi_url = Column(String(500), nullable=True)
    
    # Relationships
    chapters = relationship("AliveChapter", secondary=chapter_source_mapping, back_populates="sources")
    
    @validates('credibility_score')
    def validate_credibility(self, key, score):
        if score < 0 or score > 100:
            raise ValueError("Credibility score must be between 0 and 100")
        return score

class AliveChapter(UUPBaseModel):
    """Dynamic, self-updating medical content chapters"""
    __tablename__ = "alive_chapters"
    
    # Basic chapter information
    title = Column(String(500), nullable=False, index=True)
    slug = Column(String(200), nullable=False, unique=True, index=True)
    subtitle = Column(String(500), nullable=True)
    specialty = Column(String(100), default="neurosurgery", index=True)
    subspecialty = Column(String(100), nullable=True, index=True)
    
    # Content structure
    content_sections = Column(JSON, default=list)  # Structured content with sections
    summary = Column(Text, nullable=True)
    learning_objectives = Column(ARRAY(String), default=list)
    key_points = Column(ARRAY(String), default=list)
    
    # Dynamic updating configuration
    monitoring_keywords = Column(ARRAY(String), default=list)
    update_frequency = Column(String(20), default="weekly", index=True)  # daily, weekly, monthly
    auto_update_enabled = Column(Boolean, default=True, index=True)
    last_updated = Column(DateTime, nullable=True, index=True)
    next_update_due = Column(DateTime, nullable=True, index=True)
    
    # Quality metrics
    quality_score = Column(Float, default=0.0, index=True)  # 0-100 scale
    completeness_score = Column(Float, default=0.0)
    accuracy_score = Column(Float, default=0.0)
    freshness_score = Column(Float, default=0.0)
    evidence_strength = Column(Float, default=0.0)
    
    # User engagement and feedback
    view_count = Column(Integer, default=0, index=True)
    bookmark_count = Column(Integer, default=0)
    rating_average = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    feedback_summary = Column(JSON, default=dict)
    
    # Content management
    word_count = Column(Integer, default=0)
    reading_time_minutes = Column(Integer, default=0)
    difficulty_level = Column(String(20), default="intermediate")  # beginner, intermediate, advanced
    target_audience = Column(ARRAY(String), default=list)  # residents, attendings, students
    
    # Relationships
    sources = relationship("EvidenceSource", secondary=chapter_source_mapping, back_populates="chapters")
    anatomical_structures = relationship("AnatomicalStructure", secondary=chapter_anatomy_mapping, back_populates="chapters")
    updates = relationship("ContentUpdate", back_populates="chapter", cascade="all, delete-orphan")
    
    @validates('quality_score', 'completeness_score', 'accuracy_score', 'freshness_score')
    def validate_scores(self, key, score):
        if score < 0 or score > 100:
            raise ValueError(f"{key} must be between 0 and 100")
        return score
    
    @validates('update_frequency')
    def validate_update_frequency(self, key, frequency):
        valid_frequencies = ['daily', 'weekly', 'monthly', 'quarterly']
        if frequency not in valid_frequencies:
            raise ValueError(f"Update frequency must be one of {valid_frequencies}")
        return frequency

class ContentUpdate(UUPBaseModel):
    """Track all content updates and changes"""
    __tablename__ = "content_updates"
    
    # Update identification
    chapter_id = Column(UUID(as_uuid=True), ForeignKey('alive_chapters.id'), nullable=False, index=True)
    source_id = Column(UUID(as_uuid=True), ForeignKey('evidence_sources.id'), nullable=True)
    
    # Update details
    update_type = Column(String(50), nullable=False, index=True)  # addition, modification, contradiction, deletion
    section_affected = Column(String(200), nullable=True)
    content_before = Column(Text, nullable=True)
    content_after = Column(Text, nullable=True)
    change_summary = Column(Text, nullable=True)
    
    # AI analysis and scoring
    confidence_score = Column(Float, default=0.0, index=True)  # 0-100 scale
    relevance_score = Column(Float, default=0.0, index=True)
    impact_assessment = Column(String(20), default="low", index=True)  # low, medium, high, critical
    quality_prediction = Column(Float, default=0.0)
    
    # Human oversight and review
    human_reviewed = Column(Boolean, default=False, index=True)
    reviewer_id = Column(UUID(as_uuid=True), nullable=True)
    review_notes = Column(Text, nullable=True)
    approved = Column(Boolean, default=False, index=True)
    applied_at = Column(DateTime, nullable=True, index=True)
    
    # Source publication details
    source_publication_id = Column(String(100), nullable=True)  # PMID, DOI
    publication_date = Column(DateTime, nullable=True)
    
    # Relationships
    chapter = relationship("AliveChapter", back_populates="updates")
    source = relationship("EvidenceSource")
    
    @validates('update_type')
    def validate_update_type(self, key, update_type):
        valid_types = ['addition', 'modification', 'contradiction', 'deletion', 'correction']
        if update_type not in valid_types:
            raise ValueError(f"Update type must be one of {valid_types}")
        return update_type
    
    @validates('impact_assessment')
    def validate_impact(self, key, impact):
        valid_impacts = ['low', 'medium', 'high', 'critical']
        if impact not in valid_impacts:
            raise ValueError(f"Impact assessment must be one of {valid_impacts}")
        return impact

class ContentEmbedding(UUPBaseModel):
    """Vector embeddings for semantic search and content similarity"""
    __tablename__ = "content_embeddings"
    
    # Content reference
    content_type = Column(String(50), nullable=False, index=True)  # chapter, procedure, anatomy, source
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    section_id = Column(String(100), nullable=True)  # For subsections
    
    # Embedding data
    embedding = Column(VECTOR(768), nullable=False)  # 768-dimensional vector
    embedding_model = Column(String(100), default="text-embedding-ada-002")
    embedding_version = Column(String(20), default="1.0")
    
    # Content metadata
    content_text = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    content_length = Column(Integer, default=0)
    
    # Search optimization
    keywords = Column(ARRAY(String), default=list)
    medical_concepts = Column(ARRAY(String), default=list)
    anatomical_terms = Column(ARRAY(String), default=list)
    
    # Quality and relevance
    content_quality = Column(Float, default=0.0)
    medical_accuracy = Column(Float, default=0.0)
    
    # Indexes for efficient vector similarity search
    __table_args__ = (
        Index('ix_content_embeddings_vector', 'embedding', postgresql_using='ivfflat'),
        Index('ix_content_embeddings_content_type_id', 'content_type', 'content_id'),
        UniqueConstraint('content_type', 'content_id', 'section_id', name='uq_content_embedding'),
    )

# Create all tables
def create_neurosurgical_tables(engine):
    """Create all neurosurgical database tables"""
    Base.metadata.create_all(engine)

# Export models for use in other modules
__all__ = [
    'AnatomicalStructure',
    'SurgicalProcedure', 
    'EvidenceSource',
    'AliveChapter',
    'ContentUpdate',
    'ContentEmbedding',
    'procedure_anatomy_mapping',
    'chapter_source_mapping',
    'chapter_anatomy_mapping'
]
