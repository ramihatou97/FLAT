# 🚀 Medical Knowledge Platform - Production Deployment Guide

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL 14+
- Redis 6+
- Node.js 18+ (for frontend)
- 4GB+ RAM
- 20GB+ storage

---

## 🔐 API Keys Configuration

### **Step 1: Create Environment File**

Create `.env` file in the root directory:

```bash
# Copy the template
cp .env.template .env
```

### **Step 2: Configure API Keys**

Edit `.env` file with your real API keys:

```env
# =============================================================================
# AI PROVIDER API KEYS (REQUIRED)
# =============================================================================

# OpenAI API Key
OPENAI_API_KEY="sk-proj-your-actual-openai-key-here"
OPENAI_ORG_ID="org-your-organization-id"  # Optional

# Google Gemini API Key
GEMINI_API_KEY="AIzaSyYour-Actual-Gemini-API-Key-Here"
GEMINI_PROJECT_ID="your-google-cloud-project-id"

# Anthropic Claude API Key
CLAUDE_API_KEY="sk-ant-api03-your-actual-claude-key-here"

# Perplexity API Key
PERPLEXITY_API_KEY="pplx-your-actual-perplexity-key-here"

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# PostgreSQL Database
DATABASE_URL="postgresql://username:password@localhost:5432/medical_platform"
DATABASE_HOST="localhost"
DATABASE_PORT="5432"
DATABASE_NAME="medical_platform"
DATABASE_USER="medical_user"
DATABASE_PASSWORD="secure_password_here"

# Redis Cache
REDIS_URL="redis://localhost:6379/0"
REDIS_HOST="localhost"
REDIS_PORT="6379"
REDIS_PASSWORD=""  # Set if Redis requires auth

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

# Secret key for JWT tokens (generate with: openssl rand -hex 32)
SECRET_KEY="your-very-secure-secret-key-minimum-32-characters-long"

# API Rate Limiting
RATE_LIMIT_PER_MINUTE="60"
RATE_LIMIT_PER_HOUR="1000"

# CORS Origins (comma-separated)
ALLOWED_ORIGINS="http://localhost:3000,https://yourdomain.com"

# =============================================================================
# AI PROVIDER SETTINGS
# =============================================================================

# Daily Budget Limits (USD)
DAILY_BUDGET_OPENAI="15.00"
DAILY_BUDGET_GEMINI="15.00"
DAILY_BUDGET_CLAUDE="15.00"
DAILY_BUDGET_PERPLEXITY="15.00"
TOTAL_MONTHLY_BUDGET="1800.00"

# Model Specifications
GEMINI_MODEL="gemini-2.5-pro"  # Gemini 2.5 Pro with Deep Search
CLAUDE_MODEL="claude-3-opus-20240229"  # Claude Opus 4.1 Extended
OPENAI_MODEL="gpt-4"
PERPLEXITY_MODEL="llama-3.1-sonar-huge-128k-online"

# =============================================================================
# RESEARCH DATA SOURCES
# =============================================================================

# PubMed API Settings
PUBMED_API_KEY=""  # Optional, for higher rate limits
PUBMED_EMAIL="your-email@domain.com"  # Required for API access

# Google Scholar Settings (if using ScholARLY)
SCHOLAR_PROXY=""  # Optional proxy for Scholar access

# =============================================================================
# FILE STORAGE CONFIGURATION
# =============================================================================

# Upload Settings
MAX_UPLOAD_SIZE="100MB"
ALLOWED_FILE_TYPES=".pdf,.docx,.txt,.md"
UPLOAD_DIRECTORY="./uploads"

# Reference Library Path
REFERENCE_LIBRARY_PATH="./reference_library"

# =============================================================================
# LOGGING & MONITORING
# =============================================================================

# Log Level
LOG_LEVEL="INFO"
LOG_FILE="./logs/app.log"

# Monitoring
ENABLE_METRICS="true"
METRICS_PORT="9090"

# =============================================================================
# PRODUCTION SETTINGS
# =============================================================================

# Environment
ENVIRONMENT="production"
DEBUG="false"

# Server Settings
HOST="0.0.0.0"
PORT="8000"
WORKERS="4"
```

---

## 📁 Directory Structure Setup

Create the required directories:

```bash
# Create essential directories
mkdir -p logs
mkdir -p uploads
mkdir -p reference_library
mkdir -p data/embeddings
mkdir -p backups

# Set permissions
chmod 755 logs uploads reference_library
chmod 700 data  # Secure data directory
```

---

## 🗃️ Database Setup

### **Step 1: Install PostgreSQL**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
```

### **Step 2: Create Database**

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE medical_platform;
CREATE USER medical_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE medical_platform TO medical_user;

# Enable required extensions
\c medical_platform
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "vector";  # For semantic search

\q
```

### **Step 3: Install Redis**

```bash
# Ubuntu/Debian
sudo apt install redis-server

# macOS
brew install redis

# Windows
# Download from https://github.com/microsoftarchive/redis/releases
```

---

## 🔧 Backend Setup

### **Step 1: Install Python Dependencies**

```bash
cd medical_platform_v3

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install additional production dependencies
pip install gunicorn uvicorn[standard] psycopg2-binary redis python-multipart
```

### **Step 2: Database Migration**

```bash
# Initialize database tables
python -c "
from src.core.database import create_tables
import asyncio
asyncio.run(create_tables())
"
```

### **Step 3: Initialize AI Services**

```bash
# Test API connections
python -c "
from src.core.api_key_manager import api_key_manager
import asyncio

async def test_apis():
    await api_key_manager.initialize()
    health = await api_key_manager.get_all_service_health()
    print('AI Services Status:', health)

asyncio.run(test_apis())
"
```

---

## 📚 Reference Library Setup

### **Step 1: Create Library Structure**

```bash
mkdir -p reference_library/{neurosurgery,general_medicine,research_papers,guidelines}

# Example structure:
reference_library/
├── neurosurgery/
│   ├── glioblastoma/
│   ├── dbs/
│   └── surgical_techniques/
├── general_medicine/
│   ├── anatomy/
│   └── physiology/
├── research_papers/
│   ├── 2024/
│   ├── 2023/
│   └── classics/
└── guidelines/
    ├── clinical/
    └── research/
```

### **Step 2: Upload Reference Materials**

```bash
# Copy your medical documents to appropriate folders
cp /path/to/your/medical/pdfs/* reference_library/neurosurgery/
cp /path/to/research/papers/* reference_library/research_papers/2024/

# The system will automatically index these files
```

---

## 🎯 AI Provider Specific Setup

### **Gemini 2.5 Pro with Deep Search & Deep Think**

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create API key
3. Enable Advanced Features:
   ```bash
   # Add to .env
   GEMINI_API_KEY="AIzaSy..."
   GEMINI_MODEL="gemini-2.5-pro"
   GEMINI_FEATURES="deep_search,deep_think"
   ```

### **Claude Opus 4.1 Extended**

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create API key
3. Configure extended reasoning:
   ```bash
   # Add to .env
   CLAUDE_API_KEY="sk-ant-api03-..."
   CLAUDE_MODEL="claude-3-opus-20240229"
   CLAUDE_FEATURES="extended_reasoning"
   ```

### **OpenAI GPT-4**

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create API key
3. Set up billing limits

### **Perplexity Pro**

1. Go to [Perplexity API](https://www.perplexity.ai/settings/api)
2. Create API key
3. Enable online search features

---

## 🚀 Production Deployment

### **Step 1: Install Production Server**

```bash
# Install production WSGI server
pip install gunicorn

# Create systemd service file
sudo nano /etc/systemd/system/medical-platform.service
```

Add this configuration:

```ini
[Unit]
Description=Medical Knowledge Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/medical_platform_v3
Environment="PATH=/path/to/medical_platform_v3/venv/bin"
ExecStart=/path/to/medical_platform_v3/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker simple_main:app --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### **Step 2: Configure Nginx (Optional)**

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # File upload size limit
    client_max_body_size 100M;
}
```

### **Step 3: Start Services**

```bash
# Enable and start the service
sudo systemctl enable medical-platform
sudo systemctl start medical-platform

# Check status
sudo systemctl status medical-platform

# View logs
sudo journalctl -u medical-platform -f
```

---

## 🔒 Security Checklist

### **API Keys Security**

- ✅ Store API keys in `.env` file (never in code)
- ✅ Add `.env` to `.gitignore`
- ✅ Use different keys for development/production
- ✅ Rotate keys regularly
- ✅ Monitor API usage and costs

### **Database Security**

- ✅ Use strong passwords
- ✅ Enable SSL connections
- ✅ Restrict database access by IP
- ✅ Regular backups
- ✅ Keep PostgreSQL updated

### **Application Security**

- ✅ Enable HTTPS in production
- ✅ Configure CORS properly
- ✅ Implement rate limiting
- ✅ Regular security updates
- ✅ Monitor logs for suspicious activity

---

## 🧪 Testing Deployment

### **Step 1: Health Checks**

```bash
# Test basic health
curl http://localhost:8000/api/health

# Test detailed monitoring
curl http://localhost:8000/api/monitoring/health/detailed

# Test AI providers
curl http://localhost:8000/api/keys/services/health
```

### **Step 2: Functional Tests**

```bash
# Test semantic search
curl -X POST http://localhost:8000/api/search/ \
  -H "Content-Type: application/json" \
  -d '{"query": "glioblastoma treatment", "search_type": "semantic"}'

# Test AI generation
curl -X POST http://localhost:8000/api/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain brain anatomy", "provider": "gemini"}'
```

---

## 📊 Monitoring Setup

### **Step 1: Log Monitoring**

```bash
# Monitor application logs
tail -f logs/app.log

# Monitor system logs
sudo journalctl -u medical-platform -f
```

### **Step 2: Performance Monitoring**

```bash
# Monitor API response times
curl http://localhost:8000/api/monitoring/metrics/system

# Monitor AI provider costs
curl http://localhost:8000/api/keys/budgets/all
```

---

## 🆘 Troubleshooting

### **Common Issues**

1. **Database Connection Failed**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql

   # Test connection
   psql -h localhost -U medical_user -d medical_platform
   ```

2. **Redis Connection Failed**
   ```bash
   # Check Redis status
   sudo systemctl status redis

   # Test connection
   redis-cli ping
   ```

3. **AI Provider API Errors**
   ```bash
   # Check API key validity
   curl http://localhost:8000/api/keys/services/health

   # Monitor rate limits
   curl http://localhost:8000/api/keys/budgets/all
   ```

4. **File Upload Issues**
   ```bash
   # Check directory permissions
   ls -la uploads/

   # Fix permissions
   chmod 755 uploads/
   ```

---

## 🎯 Quick Start Commands

```bash
# Complete setup in one go:

# 1. Environment setup
cp .env.template .env
# Edit .env with your API keys

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start services
redis-server &
sudo systemctl start postgresql

# 4. Initialize database
python -c "from src.core.database import create_tables; import asyncio; asyncio.run(create_tables())"

# 5. Start application
uvicorn simple_main:app --host 0.0.0.0 --port 8000

# 6. Test deployment
curl http://localhost:8000/api/health
```

---

## 📞 Support

- **Documentation**: `http://localhost:8000/api/docs/interactive`
- **Health Status**: `http://localhost:8000/api/monitoring/health/detailed`
- **API Reference**: `http://localhost:8000/api/docs`

**The platform is now ready for production use! 🚀**