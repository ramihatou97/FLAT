# 🔐 API Key Setup & Security Guide

## Medical Knowledge Platform - Production API Key Configuration

This guide provides **exact instructions** for securing and configuring all API keys for the Medical Knowledge Platform with the latest AI providers: **Gemini 2.5 Pro with Deep Search & Deep Think**, **Claude Opus 4.1 Extended**, **OpenAI GPT-4**, and **Perplexity Pro**.

---

## 📋 Required API Keys

### 1. **OpenAI GPT-4 & GPT-4 Turbo**
- **Provider**: OpenAI
- **Get Key**: https://platform.openai.com/api-keys
- **Required Format**: `sk-proj-...` (Project API keys recommended)

### 2. **Google Gemini 2.5 Pro with Deep Search & Deep Think**
- **Provider**: Google AI Studio
- **Get Key**: https://aistudio.google.com/
- **Required Format**: `AIzaSy...`
- **Features**: Deep Search, Deep Think, Enhanced reasoning

### 3. **Anthropic Claude Opus 4.1 Extended**
- **Provider**: Anthropic
- **Get Key**: https://console.anthropic.com/
- **Required Format**: `sk-ant-api03-...`
- **Features**: Extended reasoning, Long context

### 4. **Perplexity Pro with Online Search**
- **Provider**: Perplexity AI
- **Get Key**: https://www.perplexity.ai/settings/api
- **Required Format**: `pplx-...`
- **Features**: Real-time web search, Latest information

---

## 🔧 Step-by-Step Setup

### **Step 1: Create .env File**

1. **Copy the template**:
   ```bash
   cd medical_platform_v3
   cp .env.template .env
   ```

2. **Edit the .env file** with your actual API keys:
   ```bash
   nano .env
   # or
   code .env
   ```

### **Step 2: Configure API Keys in .env**

Replace the placeholder values with your **actual API keys**:

```env
# =============================================================================
# AI PROVIDER API KEYS (REQUIRED)
# =============================================================================

# OpenAI API Key - Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY="sk-proj-YOUR-ACTUAL-OPENAI-KEY-HERE"
OPENAI_ORG_ID="org-YOUR-ORGANIZATION-ID"  # Optional

# Google Gemini API Key - Get from: https://aistudio.google.com/
GEMINI_API_KEY="AIzaSyYOUR-ACTUAL-GEMINI-API-KEY-HERE"
GEMINI_PROJECT_ID="your-google-cloud-project-id"

# Anthropic Claude API Key - Get from: https://console.anthropic.com/
CLAUDE_API_KEY="sk-ant-api03-YOUR-ACTUAL-CLAUDE-KEY-HERE"

# Perplexity API Key - Get from: https://www.perplexity.ai/settings/api
PERPLEXITY_API_KEY="pplx-YOUR-ACTUAL-PERPLEXITY-KEY-HERE"

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# PostgreSQL Database Settings
DATABASE_URL="postgresql://medical_user:YOUR_SECURE_PASSWORD@localhost:5432/medical_platform"
DATABASE_HOST="localhost"
DATABASE_PORT="5432"
DATABASE_NAME="medical_platform"
DATABASE_USER="medical_user"
DATABASE_PASSWORD="YOUR_SECURE_DATABASE_PASSWORD"

# Redis Cache Settings
REDIS_URL="redis://localhost:6379/0"
REDIS_HOST="localhost"
REDIS_PORT="6379"
REDIS_PASSWORD=""  # Set if Redis requires auth

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

# Secret key for JWT tokens (generate with: openssl rand -hex 32)
SECRET_KEY="YOUR-VERY-SECURE-SECRET-KEY-MINIMUM-32-CHARACTERS-LONG"

# =============================================================================
# RESEARCH DATA SOURCES
# =============================================================================

# PubMed API Settings
PUBMED_EMAIL="your-email@domain.com"  # Required for API access
PUBMED_API_KEY=""  # Optional, for higher rate limits

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

### **Step 3: Generate Secure Values**

1. **Generate SECRET_KEY**:
   ```bash
   openssl rand -hex 32
   ```

2. **Create strong database password**:
   ```bash
   openssl rand -base64 32
   ```

---

## 🛡️ Security Best Practices

### **File Permissions**
```bash
# Secure the .env file
chmod 600 .env
chown root:root .env  # or your application user

# Ensure .env is in .gitignore
echo ".env" >> .gitignore
```

### **Environment Variable Validation**
The platform automatically validates all required environment variables on startup. Run the validation script:

```bash
python scripts/deployment_validation.py
```

### **API Key Security Checklist**

- ✅ **Never commit .env to version control**
- ✅ **Use different keys for development/staging/production**
- ✅ **Rotate keys regularly (quarterly recommended)**
- ✅ **Monitor API usage and costs**
- ✅ **Set up budget alerts for each provider**
- ✅ **Use project-scoped keys when available**
- ✅ **Implement rate limiting and usage monitoring**

---

## 🚀 Provider-Specific Setup Instructions

### **OpenAI Setup**
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Choose "Project" scope for better security
4. Copy the key (starts with `sk-proj-`)
5. Set up billing limits in your account settings

### **Google Gemini 2.5 Pro Setup**
1. Go to https://aistudio.google.com/
2. Click "Get API key"
3. Create new project or use existing
4. Enable "Advanced Features" for Deep Search & Deep Think
5. Copy the API key (starts with `AIzaSy`)

```env
# Enable advanced Gemini features
GEMINI_MODEL="gemini-2.5-pro"
GEMINI_FEATURES="deep_search,deep_think"
```

### **Claude Opus 4.1 Extended Setup**
1. Go to https://console.anthropic.com/
2. Navigate to "API Keys"
3. Create new key
4. Select "Claude-3 Opus" access level
5. Copy the key (starts with `sk-ant-api03-`)

```env
# Enable Claude extended reasoning
CLAUDE_MODEL="claude-3-opus-20240229"
CLAUDE_FEATURES="extended_reasoning"
```

### **Perplexity Pro Setup**
1. Go to https://www.perplexity.ai/settings/api
2. Generate new API key
3. Choose "Pro" tier for online search capabilities
4. Copy the key (starts with `pplx-`)

```env
# Enable Perplexity online search
PERPLEXITY_MODEL="llama-3.1-sonar-huge-128k-online"
PERPLEXITY_FEATURES="online_search"
```

---

## 💰 Budget Configuration

Set daily and monthly budget limits to control costs:

```env
# Daily Budget Limits (USD)
DAILY_BUDGET_OPENAI="15.00"
DAILY_BUDGET_GEMINI="15.00"
DAILY_BUDGET_CLAUDE="15.00"
DAILY_BUDGET_PERPLEXITY="15.00"
TOTAL_MONTHLY_BUDGET="1800.00"
```

### **Budget Monitoring**
Monitor usage with built-in endpoints:
```bash
# Check all provider budgets
curl http://localhost:8000/api/keys/budgets/all

# Check specific provider usage
curl http://localhost:8000/api/keys/usage/openai
```

---

## 📊 Reference Library Setup

### **Step 1: Create Library Structure**
```bash
mkdir -p reference_library/{neurosurgery,general_medicine,research_papers,guidelines}

# Example directory structure:
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

### **Step 2: Configure Library Path**
```env
# File Storage Configuration
REFERENCE_LIBRARY_PATH="./reference_library"
AUTO_INDEX_UPLOADS="true"
MAX_UPLOAD_SIZE="100MB"
ALLOWED_FILE_TYPES=".pdf,.docx,.txt,.md,.ppt,.pptx"
```

### **Step 3: Upload Initial Documents**
```bash
# Copy your medical documents
cp /path/to/your/medical/pdfs/* reference_library/neurosurgery/
cp /path/to/research/papers/* reference_library/research_papers/2024/

# The system will automatically index these files on startup
```

---

## 🔍 Validation & Testing

### **Validate Configuration**
```bash
# Run comprehensive validation
python scripts/deployment_validation.py

# Test API key connectivity
curl -X GET http://localhost:8000/api/keys/services/health

# Test AI providers
curl -X POST http://localhost:8000/api/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test prompt", "provider": "gemini"}'
```

### **Health Check Endpoints**
```bash
# Basic health
curl http://localhost:8000/api/health

# Detailed health with AI providers
curl http://localhost:8000/api/monitoring/health/detailed

# Service-specific health
curl http://localhost:8000/api/keys/services/health
```

---

## 🐳 Docker Deployment

### **Using Docker Compose (Recommended)**
```bash
# Copy environment file
cp .env docker/.env

# Start production stack
cd docker
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f medical-platform
```

### **Environment Variables in Docker**
For Docker deployment, you can also use environment variable injection:

```yaml
# docker-compose.prod.yml
services:
  medical-platform:
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - PERPLEXITY_API_KEY=${PERPLEXITY_API_KEY}
```

---

## 🚨 Troubleshooting

### **Common Issues**

1. **"API key validation failed"**
   ```bash
   # Check key format and validity
   python -c "
   import os
   from src.core.api_key_manager import api_key_manager
   import asyncio
   asyncio.run(api_key_manager.check_service_health('openai'))
   "
   ```

2. **"Database connection failed"**
   ```bash
   # Test database connection
   psql $DATABASE_URL -c "SELECT 1;"
   ```

3. **"Redis connection failed"**
   ```bash
   # Test Redis connection
   redis-cli -u $REDIS_URL ping
   ```

### **Debug Mode**
For troubleshooting, temporarily enable debug mode:
```env
DEBUG="true"
LOG_LEVEL="DEBUG"
```

---

## 📞 Support & Resources

- **API Documentation**: http://localhost:8000/docs
- **Interactive API Docs**: http://localhost:8000/api/docs/interactive
- **Monitoring Dashboard**: http://localhost:8000/api/monitoring/dashboard
- **Health Status**: http://localhost:8000/api/monitoring/health/detailed

### **Provider Documentation**
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Google Gemini Docs](https://ai.google.dev/docs)
- [Anthropic Claude Docs](https://docs.anthropic.com/)
- [Perplexity API Docs](https://docs.perplexity.ai/)

---

## 🎯 Quick Deployment Commands

```bash
# Complete setup in one go:

# 1. Environment setup
cp .env.template .env
# Edit .env with your API keys

# 2. Install dependencies
pip install -r requirements.txt

# 3. Validate configuration
python scripts/deployment_validation.py

# 4. Start production server
python scripts/production_startup.py

# 5. Test deployment
curl http://localhost:8000/api/health
```

## 🔄 **Content Integration System**

The platform now includes a **unified content integration system** that seamlessly handles content from both API integrations and web interface extractions.

### **Content Integration Features:**
- ✅ **Unified processing** for API and web interface content
- ✅ **Automatic medical concept extraction** from all sources
- ✅ **Cross-provider content search** with semantic similarity
- ✅ **Content consolidation** and duplicate detection
- ✅ **Web import interface** for manual content integration

### **Web Interface Content Import:**
1. **Access the Content Import Interface**: `content_import_interface.html`
2. **Generate content** using AI provider web interfaces:
   - **Gemini AI Studio**: Use Deep Search & Deep Think
   - **Claude.ai**: Use Extended Reasoning & File Analysis
   - **ChatGPT**: Use Code Interpreter & DALL-E
   - **Perplexity**: Use Real-time Search & Citations
3. **Copy the generated content**
4. **Import via the web interface** or API endpoint
5. **Content is automatically processed** and made searchable

### **API Endpoints for Content Integration:**
```bash
# Import web interface content
POST /api/content/import/web-content

# Import files (exported conversations)
POST /api/content/import/file

# Search integrated content
POST /api/content/search

# View integration statistics
GET /api/content/statistics

# Export integrated content
GET /api/content/export
```

### **Usage Workflow:**
1. **Use AI providers** through their web interfaces with advanced features
2. **Extract valuable content** (research, analysis, insights)
3. **Import into platform** using the content integration system
4. **Search and analyze** across all integrated content
5. **Merge and consolidate** similar content from different sources

---

**The platform is now ready for production use with complete AI provider integration! 🚀**