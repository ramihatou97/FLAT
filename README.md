# Medical Knowledge Platform

**A Personal Medical Encyclopedia with AI-Powered Content Synthesis**

[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://semver.org)
[![Status](https://img.shields.io/badge/status-production%20ready-green.svg)]()

## Overview

This is a streamlined, production-ready medical knowledge management platform designed for personal use. It combines AI-powered content synthesis, document processing, and intelligent search to create a comprehensive medical reference system.

### Key Features

- **AI Content Synthesis**: Generate medical content using multiple AI providers
- **Document Processing**: Extract and process medical literature and textbooks
- **Intelligent Search**: Semantic search across medical content
- **Personal Chapters**: Create and maintain personal medical notes and chapters
- **Real-time Updates**: Monitor and update content based on new research

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+

### Installation

1. **Clone and Setup**
```bash
git clone <repository-url>
cd koo
cp .env.example .env  # Configure your environment variables
```

2. **Start with Docker**
```bash
docker-compose up -d
```

3. **Manual Setup** (alternative)
```bash
# Backend
cd medical_platform_v3
pip install -r requirements.txt
python -m uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm start
```

4. **Access the Application**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Architecture

### Backend (`/medical_platform_v3/`)
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database with medical models
- **SQLAlchemy** - ORM for database operations
- **AI Integration** - OpenAI GPT-4 for content generation

### Frontend (`/frontend/`)
- **React 18** - Modern frontend framework
- **TypeScript** - Type-safe JavaScript
- **Material-UI** - Component library
- **Lucide Icons** - Modern icon set

### Database (`/database/`)
- **Neurosurgical Models** - Specialized medical data structures
- **Migration System** - Database version control
- **Seed Data** - Initial medical content

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/medical_platform

# AI Services
OPENAI_API_KEY=your_openai_api_key

# Application
DEBUG=False
SECRET_KEY=your_secret_key
```

### API Keys Required

- **OpenAI API Key** - For AI content generation
- **PubMed API Key** - For literature search (optional)

## Usage

### Creating Medical Content

1. **Navigate to Chapters** - Access the chapter management interface
2. **Create New Chapter** - Use the AI-assisted chapter creation
3. **Upload Documents** - Process PDFs and extract medical content
4. **Search Literature** - Find relevant research and publications

### API Endpoints

```bash
# Get all chapters
GET /api/chapters

# Create new chapter
POST /api/chapters

# Search content
POST /api/search

# Upload PDF
POST /api/pdf/upload

# Generate AI content
POST /api/ai/generate
```

## Development

### Project Structure

```
koo/
├── medical_platform_v3/     # Main backend application
│   ├── src/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configurations
│   │   ├── domain/         # Domain models
│   │   └── services/       # Business logic
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   └── services/       # API services
│   └── package.json
├── database/              # Database models and migrations
└── docker-compose.yml     # Container orchestration
```

### Running Tests

```bash
# Backend tests
cd medical_platform_v3
pytest

# Frontend tests
cd frontend
npm test
```

### Adding New Features

1. **Backend Changes**
   - Add new API endpoints in `medical_platform_v3/src/api/`
   - Implement business logic in `medical_platform_v3/src/services/`
   - Add database models in `database/neurosurgical_models.py`

2. **Frontend Changes**
   - Create components in `frontend/src/components/`
   - Add API calls in `frontend/src/services/`
   - Update routing and navigation

## Deployment

### Production Deployment

1. **Build Docker Images**
```bash
docker-compose -f docker-compose.prod.yml build
```

2. **Deploy to Production**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Environment Setup**
   - Configure production database
   - Set up SSL certificates
   - Configure monitoring and logging

### Monitoring

- **Health Checks**: Built-in health monitoring endpoints
- **Logging**: Structured logging with configurable levels
- **Metrics**: Performance monitoring and analytics

## Contributing

### Code Style

- **Python**: Follow PEP 8, use Black formatter
- **TypeScript**: Use ESLint and Prettier
- **Git**: Conventional commits

### Development Workflow

1. Create feature branch
2. Implement changes with tests
3. Run linting and tests
4. Submit pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the [API Documentation](http://localhost:8000/docs)
- Review the [Technical Documentation](./TECHNICAL_DOCS.md)
- Create an issue in the repository

---

**Note**: This is a personal medical knowledge platform. Ensure proper medical supervision when using for clinical purposes.