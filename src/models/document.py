"""Document Library Models for Medical Knowledge Platform"""

from sqlalchemy import Column, String, Text, DateTime, JSON, Integer, Float, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid

from ..core.database import Base

class DocumentType(str, Enum):
    BOOK = "book"
    CHAPTER = "chapter"
    PAPER = "paper"
    REFERENCE = "reference"
    GUIDELINE = "guideline"
    CASE_STUDY = "case_study"
    REVIEW = "review"
    THESIS = "thesis"

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXTRACTING = "extracting"
    INDEXING = "indexing"

class Document(Base):
    """Main document library table"""

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    authors = Column(JSON, nullable=True)  # List of authors
    document_type = Column(String(50), nullable=False)  # DocumentType enum
    specialty = Column(String(100), nullable=True)
    subspecialty = Column(String(100), nullable=True)

    # File information
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    file_type = Column(String(10), nullable=False)  # pdf, docx, txt, etc.
    mime_type = Column(String(100), nullable=True)

    # Content extraction
    extracted_text = Column(Text, nullable=True)
    word_count = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True)

    # Processing status
    processing_status = Column(String(50), default=ProcessingStatus.PENDING.value)
    processing_progress = Column(Float, default=0.0)
    processing_log = Column(JSON, nullable=True)

    # Metadata
    publication_date = Column(DateTime, nullable=True)
    journal = Column(String(255), nullable=True)
    volume = Column(String(50), nullable=True)
    issue = Column(String(50), nullable=True)
    pages = Column(String(50), nullable=True)
    doi = Column(String(255), nullable=True)
    pmid = Column(String(50), nullable=True)
    isbn = Column(String(50), nullable=True)

    # Medical categorization
    keywords = Column(JSON, nullable=True)  # List of keywords
    medical_concepts = Column(JSON, nullable=True)  # Extracted medical concepts
    anatomical_structures = Column(JSON, nullable=True)
    procedures = Column(JSON, nullable=True)
    conditions = Column(JSON, nullable=True)

    # Quality and evidence
    evidence_level = Column(String(50), nullable=True)
    quality_score = Column(Float, nullable=True)
    credibility_score = Column(Float, nullable=True)
    citation_count = Column(Integer, default=0)

    # System fields
    uploaded_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    indexed_at = Column(DateTime, nullable=True)

    # Flags
    is_public = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)

    # Relationships
    figures = relationship("DocumentFigure", back_populates="document")
    extracts = relationship("DocumentExtract", back_populates="document")
    citations = relationship("DocumentCitation", back_populates="document")
    analyses = relationship("DocumentAnalysis", back_populates="document")

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "title": self.title,
            "authors": self.authors,
            "document_type": self.document_type,
            "specialty": self.specialty,
            "subspecialty": self.subspecialty,
            "original_filename": self.original_filename,
            "file_size_bytes": self.file_size_bytes,
            "file_type": self.file_type,
            "word_count": self.word_count,
            "page_count": self.page_count,
            "processing_status": self.processing_status,
            "processing_progress": self.processing_progress,
            "publication_date": self.publication_date.isoformat() if self.publication_date else None,
            "journal": self.journal,
            "doi": self.doi,
            "pmid": self.pmid,
            "keywords": self.keywords,
            "medical_concepts": self.medical_concepts,
            "evidence_level": self.evidence_level,
            "quality_score": self.quality_score,
            "citation_count": self.citation_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_public": self.is_public,
            "is_favorite": self.is_favorite,
        }

class DocumentFigure(Base):
    """Extracted figures from documents"""

    __tablename__ = "document_figures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)

    # Figure information
    figure_number = Column(String(20), nullable=True)
    caption = Column(Text, nullable=True)
    page_number = Column(Integer, nullable=True)

    # File information
    figure_path = Column(String(500), nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)

    # Classification
    figure_type = Column(String(50), nullable=True)  # anatomical, radiological, chart, etc.
    medical_concepts = Column(JSON, nullable=True)
    anatomical_structures = Column(JSON, nullable=True)

    # Quality
    quality_score = Column(Float, nullable=True)
    resolution_dpi = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="figures")

class DocumentExtract(Base):
    """Key text extracts from documents"""

    __tablename__ = "document_extracts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)

    # Extract information
    extract_type = Column(String(50), nullable=False)  # abstract, conclusion, key_finding, etc.
    content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    section_title = Column(String(255), nullable=True)

    # Metadata
    importance_score = Column(Float, nullable=True)
    medical_concepts = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="extracts")

class DocumentCitation(Base):
    """Citations found in documents"""

    __tablename__ = "document_citations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)

    # Citation information
    citation_text = Column(Text, nullable=False)
    citation_number = Column(Integer, nullable=True)
    page_number = Column(Integer, nullable=True)

    # Resolved citation details
    cited_title = Column(String(500), nullable=True)
    cited_authors = Column(JSON, nullable=True)
    cited_journal = Column(String(255), nullable=True)
    cited_year = Column(Integer, nullable=True)
    cited_doi = Column(String(255), nullable=True)
    cited_pmid = Column(String(50), nullable=True)

    # Validation
    is_verified = Column(Boolean, default=False)
    credibility_score = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="citations")

class DocumentAnalysis(Base):
    """AI-powered analysis results for documents"""

    __tablename__ = "document_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)

    # Analysis information
    analysis_type = Column(String(50), nullable=False)  # comprehensive, summary, key_points, terminology
    analysis_content = Column(Text, nullable=False)

    # AI metadata
    ai_provider = Column(String(50), nullable=True)  # gemini, claude, openai, perplexity
    ai_model = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)

    # Analysis metadata
    analysis_metadata = Column(JSON, nullable=True)  # Additional analysis-specific data
    confidence_score = Column(Float, nullable=True)

    # System fields
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=True)

    # Relationships
    document = relationship("Document", back_populates="analyses")

class LibraryCollection(Base):
    """Document collections/folders"""

    __tablename__ = "library_collections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Organization
    parent_id = Column(UUID(as_uuid=True), ForeignKey("library_collections.id"), nullable=True)
    specialty = Column(String(100), nullable=True)

    # Metadata
    document_count = Column(Integer, default=0)
    total_size_bytes = Column(Integer, default=0)

    # System fields
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Flags
    is_public = Column(Boolean, default=False)
    is_system = Column(Boolean, default=False)

class DocumentCollectionMapping(Base):
    """Many-to-many mapping between documents and collections"""

    __tablename__ = "document_collection_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    collection_id = Column(UUID(as_uuid=True), ForeignKey("library_collections.id"), nullable=False)

    added_at = Column(DateTime, default=datetime.utcnow)
    added_by = Column(String(100), nullable=True)