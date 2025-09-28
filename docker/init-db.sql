-- Initialize Medical Platform Database
-- Enable required extensions

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable UUID extension for unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable full text search extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

-- Create custom types for medical platform
DO $$ BEGIN
    CREATE TYPE content_type AS ENUM (
        'chapter',
        'research_paper', 
        'pdf_document',
        'clinical_trial',
        'case_study',
        'medical_image',
        'video_content'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE chapter_status AS ENUM (
        'draft',
        'review', 
        'published',
        'archived'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE synthesis_status AS ENUM (
        'pending',
        'processing',
        'completed',
        'failed'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create indexes for better performance
-- These will be created after tables are created by Alembic

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function for medical concept extraction (placeholder)
CREATE OR REPLACE FUNCTION extract_medical_concepts(content TEXT)
RETURNS TEXT[] AS $$
BEGIN
    -- This is a simplified version - in production, this would use
    -- medical terminology databases like UMLS or SNOMED CT
    RETURN string_to_array(
        regexp_replace(
            lower(content), 
            '[^a-z0-9\s]', 
            ' ', 
            'g'
        ), 
        ' '
    );
END;
$$ LANGUAGE plpgsql;

-- Function for content similarity scoring
CREATE OR REPLACE FUNCTION calculate_content_similarity(
    content1 TEXT,
    content2 TEXT
) RETURNS FLOAT AS $$
BEGIN
    -- Simple similarity calculation using trigram similarity
    RETURN similarity(content1, content2);
END;
$$ LANGUAGE plpgsql;

-- Create materialized view for search optimization (will be created after tables)
-- This will be handled by the application after initial migration

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE medical_platform TO medical;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO medical;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO medical;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO medical;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO medical;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO medical;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO medical;

-- Create initial admin user (will be handled by application)
-- INSERT INTO users (username, email, role, is_active) 
-- VALUES ('admin', 'admin@medical-platform.com', 'admin', true);

-- Log initialization completion
INSERT INTO public.system_logs (level, message, timestamp) 
VALUES ('INFO', 'Database initialization completed successfully', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;
