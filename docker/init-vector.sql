-- =============================================================================
-- Medical Knowledge Platform - Vector Database Initialization
-- =============================================================================
-- Initialize pgvector extension and create vector tables for semantic search
-- =============================================================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create vector embedding table for semantic search
CREATE TABLE IF NOT EXISTS document_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL,
    chunk_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(384) NOT NULL,  -- Sentence-BERT embedding dimension
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_document_embeddings_document_id ON document_embeddings(document_id);
CREATE INDEX IF NOT EXISTS idx_document_embeddings_chunk_id ON document_embeddings(chunk_id);
CREATE INDEX IF NOT EXISTS idx_document_embeddings_created_at ON document_embeddings(created_at);

-- Create vector similarity index (HNSW for fast approximate nearest neighbor search)
CREATE INDEX IF NOT EXISTS idx_document_embeddings_vector
ON document_embeddings USING hnsw (embedding vector_cosine_ops);

-- Create GIN index for metadata queries
CREATE INDEX IF NOT EXISTS idx_document_embeddings_metadata
ON document_embeddings USING gin (metadata);

-- Create medical concepts table for neurosurgical terminology
CREATE TABLE IF NOT EXISTS medical_concepts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    term VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    definition TEXT,
    synonyms TEXT[],
    embedding vector(384),
    specialty VARCHAR(100) DEFAULT 'neurosurgery',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create unique index for medical terms
CREATE UNIQUE INDEX IF NOT EXISTS idx_medical_concepts_term_category
ON medical_concepts(term, category);

-- Create vector index for concept similarity
CREATE INDEX IF NOT EXISTS idx_medical_concepts_vector
ON medical_concepts USING hnsw (embedding vector_cosine_ops);

-- Create research papers table for literature analysis
CREATE TABLE IF NOT EXISTS research_papers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    authors TEXT[],
    abstract TEXT,
    journal VARCHAR(255),
    publication_date DATE,
    doi VARCHAR(255),
    pmid VARCHAR(50),
    keywords TEXT[],
    full_text_url TEXT,
    pdf_path TEXT,
    embedding vector(384),
    citation_count INTEGER DEFAULT 0,
    impact_factor REAL,
    specialty VARCHAR(100) DEFAULT 'neurosurgery',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for research papers
CREATE INDEX IF NOT EXISTS idx_research_papers_title ON research_papers USING gin (to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_research_papers_abstract ON research_papers USING gin (to_tsvector('english', abstract));
CREATE INDEX IF NOT EXISTS idx_research_papers_keywords ON research_papers USING gin (keywords);
CREATE INDEX IF NOT EXISTS idx_research_papers_publication_date ON research_papers(publication_date);
CREATE INDEX IF NOT EXISTS idx_research_papers_specialty ON research_papers(specialty);
CREATE UNIQUE INDEX IF NOT EXISTS idx_research_papers_doi ON research_papers(doi) WHERE doi IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_research_papers_pmid ON research_papers(pmid) WHERE pmid IS NOT NULL;

-- Create vector index for paper similarity
CREATE INDEX IF NOT EXISTS idx_research_papers_vector
ON research_papers USING hnsw (embedding vector_cosine_ops);

-- Create chapters table for content management
CREATE TABLE IF NOT EXISTS chapters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    content TEXT,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    keywords TEXT[],
    embedding vector(384),
    difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 5),
    estimated_reading_time INTEGER, -- in minutes
    references TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for chapters
CREATE INDEX IF NOT EXISTS idx_chapters_title ON chapters USING gin (to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_chapters_content ON chapters USING gin (to_tsvector('english', content));
CREATE INDEX IF NOT EXISTS idx_chapters_category ON chapters(category);
CREATE INDEX IF NOT EXISTS idx_chapters_keywords ON chapters USING gin (keywords);
CREATE INDEX IF NOT EXISTS idx_chapters_difficulty ON chapters(difficulty_level);

-- Create vector index for chapter similarity
CREATE INDEX IF NOT EXISTS idx_chapters_vector
ON chapters USING hnsw (embedding vector_cosine_ops);

-- Create user queries table for analytics
CREATE TABLE IF NOT EXISTS user_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_text TEXT NOT NULL,
    query_type VARCHAR(50) NOT NULL, -- 'semantic', 'keyword', 'ai_generation'
    user_id UUID,
    session_id UUID,
    embedding vector(384),
    results_count INTEGER,
    response_time_ms INTEGER,
    satisfaction_score INTEGER CHECK (satisfaction_score BETWEEN 1 AND 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for analytics
CREATE INDEX IF NOT EXISTS idx_user_queries_query_type ON user_queries(query_type);
CREATE INDEX IF NOT EXISTS idx_user_queries_created_at ON user_queries(created_at);
CREATE INDEX IF NOT EXISTS idx_user_queries_user_id ON user_queries(user_id);
CREATE INDEX IF NOT EXISTS idx_user_queries_response_time ON user_queries(response_time_ms);

-- Create vector index for query similarity analysis
CREATE INDEX IF NOT EXISTS idx_user_queries_vector
ON user_queries USING hnsw (embedding vector_cosine_ops);

-- Create function for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for auto-updating timestamps
CREATE TRIGGER update_document_embeddings_updated_at BEFORE UPDATE ON document_embeddings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_research_papers_updated_at BEFORE UPDATE ON research_papers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chapters_updated_at BEFORE UPDATE ON chapters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function for vector similarity search
CREATE OR REPLACE FUNCTION similarity_search(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10,
    table_name text DEFAULT 'document_embeddings'
)
RETURNS TABLE(
    id UUID,
    content TEXT,
    similarity FLOAT,
    metadata JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF table_name = 'document_embeddings' THEN
        RETURN QUERY
        SELECT
            de.id,
            de.content,
            1 - (de.embedding <=> query_embedding) as similarity,
            de.metadata
        FROM document_embeddings de
        WHERE 1 - (de.embedding <=> query_embedding) > match_threshold
        ORDER BY de.embedding <=> query_embedding
        LIMIT match_count;
    ELSIF table_name = 'research_papers' THEN
        RETURN QUERY
        SELECT
            rp.id,
            COALESCE(rp.abstract, rp.title) as content,
            1 - (rp.embedding <=> query_embedding) as similarity,
            jsonb_build_object(
                'title', rp.title,
                'authors', rp.authors,
                'journal', rp.journal,
                'doi', rp.doi
            ) as metadata
        FROM research_papers rp
        WHERE rp.embedding IS NOT NULL
        AND 1 - (rp.embedding <=> query_embedding) > match_threshold
        ORDER BY rp.embedding <=> query_embedding
        LIMIT match_count;
    END IF;
END;
$$;

-- Insert some sample neurosurgical concepts
INSERT INTO medical_concepts (term, category, definition, synonyms, specialty) VALUES
    ('Glioblastoma', 'Tumor', 'The most aggressive and common primary brain tumor in adults', ARRAY['GBM', 'Grade IV astrocytoma'], 'neurosurgery'),
    ('Deep Brain Stimulation', 'Procedure', 'Surgical procedure to treat movement disorders using electrical stimulation', ARRAY['DBS'], 'neurosurgery'),
    ('Craniotomy', 'Procedure', 'Surgical removal of part of the skull to access the brain', ARRAY['Cranial surgery'], 'neurosurgery'),
    ('Hydrocephalus', 'Condition', 'Accumulation of cerebrospinal fluid in brain ventricles', ARRAY['Water on the brain'], 'neurosurgery'),
    ('Aneurysm', 'Condition', 'Abnormal bulging of blood vessel wall in the brain', ARRAY['Cerebral aneurysm'], 'neurosurgery')
ON CONFLICT (term, category) DO NOTHING;

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO medical_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO medical_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO medical_user;