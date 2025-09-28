"""
Alembic Migration: Create Neurosurgical Encyclopedia Schema
Revision ID: 001_neurosurgical_base
Create Date: 2024-12-27
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_neurosurgical_base'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Create neurosurgical encyclopedia database schema"""
    
    # Enable pgvector extension for vector similarity search
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create anatomical_structures table
    op.create_table(
        'anatomical_structures',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        
        # Basic identification
        sa.Column('name', sa.String(200), nullable=False, index=True),
        sa.Column('latin_name', sa.String(200), nullable=True, index=True),
        sa.Column('synonyms', postgresql.ARRAY(sa.String), default=list),
        sa.Column('abbreviations', postgresql.ARRAY(sa.String), default=list),
        
        # Hierarchical organization
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('anatomical_structures.id'), nullable=True),
        sa.Column('level', sa.Integer, default=0, index=True),
        sa.Column('path', sa.String(500), nullable=True, index=True),
        
        # 3D spatial data
        sa.Column('coordinates_3d', sa.JSON, default=dict),
        sa.Column('mesh_data', sa.JSON, default=dict),
        sa.Column('visualization_config', sa.JSON, default=dict),
        
        # Clinical and surgical relevance
        sa.Column('clinical_significance', sa.Text, nullable=True),
        sa.Column('surgical_approaches', postgresql.ARRAY(sa.String), default=list),
        sa.Column('common_pathologies', postgresql.ARRAY(sa.String), default=list),
        sa.Column('eloquent_area', sa.Boolean, default=False),
        sa.Column('vascular_supply', sa.JSON, default=dict),
        
        # Anatomical properties
        sa.Column('tissue_type', sa.String(100), nullable=True),
        sa.Column('functional_role', sa.Text, nullable=True),
        sa.Column('developmental_origin', sa.String(100), nullable=True),
        
        # UUP Base Model fields
        sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('medical_context', sa.JSON, default=dict, nullable=False),
        sa.Column('confidence_score', sa.String(10), nullable=True),
        sa.Column('validation_status', sa.String(20), default='pending', nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('version', sa.String(20), default='1.0', nullable=False),
        sa.Column('metadata', sa.JSON, default=dict, nullable=False),
        sa.Column('tags', sa.JSON, default=list, nullable=False),
    )
    
    # Create surgical_procedures table
    op.create_table(
        'surgical_procedures',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        
        # Basic information
        sa.Column('name', sa.String(300), nullable=False, index=True),
        sa.Column('short_name', sa.String(100), nullable=True),
        sa.Column('cpt_code', sa.String(10), nullable=True, index=True),
        sa.Column('icd_codes', postgresql.ARRAY(sa.String), default=list),
        
        # Classification and complexity
        sa.Column('specialty', sa.String(100), default="neurosurgery", index=True),
        sa.Column('subspecialty', sa.String(100), nullable=True, index=True),
        sa.Column('complexity_score', sa.Integer, default=5, index=True),
        sa.Column('duration_minutes', sa.Integer, nullable=True),
        sa.Column('anesthesia_type', sa.String(100), nullable=True),
        
        # Clinical context
        sa.Column('indications', postgresql.ARRAY(sa.String), default=list),
        sa.Column('contraindications', postgresql.ARRAY(sa.String), default=list),
        sa.Column('relative_contraindications', postgresql.ARRAY(sa.String), default=list),
        
        # Procedure details
        sa.Column('step_by_step_guide', sa.JSON, default=list),
        sa.Column('equipment_required', postgresql.ARRAY(sa.String), default=list),
        sa.Column('positioning', sa.String(200), nullable=True),
        sa.Column('surgical_approach', sa.String(200), nullable=True),
        
        # Complications and outcomes
        sa.Column('complications', sa.JSON, default=dict),
        sa.Column('success_rate', sa.Float, nullable=True),
        sa.Column('mortality_rate', sa.Float, nullable=True),
        sa.Column('morbidity_rate', sa.Float, nullable=True),
        
        # Evidence and guidelines
        sa.Column('evidence_level', sa.String(10), nullable=True, index=True),
        sa.Column('guideline_recommendations', sa.JSON, default=dict),
        sa.Column('outcome_measures', sa.JSON, default=dict),
        
        # Learning and training
        sa.Column('learning_curve', sa.String(100), nullable=True),
        sa.Column('training_requirements', postgresql.ARRAY(sa.String), default=list),
        sa.Column('simulation_available', sa.Boolean, default=False),
        
        # UUP Base Model fields
        sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('medical_context', sa.JSON, default=dict, nullable=False),
        sa.Column('confidence_score', sa.String(10), nullable=True),
        sa.Column('validation_status', sa.String(20), default='pending', nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('version', sa.String(20), default='1.0', nullable=False),
        sa.Column('metadata', sa.JSON, default=dict, nullable=False),
        sa.Column('tags', sa.JSON, default=list, nullable=False),
    )
    
    # Create evidence_sources table
    op.create_table(
        'evidence_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        
        # Source identification
        sa.Column('source_type', sa.String(50), nullable=False, index=True),
        sa.Column('external_id', sa.String(100), nullable=True, index=True),
        sa.Column('title', sa.Text, nullable=False),
        sa.Column('subtitle', sa.Text, nullable=True),
        
        # Authorship
        sa.Column('authors', postgresql.ARRAY(sa.String), default=list),
        sa.Column('corresponding_author', sa.String(200), nullable=True),
        sa.Column('author_affiliations', sa.JSON, default=dict),
        
        # Publication details
        sa.Column('journal', sa.String(200), nullable=True, index=True),
        sa.Column('publisher', sa.String(200), nullable=True),
        sa.Column('publication_date', sa.DateTime, nullable=True, index=True),
        sa.Column('volume', sa.String(20), nullable=True),
        sa.Column('issue', sa.String(20), nullable=True),
        sa.Column('pages', sa.String(50), nullable=True),
        
        # Quality and impact metrics
        sa.Column('impact_factor', sa.Float, nullable=True, index=True),
        sa.Column('citation_count', sa.Integer, default=0, index=True),
        sa.Column('credibility_score', sa.Float, default=50.0, index=True),
        sa.Column('evidence_level', sa.String(10), nullable=True, index=True),
        sa.Column('study_design', sa.String(100), nullable=True),
        
        # Content analysis
        sa.Column('abstract', sa.Text, nullable=True),
        sa.Column('keywords', postgresql.ARRAY(sa.String), default=list),
        sa.Column('mesh_terms', postgresql.ARRAY(sa.String), default=list),
        sa.Column('medical_concepts', postgresql.ARRAY(sa.String), default=list),
        
        # Validation and quality control
        sa.Column('last_validated', sa.DateTime, nullable=True),
        sa.Column('validation_notes', sa.Text, nullable=True),
        sa.Column('peer_reviewed', sa.Boolean, default=False),
        sa.Column('retracted', sa.Boolean, default=False),
        sa.Column('retraction_reason', sa.Text, nullable=True),
        
        # Access and availability
        sa.Column('open_access', sa.Boolean, default=False),
        sa.Column('pdf_url', sa.String(500), nullable=True),
        sa.Column('doi_url', sa.String(500), nullable=True),
        
        # UUP Base Model fields
        sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('medical_context', sa.JSON, default=dict, nullable=False),
        sa.Column('confidence_score', sa.String(10), nullable=True),
        sa.Column('validation_status', sa.String(20), default='pending', nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('version', sa.String(20), default='1.0', nullable=False),
        sa.Column('metadata', sa.JSON, default=dict, nullable=False),
        sa.Column('tags', sa.JSON, default=list, nullable=False),
    )
    
    # Create alive_chapters table
    op.create_table(
        'alive_chapters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        
        # Basic chapter information
        sa.Column('title', sa.String(500), nullable=False, index=True),
        sa.Column('slug', sa.String(200), nullable=False, unique=True, index=True),
        sa.Column('subtitle', sa.String(500), nullable=True),
        sa.Column('specialty', sa.String(100), default="neurosurgery", index=True),
        sa.Column('subspecialty', sa.String(100), nullable=True, index=True),
        
        # Content structure
        sa.Column('content_sections', sa.JSON, default=list),
        sa.Column('summary', sa.Text, nullable=True),
        sa.Column('learning_objectives', postgresql.ARRAY(sa.String), default=list),
        sa.Column('key_points', postgresql.ARRAY(sa.String), default=list),
        
        # Dynamic updating configuration
        sa.Column('monitoring_keywords', postgresql.ARRAY(sa.String), default=list),
        sa.Column('update_frequency', sa.String(20), default="weekly", index=True),
        sa.Column('auto_update_enabled', sa.Boolean, default=True, index=True),
        sa.Column('last_updated', sa.DateTime, nullable=True, index=True),
        sa.Column('next_update_due', sa.DateTime, nullable=True, index=True),
        
        # Quality metrics
        sa.Column('quality_score', sa.Float, default=0.0, index=True),
        sa.Column('completeness_score', sa.Float, default=0.0),
        sa.Column('accuracy_score', sa.Float, default=0.0),
        sa.Column('freshness_score', sa.Float, default=0.0),
        sa.Column('evidence_strength', sa.Float, default=0.0),
        
        # User engagement and feedback
        sa.Column('view_count', sa.Integer, default=0, index=True),
        sa.Column('bookmark_count', sa.Integer, default=0),
        sa.Column('rating_average', sa.Float, default=0.0),
        sa.Column('rating_count', sa.Integer, default=0),
        sa.Column('feedback_summary', sa.JSON, default=dict),
        
        # Content management
        sa.Column('word_count', sa.Integer, default=0),
        sa.Column('reading_time_minutes', sa.Integer, default=0),
        sa.Column('difficulty_level', sa.String(20), default="intermediate"),
        sa.Column('target_audience', postgresql.ARRAY(sa.String), default=list),
        
        # UUP Base Model fields
        sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('medical_context', sa.JSON, default=dict, nullable=False),
        sa.Column('confidence_score', sa.String(10), nullable=True),
        sa.Column('validation_status', sa.String(20), default='pending', nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('version', sa.String(20), default='1.0', nullable=False),
        sa.Column('metadata', sa.JSON, default=dict, nullable=False),
        sa.Column('tags', sa.JSON, default=list, nullable=False),
    )
    
    # Create content_updates table
    op.create_table(
        'content_updates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        
        # Update identification
        sa.Column('chapter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('alive_chapters.id'), nullable=False, index=True),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('evidence_sources.id'), nullable=True),
        
        # Update details
        sa.Column('update_type', sa.String(50), nullable=False, index=True),
        sa.Column('section_affected', sa.String(200), nullable=True),
        sa.Column('content_before', sa.Text, nullable=True),
        sa.Column('content_after', sa.Text, nullable=True),
        sa.Column('change_summary', sa.Text, nullable=True),
        
        # AI analysis and scoring
        sa.Column('confidence_score', sa.Float, default=0.0, index=True),
        sa.Column('relevance_score', sa.Float, default=0.0, index=True),
        sa.Column('impact_assessment', sa.String(20), default="low", index=True),
        sa.Column('quality_prediction', sa.Float, default=0.0),
        
        # Human oversight and review
        sa.Column('human_reviewed', sa.Boolean, default=False, index=True),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('review_notes', sa.Text, nullable=True),
        sa.Column('approved', sa.Boolean, default=False, index=True),
        sa.Column('applied_at', sa.DateTime, nullable=True, index=True),
        
        # Source publication details
        sa.Column('source_publication_id', sa.String(100), nullable=True),
        sa.Column('publication_date', sa.DateTime, nullable=True),
        
        # UUP Base Model fields
        sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('medical_context', sa.JSON, default=dict, nullable=False),
        sa.Column('confidence_score_meta', sa.String(10), nullable=True),
        sa.Column('validation_status', sa.String(20), default='pending', nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('version', sa.String(20), default='1.0', nullable=False),
        sa.Column('metadata', sa.JSON, default=dict, nullable=False),
        sa.Column('tags', sa.JSON, default=list, nullable=False),
    )
    
    # Create content_embeddings table for vector search
    op.create_table(
        'content_embeddings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        
        # Content reference
        sa.Column('content_type', sa.String(50), nullable=False, index=True),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('section_id', sa.String(100), nullable=True),
        
        # Embedding data
        sa.Column('embedding', postgresql.VECTOR(768), nullable=False),
        sa.Column('embedding_model', sa.String(100), default="text-embedding-ada-002"),
        sa.Column('embedding_version', sa.String(20), default="1.0"),
        
        # Content metadata
        sa.Column('content_text', sa.Text, nullable=False),
        sa.Column('content_hash', sa.String(64), nullable=False, index=True),
        sa.Column('content_length', sa.Integer, default=0),
        
        # Search optimization
        sa.Column('keywords', postgresql.ARRAY(sa.String), default=list),
        sa.Column('medical_concepts', postgresql.ARRAY(sa.String), default=list),
        sa.Column('anatomical_terms', postgresql.ARRAY(sa.String), default=list),
        
        # Quality and relevance
        sa.Column('content_quality', sa.Float, default=0.0),
        sa.Column('medical_accuracy', sa.Float, default=0.0),
        
        # UUP Base Model fields
        sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('medical_context', sa.JSON, default=dict, nullable=False),
        sa.Column('confidence_score', sa.String(10), nullable=True),
        sa.Column('validation_status', sa.String(20), default='pending', nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('version', sa.String(20), default='1.0', nullable=False),
        sa.Column('metadata', sa.JSON, default=dict, nullable=False),
        sa.Column('tags', sa.JSON, default=list, nullable=False),
    )
    
    # Create association tables for many-to-many relationships
    op.create_table(
        'procedure_anatomy_mapping',
        sa.Column('procedure_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('surgical_procedures.id'), primary_key=True),
        sa.Column('anatomy_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('anatomical_structures.id'), primary_key=True),
        sa.Column('relevance_score', sa.Float, default=1.0),
        sa.Column('surgical_significance', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now())
    )
    
    op.create_table(
        'chapter_source_mapping',
        sa.Column('chapter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('alive_chapters.id'), primary_key=True),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('evidence_sources.id'), primary_key=True),
        sa.Column('relevance_score', sa.Float, default=0.0),
        sa.Column('citation_context', sa.Text, nullable=True),
        sa.Column('evidence_weight', sa.Float, default=1.0),
        sa.Column('created_at', sa.DateTime, default=sa.func.now())
    )
    
    op.create_table(
        'chapter_anatomy_mapping',
        sa.Column('chapter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('alive_chapters.id'), primary_key=True),
        sa.Column('anatomy_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('anatomical_structures.id'), primary_key=True),
        sa.Column('relevance_score', sa.Float, default=0.0),
        sa.Column('created_at', sa.DateTime, default=sa.func.now())
    )
    
    # Create indexes for performance optimization
    
    # Vector similarity search index
    op.execute(
        'CREATE INDEX ix_content_embeddings_vector ON content_embeddings '
        'USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)'
    )
    
    # Composite indexes for common queries
    op.create_index('ix_content_embeddings_content_type_id', 'content_embeddings', ['content_type', 'content_id'])
    op.create_index('ix_alive_chapters_specialty_subspecialty', 'alive_chapters', ['specialty', 'subspecialty'])
    op.create_index('ix_surgical_procedures_complexity_specialty', 'surgical_procedures', ['complexity_score', 'specialty'])
    op.create_index('ix_evidence_sources_type_date', 'evidence_sources', ['source_type', 'publication_date'])
    op.create_index('ix_content_updates_chapter_type', 'content_updates', ['chapter_id', 'update_type'])
    
    # Unique constraints
    op.create_unique_constraint('uq_content_embedding', 'content_embeddings', ['content_type', 'content_id', 'section_id'])
    
    # Check constraints for data validation
    op.execute("ALTER TABLE surgical_procedures ADD CONSTRAINT ck_complexity_score CHECK (complexity_score >= 1 AND complexity_score <= 10)")
    op.execute("ALTER TABLE evidence_sources ADD CONSTRAINT ck_credibility_score CHECK (credibility_score >= 0 AND credibility_score <= 100)")
    op.execute("ALTER TABLE alive_chapters ADD CONSTRAINT ck_quality_scores CHECK (quality_score >= 0 AND quality_score <= 100)")

def downgrade():
    """Drop neurosurgical encyclopedia database schema"""
    
    # Drop tables in reverse order to handle foreign key constraints
    op.drop_table('chapter_anatomy_mapping')
    op.drop_table('chapter_source_mapping')
    op.drop_table('procedure_anatomy_mapping')
    op.drop_table('content_embeddings')
    op.drop_table('content_updates')
    op.drop_table('alive_chapters')
    op.drop_table('evidence_sources')
    op.drop_table('surgical_procedures')
    op.drop_table('anatomical_structures')
    
    # Drop pgvector extension
    op.execute('DROP EXTENSION IF EXISTS vector')
