#!/bin/bash
# MS11 Docker Health Check Script
# Comprehensive health monitoring for containerized MS11

set -e

# Health check configuration
TIMEOUT=${HEALTHCHECK_TIMEOUT:-10}
MAX_CHECKS=5
CURRENT_CHECKS=0

# Health check functions
check_python_process() {
    if pgrep -f "python.*src/main.py" > /dev/null; then
        return 0
    else
        return 1
    fi
}

check_database_connection() {
    # Get database URL from environment or config
    DB_URL=${MS11_DATABASE_URL:-"sqlite:///data/ms11.db"}
    
    if [[ "$DB_URL" == sqlite* ]]; then
        # SQLite health check
        if [ -f "/app/data/ms11.db" ]; then
            # Try to query the database
            python -c "
import sqlite3
try:
    conn = sqlite3.connect('/app/data/ms11.db', timeout=5)
    cursor = conn.cursor()
    cursor.execute('SELECT 1')
    conn.close()
    exit(0)
except Exception:
    exit(1)
" 2>/dev/null
            return $?
        else
            # Database file doesn't exist yet, may be starting up
            return 0
        fi
    elif [[ "$DB_URL" == postgres* ]]; then
        # PostgreSQL health check
        python -c "
import os
import asyncio
import asyncpg
from urllib.parse import urlparse

async def check_postgres():
    try:
        url = os.getenv('MS11_DATABASE_URL')
        if not url:
            return False
            
        parsed = urlparse(url)
        conn = await asyncpg.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip('/'),
            command_timeout=5
        )
        
        await conn.execute('SELECT 1')
        await conn.close()
        return True
    except Exception:
        return False

result = asyncio.run(check_postgres())
exit(0 if result else 1)
" 2>/dev/null
        return $?
    fi
    
    return 0
}

check_redis_connection() {
    REDIS_URL=${MS11_REDIS_URL:-"redis://localhost:6379/0"}
    
    # Skip Redis check if using localhost (optional dependency)
    if [[ "$REDIS_URL" == *"localhost"* ]] || [[ "$REDIS_URL" == *"127.0.0.1"* ]]; then
        return 0
    fi
    
    # Check Redis connection
    if command -v redis-cli >/dev/null 2>&1; then
        redis-cli -u "$REDIS_URL" ping > /dev/null 2>&1
        return $?
    fi
    
    return 0
}

check_web_interface() {
    # Check if web interface is responding
    if command -v curl >/dev/null 2>&1; then
        curl -f -s -m 5 http://localhost:5000/health > /dev/null 2>&1
        return $?
    fi
    
    # Fallback: check if port is open
    python -c "
import socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('localhost', 5000))
    sock.close()
    exit(0 if result == 0 else 1)
except Exception:
    exit(1)
" 2>/dev/null
    return $?
}

check_filesystem_health() {
    # Check if critical directories are writable
    for dir in "/app/logs" "/app/data" "/app/backups"; do
        if [ -d "$dir" ] && [ ! -w "$dir" ]; then
            return 1
        fi
    done
    
    # Check disk space (fail if < 100MB available)
    available_space=$(df /app | awk 'NR==2 {print $4}')
    if [ "$available_space" -lt 100000 ]; then
        return 1
    fi
    
    return 0
}

check_memory_usage() {
    # Check if memory usage is reasonable
    python -c "
import psutil
import os

try:
    # Get memory usage of the current process tree
    current_pid = os.getpid()
    process = psutil.Process(current_pid)
    
    # Find Python processes
    python_procs = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        if 'python' in proc.info['name'].lower():
            python_procs.append(proc.info['memory_percent'])
    
    total_memory_percent = sum(python_procs)
    
    # Fail if using more than 80% of system memory
    if total_memory_percent > 80:
        exit(1)
    else:
        exit(0)
except Exception:
    exit(0)  # Don't fail health check if can't check memory
" 2>/dev/null
    return $?
}

check_application_health() {
    # Check if the application is responding correctly
    python -c "
import sys
import os
sys.path.append('/app')

try:
    # Try to import core modules
    from core.structured_logging import StructuredLogger
    from core.configuration_manager import ConfigurationManager
    
    # Basic functionality check
    logger = StructuredLogger('healthcheck')
    config_manager = ConfigurationManager()
    
    # If we get here, basic imports work
    exit(0)
except Exception as e:
    print(f'Application health check failed: {e}', file=sys.stderr)
    exit(1)
" 2>/dev/null
    return $?
}

# Main health check routine
perform_health_check() {
    local check_name="$1"
    local check_function="$2"
    
    if $check_function; then
        echo "✓ $check_name: OK"
        return 0
    else
        echo "✗ $check_name: FAILED"
        return 1
    fi
}

# Comprehensive health check
main_health_check() {
    echo "MS11 Health Check - $(date)"
    echo "================================"
    
    local failed_checks=0
    
    # Core checks (failure of these fails the health check)
    if ! perform_health_check "Python Process" check_python_process; then
        ((failed_checks++))
    fi
    
    if ! perform_health_check "Database Connection" check_database_connection; then
        ((failed_checks++))
    fi
    
    if ! perform_health_check "Application Health" check_application_health; then
        ((failed_checks++))
    fi
    
    # Secondary checks (warnings but don't fail health check)
    if ! perform_health_check "Filesystem Health" check_filesystem_health; then
        echo "  Warning: Filesystem issues detected"
    fi
    
    if ! perform_health_check "Memory Usage" check_memory_usage; then
        echo "  Warning: High memory usage detected"
    fi
    
    # Optional checks
    perform_health_check "Redis Connection" check_redis_connection || echo "  Info: Redis check skipped or failed"
    perform_health_check "Web Interface" check_web_interface || echo "  Info: Web interface check failed"
    
    echo "================================"
    
    if [ $failed_checks -eq 0 ]; then
        echo "Overall Status: HEALTHY"
        return 0
    else
        echo "Overall Status: UNHEALTHY ($failed_checks critical checks failed)"
        return 1
    fi
}

# Quick health check (for frequent Docker health checks)
quick_health_check() {
    # Just check if the main process is running and responding
    if check_python_process && check_application_health; then
        return 0
    else
        return 1
    fi
}

# Main execution
if [ "${1}" = "--detailed" ] || [ "${1}" = "-d" ]; then
    main_health_check
elif [ "${1}" = "--quick" ] || [ "${1}" = "-q" ]; then
    quick_health_check
else
    # Default to quick check for Docker health checks
    quick_health_check
fi