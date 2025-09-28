# Requirements Structure

This directory contains the organized requirements files for the Medical Knowledge Platform.

## Files Overview

- **`base.txt`** - Core dependencies required for basic platform functionality
- **`dev.txt`** - Development dependencies (includes base.txt + testing/development tools)
- **`production.txt`** - Production optimizations (includes base.txt + production-specific packages)

## Usage

### For Development
```bash
pip install -r requirements/dev.txt
```

### For Production
```bash
pip install -r requirements/production.txt
```

### For Railway Deployment
Use the root `requirements.txt` file which contains fixed versions optimized for Railway's deployment environment.

## Package Organization

- **Core dependencies** are in `base.txt`
- **Development tools** (pytest, black, flake8, etc.) are in `dev.txt`
- **Production optimizations** (uvloop, orjson, monitoring tools) are in `production.txt`
- **Deployment-specific** versions are in root `requirements.txt`

## Notes

- Perplexity API access is via direct HTTP requests (no official PyPI package)
- All AI provider packages (OpenAI, Anthropic, Google) use the latest stable versions
- PostgreSQL support includes both asyncpg and psycopg2-binary for compatibility