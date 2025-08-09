# MS11 Docker Deployment Guide

This guide covers deploying MS11 using Docker containers for development, testing, and production environments.

## Quick Start

### Production Deployment

```bash
# 1. Set environment variables
export DB_PASSWORD="your_secure_password"
export MS11_SECRET_KEY="your_secret_key_here"

# 2. Start the complete stack
docker-compose up -d

# 3. Check services
docker-compose ps
```

### Development Mode

```bash
# Start development environment
docker-compose --profile dev up -d

# Or start only development service
docker-compose up ms11-dev
```

### Testing

```bash
# Run tests
docker-compose --profile test run --rm ms11-test
```

## Architecture

The MS11 Docker deployment consists of:

- **ms11-app**: Main application (production)
- **postgres**: PostgreSQL database with extensions
- **redis**: Redis cache for rate limiting and sessions
- **xvfb**: X Virtual Framebuffer for GUI automation
- **ms11-dev**: Development environment (optional)
- **ms11-test**: Testing environment (optional)

## Configuration

### Environment Variables

#### Required for Production
- `DB_PASSWORD`: PostgreSQL password
- `MS11_SECRET_KEY`: Application secret key

#### Optional Configuration
- `MS11_PORT`: Application port (default: 5000)
- `MS11_DASHBOARD_PORT`: Dashboard port (default: 8080)
- `MS11_LOG_LEVEL`: Logging level (default: INFO)
- `POSTGRES_PORT`: PostgreSQL port (default: 5432)
- `REDIS_PORT`: Redis port (default: 6379)

### Docker Build Targets

The Dockerfile provides multiple build targets:

1. **base**: Common dependencies
2. **development**: Full development environment
3. **production**: Optimized for production
4. **testing**: Configured for running tests

## Deployment Scenarios

### 1. Local Development

```bash
# Start development stack
docker-compose --profile dev up

# Access application
open http://localhost:5001

# View logs
docker-compose logs -f ms11-dev
```

### 2. Production Deployment

```bash
# Create .env file
cat > .env << EOF
DB_PASSWORD=your_secure_password_here
MS11_SECRET_KEY=your_32_character_secret_key_here
MS11_LOG_LEVEL=INFO
EOF

# Deploy production stack
docker-compose up -d

# Check health
docker-compose exec ms11-app ./scripts/healthcheck.sh --detailed
```

### 3. Staging Environment

```bash
# Override default configuration
export MS11_ENVIRONMENT=staging
export MS11_LOG_LEVEL=DEBUG

docker-compose up -d
```

## Management Commands

### Database Management

```bash
# Run database migrations
docker-compose exec ms11-app python -c "
import asyncio
from core.advanced_database import AdvancedDatabaseManager
from core.configuration_manager import ConfigurationManager

async def migrate():
    config_manager = ConfigurationManager()
    config = await config_manager.load_configuration()
    db = AdvancedDatabaseManager(config.database)
    await db.initialize()
    await db.migration_manager.run_migrations()

asyncio.run(migrate())
"

# Database backup
docker-compose exec postgres pg_dump -U ms11 ms11 > backup.sql

# Restore database
docker-compose exec -T postgres psql -U ms11 ms11 < backup.sql
```

### Application Management

```bash
# View application logs
docker-compose logs -f ms11-app

# Access application shell
docker-compose exec ms11-app bash

# Run health check
docker-compose exec ms11-app ./scripts/healthcheck.sh

# Restart application
docker-compose restart ms11-app
```

### Monitoring

```bash
# View all service status
docker-compose ps

# Check resource usage
docker stats

# View detailed health status
docker-compose exec ms11-app ./scripts/healthcheck.sh --detailed
```

## Persistent Data

The following directories are mounted as volumes:

- `./data`: Application data and SQLite fallback
- `./logs`: Application logs
- `./backups`: Database and application backups
- `postgres_data`: PostgreSQL data (Docker volume)
- `redis_data`: Redis persistence (Docker volume)

## Scaling

### Horizontal Scaling

```bash
# Scale application instances
docker-compose up -d --scale ms11-app=3

# Use with load balancer
# (Nginx, Traefik, or cloud load balancer)
```

### Vertical Scaling

```yaml
# In docker-compose.override.yml
version: '3.8'
services:
  ms11-app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

## Security Considerations

### Production Security Checklist

- [ ] Set strong `DB_PASSWORD`
- [ ] Set unique `MS11_SECRET_KEY`
- [ ] Use HTTPS proxy (Nginx, Traefik)
- [ ] Enable firewall rules
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity
- [ ] Backup encryption
- [ ] Network segmentation

### Container Security

```bash
# Scan for vulnerabilities
docker scout cves ms11-app

# Update base images regularly
docker-compose pull
docker-compose up -d
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check PostgreSQL status
   docker-compose exec postgres pg_isready -U ms11
   
   # View PostgreSQL logs
   docker-compose logs postgres
   ```

2. **Memory Issues**
   ```bash
   # Check memory usage
   docker stats
   
   # Increase Redis memory limit
   docker-compose exec redis redis-cli config set maxmemory 512mb
   ```

3. **Permission Issues**
   ```bash
   # Fix volume permissions
   sudo chown -R 1000:1000 ./data ./logs ./backups
   ```

4. **Network Issues**
   ```bash
   # Check network connectivity
   docker-compose exec ms11-app ping postgres
   docker-compose exec ms11-app ping redis
   ```

### Debug Mode

```bash
# Start with debug logging
MS11_LOG_LEVEL=DEBUG docker-compose up

# Access debug information
docker-compose exec ms11-app python -c "
from core.performance_dashboard import PerformanceDashboard
dashboard = PerformanceDashboard()
print(dashboard.get_system_status())
"
```

### Health Monitoring

```bash
# Continuous health monitoring
watch -n 30 'docker-compose exec ms11-app ./scripts/healthcheck.sh --detailed'

# Set up automated alerts
docker-compose exec ms11-app ./scripts/healthcheck.sh || echo "ALERT: MS11 unhealthy"
```

## Backup and Recovery

### Automated Backups

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
docker-compose exec postgres pg_dump -U ms11 ms11 | gzip > "backups/db_backup_$DATE.sql.gz"

# Application data backup
tar -czf "backups/app_data_$DATE.tar.gz" data/ logs/ config/

# Clean old backups (keep last 7 days)
find backups/ -name "*.gz" -mtime +7 -delete
EOF

chmod +x backup.sh
```

### Recovery Process

```bash
# Stop services
docker-compose down

# Restore database
gunzip -c backups/db_backup_YYYYMMDD_HHMMSS.sql.gz | \
  docker-compose exec -T postgres psql -U ms11 ms11

# Restore application data
tar -xzf backups/app_data_YYYYMMDD_HHMMSS.tar.gz

# Restart services
docker-compose up -d
```

## Performance Optimization

### Production Optimizations

```yaml
# docker-compose.override.yml
version: '3.8'
services:
  ms11-app:
    environment:
      - MS11_WORKERS=4  # CPU cores
      - MS11_MAX_CONNECTIONS=100
    deploy:
      replicas: 2
      
  postgres:
    command: postgres -c shared_preload_libraries=pg_stat_statements -c max_connections=200
    
  redis:
    command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru --save 60 1000
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy MS11
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        run: |
          docker-compose pull
          docker-compose up -d
          docker-compose exec ms11-app ./scripts/healthcheck.sh
```

This deployment guide ensures MS11 can be deployed reliably across different environments with proper monitoring, security, and maintenance procedures.