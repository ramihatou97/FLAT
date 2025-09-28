# Technical Documentation

## System Architecture

### Overview

The Medical Knowledge Platform is built using a modern, scalable architecture with clear separation of concerns:

- **Backend**: FastAPI application with PostgreSQL database
- **Frontend**: React SPA with TypeScript
- **AI Integration**: OpenAI GPT-4 for content generation
- **Document Processing**: PDF extraction and analysis
- **Search**: Semantic search capabilities

## Database Design

### Core Models

#### Chapter Model
```python
class AliveChapter(Base):
    id: UUID
    title: str
    content: Text
    slug: str
    status: enum (draft, review, published)
    created_at: datetime
    updated_at: datetime
    metadata: JSON
```

#### Content Update Model
```python
class ContentUpdate(Base):
    id: UUID
    chapter_id: UUID (foreign key)
    update_type: str
    change_summary: Text
    confidence_score: float
    source_publication_id: str
    approved: bool
    applied_at: datetime
```

#### Evidence Source Model
```python
class EvidenceSource(Base):
    id: UUID
    title: str
    authors: List[str]
    publication_date: datetime
    source_type: str (pubmed, textbook, guideline)
    credibility_score: float
    pmid: str (optional)
    doi: str (optional)
```

### Relationships

- **Chapter ↔ Sources**: Many-to-many relationship for evidence tracking
- **Chapter ↔ Updates**: One-to-many for update history
- **Chapter ↔ Anatomy**: Many-to-many for anatomical references

## API Design

### RESTful Endpoints

#### Chapters
```
GET    /api/chapters          # List chapters
POST   /api/chapters          # Create chapter
GET    /api/chapters/{id}     # Get chapter
PUT    /api/chapters/{id}     # Update chapter
DELETE /api/chapters/{id}     # Delete chapter
```

#### Content Generation
```
POST   /api/ai/generate       # Generate content
POST   /api/ai/validate       # Validate content
POST   /api/ai/synthesize     # Synthesize from sources
```

#### Document Processing
```
POST   /api/pdf/upload        # Upload PDF
GET    /api/pdf/status/{id}   # Check processing status
```

#### Search
```
POST   /api/search            # Semantic search
GET    /api/search/suggest    # Search suggestions
```

### Request/Response Formats

#### Chapter Creation
```json
{
  "title": "Brain Tumor Management",
  "content": "Chapter content...",
  "metadata": {
    "specialty": "neurosurgery",
    "difficulty": "advanced",
    "keywords": ["glioma", "craniotomy"]
  }
}
```

#### AI Content Generation
```json
{
  "prompt": "Generate content about...",
  "context": "neurosurgical",
  "max_tokens": 1000,
  "temperature": 0.7
}
```

## Frontend Architecture

### Component Structure

```
src/
├── components/
│   ├── neurosurgical/
│   │   ├── NeurosurgicalDashboard.tsx
│   │   ├── AliveChapterEditor.tsx
│   │   └── AnatomicalViewer.tsx
│   └── search/
│       └── SemanticSearchInterface.tsx
├── services/
│   ├── apiService.ts
│   └── neurosurgicalApi.ts
└── App.tsx
```

### State Management

- **Local State**: React hooks for component state
- **API State**: React Query for server state management
- **Form State**: React Hook Form for form handling

### API Integration

```typescript
class NeurosurgicalApiService {
  async getChapters(params: ChapterSearchParams): Promise<ApiResponse>
  async createChapter(data: ChapterData): Promise<ApiResponse>
  async generateContent(request: ContentGenerationRequest): Promise<ApiResponse>
  async searchContent(query: string): Promise<ApiResponse>
}
```

## AI Integration

### Content Generation Pipeline

1. **Input Processing**: Clean and validate user input
2. **Context Building**: Add relevant medical context
3. **AI Generation**: Call OpenAI GPT-4 API
4. **Post-processing**: Validate and format output
5. **Quality Check**: Ensure medical accuracy

### Prompt Engineering

```python
def build_medical_prompt(topic: str, context: str) -> str:
    return f"""
    Generate medical content about {topic}.

    Context: {context}

    Requirements:
    - Use proper medical terminology
    - Include evidence-based information
    - Structure with clear sections
    - Maintain clinical accuracy

    Format the response in markdown.
    """
```

## Document Processing

### PDF Processing Pipeline

1. **Upload**: Secure file upload with validation
2. **Extraction**: Text and image extraction using PyMuPDF
3. **OCR**: Optical character recognition for scanned documents
4. **NLP**: Medical entity recognition and extraction
5. **Storage**: Structured storage in database

### Medical Content Extraction

```python
class MedicalPDFProcessor:
    def extract_medical_content(self, pdf_path: str) -> MedicalDocument:
        # Extract text, figures, and metadata
        # Identify medical entities
        # Structure content by sections
        # Return processed document
```

## Search Implementation

### Semantic Search

- **Embedding Generation**: Convert text to vector embeddings
- **Vector Storage**: Store embeddings in PostgreSQL with pgvector
- **Similarity Search**: Find semantically similar content
- **Ranking**: Relevance scoring and result ranking

```python
class SemanticSearch:
    def search(self, query: str, filters: dict) -> List[SearchResult]:
        # Generate query embedding
        # Search vector database
        # Apply filters and ranking
        # Return results
```

## Security

### Authentication

- **JWT Tokens**: Secure token-based authentication
- **Token Refresh**: Automatic token renewal
- **Role-based Access**: User permissions and roles

### API Security

- **Rate Limiting**: Prevent API abuse
- **Input Validation**: Sanitize all inputs
- **CORS**: Proper cross-origin configuration
- **HTTPS**: SSL/TLS encryption

## Performance

### Database Optimization

- **Indexing**: Optimized database indexes
- **Connection Pooling**: Efficient database connections
- **Query Optimization**: Optimized SQL queries

### Frontend Optimization

- **Code Splitting**: Lazy loading of components
- **Caching**: Browser and API caching
- **Bundle Optimization**: Optimized build size

### AI Performance

- **Caching**: Cache frequently requested content
- **Async Processing**: Non-blocking AI operations
- **Rate Limiting**: Manage API usage

## Monitoring and Logging

### Application Monitoring

- **Health Checks**: System health endpoints
- **Performance Metrics**: Response times and throughput
- **Error Tracking**: Exception monitoring
- **Usage Analytics**: User behavior tracking

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Structured logging with contextual information
logger.info("Chapter created", extra={
    "chapter_id": chapter.id,
    "user_id": user.id,
    "action": "create_chapter"
})
```

## Testing

### Backend Testing

```python
# Unit tests
def test_chapter_creation():
    chapter = create_chapter(title="Test", content="Content")
    assert chapter.title == "Test"

# Integration tests
def test_api_chapter_creation():
    response = client.post("/api/chapters", json=chapter_data)
    assert response.status_code == 201
```

### Frontend Testing

```typescript
// Component tests
test('renders chapter list', () => {
  render(<ChapterList chapters={mockChapters} />);
  expect(screen.getByText('Chapter 1')).toBeInTheDocument();
});

// Integration tests
test('creates new chapter', async () => {
  // Test complete user flow
});
```

## Deployment

### Docker Configuration

```dockerfile
# Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Configuration

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./medical_platform_v3
    environment:
      - DATABASE_URL=postgresql://...
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"

  database:
    image: postgres:14
    environment:
      - POSTGRES_DB=medical_platform
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
```

### Production Considerations

- **Environment Variables**: Secure configuration management
- **SSL Certificates**: HTTPS configuration
- **Database Backups**: Automated backup strategy
- **Scaling**: Horizontal scaling configuration
- **Monitoring**: Production monitoring setup

## Development Workflow

### Local Development

1. **Setup Environment**: Install dependencies
2. **Database Setup**: Run migrations and seed data
3. **Start Services**: Backend and frontend development servers
4. **Development**: Code changes with hot reload

### CI/CD Pipeline

1. **Code Quality**: Linting and formatting checks
2. **Testing**: Automated test execution
3. **Build**: Docker image building
4. **Deploy**: Automated deployment to staging/production

### Code Standards

- **Python**: PEP 8, Black formatting, type hints
- **TypeScript**: ESLint rules, Prettier formatting
- **Git**: Conventional commits, feature branches
- **Documentation**: Inline comments and docstrings