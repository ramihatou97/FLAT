#!/bin/bash

# Medical Platform Development Script
# Quick development environment setup and management

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker/docker-compose.yml"
ENV_FILE=".env"

# Logging functions
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

# Show help
show_help() {
    echo "Medical Platform Development Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start development environment"
    echo "  stop      Stop all services"
    echo "  restart   Restart all services"
    echo "  logs      Show logs for all services"
    echo "  logs-api  Show backend API logs"
    echo "  logs-web  Show frontend logs"
    echo "  logs-db   Show database logs"
    echo "  shell     Open shell in backend container"
    echo "  db-shell  Open database shell"
    echo "  migrate   Run database migrations"
    echo "  reset-db  Reset database (WARNING: destroys all data)"
    echo "  test      Run tests"
    echo "  build     Rebuild all containers"
    echo "  clean     Clean up containers and volumes"
    echo "  status    Show service status"
    echo "  help      Show this help message"
    echo ""
}

# Start development environment
start_dev() {
    log "Starting development environment..."
    
    # Create .env if it doesn't exist
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example $ENV_FILE
            warning "Created $ENV_FILE from .env.example"
        fi
    fi
    
    # Start services
    docker-compose -f $COMPOSE_FILE up -d
    
    # Wait for services
    log "Waiting for services to be ready..."
    sleep 15
    
    # Check if services are running
    if docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
        success "Development environment started!"
        echo ""
        echo "🌐 Access URLs:"
        echo "   Frontend:  http://localhost:3000"
        echo "   Backend:   http://localhost:8000"
        echo "   API Docs:  http://localhost:8000/docs"
        echo ""
        echo "📝 Useful commands:"
        echo "   View logs: $0 logs"
        echo "   Stop:      $0 stop"
        echo ""
    else
        error "Some services failed to start. Check logs with: $0 logs"
    fi
}

# Stop services
stop_dev() {
    log "Stopping development environment..."
    docker-compose -f $COMPOSE_FILE down
    success "Development environment stopped"
}

# Restart services
restart_dev() {
    log "Restarting development environment..."
    docker-compose -f $COMPOSE_FILE restart
    success "Development environment restarted"
}

# Show logs
show_logs() {
    case "$1" in
        "api"|"backend")
            docker-compose -f $COMPOSE_FILE logs -f backend
            ;;
        "web"|"frontend")
            docker-compose -f $COMPOSE_FILE logs -f frontend
            ;;
        "db"|"database")
            docker-compose -f $COMPOSE_FILE logs -f db
            ;;
        *)
            docker-compose -f $COMPOSE_FILE logs -f
            ;;
    esac
}

# Open shell in backend container
open_shell() {
    log "Opening shell in backend container..."
    docker-compose -f $COMPOSE_FILE exec backend /bin/bash
}

# Open database shell
open_db_shell() {
    log "Opening database shell..."
    docker-compose -f $COMPOSE_FILE exec db psql -U medical -d medical_platform
}

# Run migrations
run_migrations() {
    log "Running database migrations..."
    docker-compose -f $COMPOSE_FILE exec backend alembic upgrade head
    success "Migrations completed"
}

# Reset database
reset_database() {
    warning "This will destroy all data in the database!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "Resetting database..."
        docker-compose -f $COMPOSE_FILE down -v
        docker-compose -f $COMPOSE_FILE up -d db redis
        sleep 10
        docker-compose -f $COMPOSE_FILE up -d backend
        sleep 5
        run_migrations
        success "Database reset completed"
    else
        log "Database reset cancelled"
    fi
}

# Run tests
run_tests() {
    log "Running tests..."
    docker-compose -f $COMPOSE_FILE exec backend python -m pytest tests/ -v
}

# Build containers
build_containers() {
    log "Building containers..."
    docker-compose -f $COMPOSE_FILE build --no-cache
    success "Containers built"
}

# Clean up
clean_up() {
    warning "This will remove all containers, networks, and volumes!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "Cleaning up..."
        docker-compose -f $COMPOSE_FILE down -v --remove-orphans
        docker system prune -f
        success "Cleanup completed"
    else
        log "Cleanup cancelled"
    fi
}

# Show status
show_status() {
    log "Service status:"
    docker-compose -f $COMPOSE_FILE ps
    echo ""
    log "Resource usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# Main function
main() {
    case "$1" in
        "start")
            start_dev
            ;;
        "stop")
            stop_dev
            ;;
        "restart")
            restart_dev
            ;;
        "logs")
            show_logs "$2"
            ;;
        "logs-api"|"logs-backend")
            show_logs "api"
            ;;
        "logs-web"|"logs-frontend")
            show_logs "web"
            ;;
        "logs-db"|"logs-database")
            show_logs "db"
            ;;
        "shell")
            open_shell
            ;;
        "db-shell")
            open_db_shell
            ;;
        "migrate")
            run_migrations
            ;;
        "reset-db")
            reset_database
            ;;
        "test")
            run_tests
            ;;
        "build")
            build_containers
            ;;
        "clean")
            clean_up
            ;;
        "status")
            show_status
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        "")
            show_help
            ;;
        *)
            error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
