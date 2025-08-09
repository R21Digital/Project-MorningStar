#!/bin/bash
# MS11 Docker Entrypoint Script
# Handles initialization, migrations, and startup

set -e

# Colors for logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Environment validation
validate_environment() {
    log_info "Validating environment..."
    
    # Check required environment variables
    REQUIRED_VARS=("MS11_ENVIRONMENT")
    
    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var}" ]; then
            log_warning "Required environment variable $var is not set, using defaults"
        fi
    done
    
    # Set defaults
    export MS11_ENVIRONMENT=${MS11_ENVIRONMENT:-"production"}
    export MS11_LOG_LEVEL=${MS11_LOG_LEVEL:-"INFO"}
    export MS11_DATABASE_URL=${MS11_DATABASE_URL:-"sqlite:///data/ms11.db"}
    export MS11_REDIS_URL=${MS11_REDIS_URL:-"redis://localhost:6379/0"}
    
    log_success "Environment validation completed"
}

# Database initialization
initialize_database() {
    log_info "Initializing database..."
    
    # Wait for database connection
    if [[ "$MS11_DATABASE_URL" == postgres* ]]; then
        log_info "Waiting for PostgreSQL connection..."
        
        # Extract connection details from URL
        DB_HOST=$(echo $MS11_DATABASE_URL | sed -n 's/.*@\([^:]*\).*/\1/p')
        DB_PORT=$(echo $MS11_DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        
        if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
            max_attempts=30
            attempt=0
            
            while [ $attempt -lt $max_attempts ]; do
                if pg_isready -h "$DB_HOST" -p "$DB_PORT" -q; then
                    log_success "PostgreSQL is ready"
                    break
                fi
                
                attempt=$((attempt + 1))
                log_info "Waiting for PostgreSQL... ($attempt/$max_attempts)"
                sleep 2
            done
            
            if [ $attempt -eq $max_attempts ]; then
                log_error "PostgreSQL connection timeout"
                exit 1
            fi
        fi
    fi
    
    # Run database migrations
    if [ -d "migrations" ]; then
        log_info "Running database migrations..."
        python -c "
import asyncio
from core.advanced_database import AdvancedDatabaseManager
from core.configuration_manager import ConfigurationManager
import os

async def run_migrations():
    try:
        config_manager = ConfigurationManager()
        config = await config_manager.load_configuration()
        
        db_manager = AdvancedDatabaseManager(config.database)
        await db_manager.initialize()
        await db_manager.migration_manager.run_migrations()
        
        print('Database migrations completed successfully')
    except Exception as e:
        print(f'Migration error: {e}')
        exit(1)

asyncio.run(run_migrations())
" || log_warning "Migration script not available or failed"
    fi
    
    log_success "Database initialization completed"
}

# Redis connection check
check_redis() {
    if [[ "$MS11_REDIS_URL" != *"localhost"* ]] && [[ "$MS11_REDIS_URL" != *"127.0.0.1"* ]]; then
        log_info "Checking Redis connection..."
        
        max_attempts=15
        attempt=0
        
        while [ $attempt -lt $max_attempts ]; do
            if redis-cli -u "$MS11_REDIS_URL" ping > /dev/null 2>&1; then
                log_success "Redis is ready"
                break
            fi
            
            attempt=$((attempt + 1))
            log_info "Waiting for Redis... ($attempt/$max_attempts)"
            sleep 1
        done
        
        if [ $attempt -eq $max_attempts ]; then
            log_warning "Redis connection timeout, continuing without Redis"
        fi
    fi
}

# Configuration setup
setup_configuration() {
    log_info "Setting up configuration..."
    
    # Create configuration directory if it doesn't exist
    mkdir -p /app/config/runtime
    
    # Generate runtime configuration
    python -c "
import json
import os
from pathlib import Path

# Create runtime configuration
runtime_config = {
    'environment': os.getenv('MS11_ENVIRONMENT', 'production'),
    'log_level': os.getenv('MS11_LOG_LEVEL', 'INFO'),
    'database_url': os.getenv('MS11_DATABASE_URL', 'sqlite:///data/ms11.db'),
    'redis_url': os.getenv('MS11_REDIS_URL', 'redis://localhost:6379/0'),
    'secret_key': os.getenv('MS11_SECRET_KEY', 'change-me-in-production'),
    'instance_id': os.getenv('HOSTNAME', 'ms11-container'),
    'startup_time': '$(date -u +%Y-%m-%dT%H:%M:%SZ)'
}

# Write runtime configuration
with open('/app/config/runtime/container.json', 'w') as f:
    json.dump(runtime_config, f, indent=2)

print('Runtime configuration created')
" || log_warning "Failed to create runtime configuration"
    
    log_success "Configuration setup completed"
}

# System health checks
perform_health_checks() {
    log_info "Performing system health checks..."
    
    # Check Python modules
    python -c "
import sys
required_modules = ['asyncio', 'fastapi', 'asyncpg', 'redis', 'pydantic']

missing_modules = []
for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        missing_modules.append(module)

if missing_modules:
    print(f'Missing required modules: {missing_modules}')
    sys.exit(1)
else:
    print('All required modules are available')
"
    
    # Check file permissions
    if [ ! -w "/app/logs" ]; then
        log_warning "Logs directory is not writable"
    fi
    
    if [ ! -w "/app/data" ]; then
        log_warning "Data directory is not writable"
    fi
    
    log_success "Health checks completed"
}

# Cleanup function
cleanup() {
    log_info "Performing cleanup..."
    
    # Save any runtime state
    if [ -f "/app/data/runtime_state.json" ]; then
        cp /app/data/runtime_state.json /app/data/last_runtime_state.json
        log_info "Runtime state saved"
    fi
    
    # Kill background processes
    jobs -p | xargs -r kill
    
    log_info "Cleanup completed"
}

# Signal handlers
trap cleanup EXIT
trap 'log_info "Received SIGTERM, shutting down gracefully..."; cleanup; exit 0' TERM
trap 'log_info "Received SIGINT, shutting down gracefully..."; cleanup; exit 0' INT

# Main execution
main() {
    log_info "Starting MS11 Container (PID: $$)"
    log_info "Environment: $MS11_ENVIRONMENT"
    log_info "Command: $*"
    
    # Run initialization steps
    validate_environment
    setup_configuration
    initialize_database
    check_redis
    perform_health_checks
    
    log_success "Initialization completed successfully"
    
    # Start the application
    log_info "Starting MS11 application..."
    
    # Execute the main command
    exec "$@"
}

# Run main function if this script is executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi