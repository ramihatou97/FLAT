#!/bin/bash

# Medical Platform Deployment Script
# Automated deployment with health checks and rollback capability

set -e

echo "🚀 Starting Medical Platform Deployment..."

# Configuration
PROJECT_NAME="medical-platform"
COMPOSE_FILE="docker/docker-compose.yml"
ENV_FILE=".env"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Setup environment
setup_environment() {
    log "Setting up environment..."
    
    # Copy environment file if it doesn't exist
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example $ENV_FILE
            warning "Created $ENV_FILE from .env.example. Please update with your configuration."
        else
            error ".env.example not found. Please create $ENV_FILE manually."
            exit 1
        fi
    fi
    
    success "Environment setup completed"
}

# Build and start services
deploy_services() {
    log "Building and starting services..."
    
    # Build images
    log "Building Docker images..."
    docker-compose -f $COMPOSE_FILE build --no-cache
    
    # Start services
    log "Starting services..."
    docker-compose -f $COMPOSE_FILE up -d
    
    success "Services started"
}

# Health checks
health_check() {
    log "Performing health checks..."
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30
    
    # Check database
    log "Checking database connection..."
    if docker-compose -f $COMPOSE_FILE exec -T db pg_isready -U medical -d medical_platform; then
        success "Database is ready"
    else
        error "Database health check failed"
        return 1
    fi
    
    # Check Redis
    log "Checking Redis connection..."
    if docker-compose -f $COMPOSE_FILE exec -T redis redis-cli ping | grep -q "PONG"; then
        success "Redis is ready"
    else
        error "Redis health check failed"
        return 1
    fi
    
    # Check backend API
    log "Checking backend API..."
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/api/health &> /dev/null; then
            success "Backend API is ready"
            break
        else
            log "Attempt $attempt/$max_attempts: Backend API not ready yet..."
            sleep 10
            ((attempt++))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        error "Backend API health check failed after $max_attempts attempts"
        return 1
    fi
    
    # Check frontend
    log "Checking frontend..."
    max_attempts=20
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:3000 &> /dev/null; then
            success "Frontend is ready"
            break
        else
            log "Attempt $attempt/$max_attempts: Frontend not ready yet..."
            sleep 10
            ((attempt++))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        error "Frontend health check failed after $max_attempts attempts"
        return 1
    fi
    
    success "All health checks passed"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    # Wait a bit more for database to be fully ready
    sleep 10
    
    # Run Alembic migrations
    if docker-compose -f $COMPOSE_FILE exec -T backend alembic upgrade head; then
        success "Database migrations completed"
    else
        error "Database migrations failed"
        return 1
    fi
}

# Display deployment information
show_deployment_info() {
    log "Deployment completed successfully! 🎉"
    echo ""
    echo "📊 Service URLs:"
    echo "   Frontend:  http://localhost:3000"
    echo "   Backend:   http://localhost:8000"
    echo "   API Docs:  http://localhost:8000/docs"
    echo "   Database:  localhost:5432"
    echo "   Redis:     localhost:6379"
    echo ""
    echo "🔧 Management Commands:"
    echo "   View logs:     docker-compose -f $COMPOSE_FILE logs -f"
    echo "   Stop services: docker-compose -f $COMPOSE_FILE down"
    echo "   Restart:       docker-compose -f $COMPOSE_FILE restart"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Open http://localhost:3000 in your browser"
    echo "   2. Configure AI API keys in $ENV_FILE (optional)"
    echo "   3. Create your first chapter or search medical content"
    echo ""
}

# Rollback function
rollback() {
    error "Deployment failed. Rolling back..."
    docker-compose -f $COMPOSE_FILE down
    error "Rollback completed"
    exit 1
}

# Main deployment process
main() {
    # Set trap for rollback on error
    trap rollback ERR
    
    check_prerequisites
    setup_environment
    deploy_services
    
    # Run health checks
    if ! health_check; then
        rollback
    fi
    
    # Run migrations
    if ! run_migrations; then
        rollback
    fi
    
    show_deployment_info
}

# Run main function
main "$@"
