# Multi-Agent SBDR System - Docker Deployment Guide

This guide provides comprehensive instructions for deploying the Multi-Agent SBDR System using Docker and Docker Compose.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Deployment Options](#deployment-options)
- [Management Scripts](#management-scripts)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

## 🔧 Prerequisites

### System Requirements

- **Docker**: Version 20.10.0 or higher
- **Docker Compose**: Version 2.0.0 or higher
- **Memory**: Minimum 2GB RAM available for containers
- **Storage**: At least 5GB free disk space
- **OS**: Linux, macOS, or Windows with WSL2

### Installation

#### Docker Installation

**Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**macOS:**
```bash
# Using Homebrew
brew install --cask docker
# Or download Docker Desktop from docker.com
```

**Windows:**
Download and install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)

#### Docker Compose Installation

Docker Compose is included with Docker Desktop. For Linux:
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Verification

```bash
docker --version
docker-compose --version
docker info
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# If you don't have the project yet
git clone <repository-url>
cd SigmAgent

# Copy environment configuration
cp .env.example .env
```

### 2. Configure Environment

Edit the `.env` file with your settings:

```bash
# Required: OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Optional: External Integrations
CRISP_IDENTIFIER=your_crisp_identifier
CRISP_KEY=your_crisp_api_key
SHOPIFY_SHOP_DOMAIN=your-shop-name
SHOPIFY_ACCESS_TOKEN=your_shopify_access_token
```

### 3. Build and Run

Using management scripts (recommended):
```bash
# Build the system
./scripts/build.sh

# Start the system
./scripts/run.sh -d
```

Or using Docker Compose directly:
```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f
```

### 4. Access the System

- **Main System**: http://localhost:8000
- **Web Interface**: http://localhost:8080
- **Monitoring Dashboard**: http://localhost:3000 (admin/admin123)
- **Prometheus Metrics**: http://localhost:9090

## ⚙️ Configuration

### Environment Variables

The system uses environment variables for configuration. Key variables include:

#### Required Configuration

```env
# OpenAI Integration (Required)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

#### Optional Integrations

```env
# Crisp Chat Integration
CRISP_IDENTIFIER=your_crisp_identifier
CRISP_KEY=your_crisp_api_key
CRISP_WEBSITE_ID=your_crisp_website_id

# Shopify E-commerce Integration  
SHOPIFY_SHOP_DOMAIN=your-shop-name
SHOPIFY_ACCESS_TOKEN=your_shopify_access_token

# Database Configuration
DATABASE_URL=postgresql://sbdr_user:sbdr_pass@postgres:5432/sbdr_db
REDIS_URL=redis://redis:6379/0
```

#### System Settings

```env
# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO

# Performance
MAX_CONCURRENT_SESSIONS=100
SESSION_TIMEOUT=1800
REQUEST_TIMEOUT=30
```

### Knowledge Base Configuration

The system uses `knowledge_base.json` for FAQ responses, policies, and qualification questions. Mount your custom knowledge base:

```yaml
volumes:
  - ./your_knowledge_base.json:/app/knowledge_base.json
```

### Custom Volumes

```yaml
volumes:
  - ./logs:/app/logs              # Application logs
  - ./data:/app/data              # Application data
  - ./custom_config:/app/config   # Custom configuration
```

## 🏭 Deployment Options

### Development Mode

For development with hot-reloading and debugging:

```bash
# Start in development mode
./scripts/run.sh --env development

# Or with docker-compose
docker-compose -f docker-compose.yml -f docker-compose.development.yml up
```

### Production Mode

For production deployment with optimizations:

```bash
# Build for production
./scripts/build.sh --env production --push

# Start in production mode
./scripts/run.sh --env production -d
```

### Minimal Setup

To run only the core system without monitoring:

```bash
# Start only essential services
./scripts/run.sh --services sbdr-system,postgres,redis -d
```

### Custom Service Selection

```bash
# Start specific services
docker-compose up -d sbdr-system postgres redis

# Scale services
docker-compose up -d --scale sbdr-system=2
```

## 🛠️ Management Scripts

### Build Script (`scripts/build.sh`)

```bash
# Basic build
./scripts/build.sh

# Build with options
./scripts/build.sh --env production --push --no-cache

# Options:
# -e, --env ENVIRONMENT     Build environment (development, staging, production)
# -p, --push                Push images to registry after build
# -n, --no-cache            Build without using cache
# -v, --verbose             Enable verbose output
# -h, --help                Show help message
```

### Run Script (`scripts/run.sh`)

```bash
# Start system
./scripts/run.sh

# Start with options
./scripts/run.sh --detach --rebuild --follow-logs

# Available commands:
./scripts/run.sh start           # Start system (default)
./scripts/run.sh stop            # Stop system  
./scripts/run.sh restart         # Restart system
./scripts/run.sh status          # Show status
./scripts/run.sh logs            # Show logs
./scripts/run.sh shell           # Open shell
./scripts/run.sh test            # Run tests

# Options:
# -e, --env ENVIRONMENT     Environment to run
# -d, --detach              Run in background
# -r, --rebuild             Rebuild images before starting
# -s, --services SERVICES   Run specific services only
# -f, --follow-logs         Follow logs output
```

### Docker Compose Commands

```bash
# View service status
docker-compose ps

# View logs
docker-compose logs -f sbdr-system

# Scale services
docker-compose up -d --scale sbdr-system=3

# Update single service
docker-compose up -d --no-deps sbdr-system

# Execute commands in container
docker-compose exec sbdr-system python multiagent_test_framework.py

# Stop and remove containers
docker-compose down

# Stop and remove everything including volumes
docker-compose down -v
```

## 📊 Monitoring and Maintenance

### Health Checks

The system includes built-in health checks:

```bash
# Check container health
docker-compose ps

# View health check logs
docker inspect --format='{{json .State.Health}}' sbdr-multiagent
```

### Monitoring Stack

The deployment includes a complete monitoring stack:

#### Prometheus Metrics
- URL: http://localhost:9090
- Collects system and application metrics
- Custom SBDR metrics available

#### Grafana Dashboard
- URL: http://localhost:3000
- Username: admin
- Password: admin123
- Pre-configured dashboards for system metrics

### Log Management

```bash
# View real-time logs
./scripts/run.sh logs -f

# View specific service logs
docker-compose logs -f sbdr-system

# Export logs
docker-compose logs --no-color > system_logs.txt

# Log rotation (for production)
# Logs are automatically rotated by Docker logging driver
```

### Database Management

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U sbdr_user -d sbdr_db

# Backup database
docker-compose exec postgres pg_dump -U sbdr_user sbdr_db > backup.sql

# Restore database
docker-compose exec -T postgres psql -U sbdr_user -d sbdr_db < backup.sql

# Access Redis
docker-compose exec redis redis-cli
```

### Performance Monitoring

```bash
# View resource usage
docker stats

# View container metrics
docker-compose exec sbdr-system python -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'Memory: {psutil.virtual_memory().percent}%')
print(f'Disk: {psutil.disk_usage(\"/\").percent}%')
"
```

## 🔧 Troubleshooting

### Common Issues

#### Container Won't Start

```bash
# Check container logs
docker-compose logs sbdr-system

# Check system resources
docker system df
docker system prune

# Rebuild containers
docker-compose down
docker-compose up --build -d
```

#### Permission Issues

```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x scripts/*.sh

# Fix Docker permissions (Linux)
sudo usermod -aG docker $USER
newgrp docker
```

#### Port Conflicts

```bash
# Check what's using ports
netstat -tulpn | grep :8000
lsof -i :8000

# Change ports in docker-compose.yml or .env
WEB_PORT=8001
POSTGRES_PORT=5433
```

#### Memory Issues

```bash
# Check container memory usage
docker stats --no-stream

# Increase Docker memory limit (Docker Desktop)
# Settings > Resources > Advanced > Memory

# Add memory limits to docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G
```

### Debugging

#### Enable Debug Mode

```bash
# Set debug environment variables
export DEBUG=true
export LOG_LEVEL=DEBUG

# Restart with debug settings
./scripts/run.sh restart
```

#### Access Container Shell

```bash
# Open shell in main container
./scripts/run.sh shell

# Or directly with docker-compose
docker-compose exec sbdr-system /bin/bash

# Run diagnostic commands
python -c "from multiagent_sbdr_system import AgentOrchestrator; print('System OK')"
```

#### Network Issues

```bash
# Check container networking
docker network ls
docker network inspect sbdr-multiagent_sbdr-network

# Test connectivity between containers
docker-compose exec sbdr-system ping postgres
docker-compose exec sbdr-system nslookup redis
```

### Log Analysis

```bash
# Search logs for errors
docker-compose logs | grep -i error

# Filter logs by service
docker-compose logs sbdr-system | grep -i "qualification"

# Export structured logs
docker-compose logs --json > logs.json
```

## 🏢 Production Deployment

### Security Considerations

#### Environment Security

```bash
# Use Docker secrets for sensitive data
echo "your_api_key" | docker secret create openai_api_key -

# Update docker-compose.yml to use secrets
secrets:
  - openai_api_key
```

#### Network Security

```yaml
# Use custom networks with restricted access
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access
```

#### Container Security

```dockerfile
# Use non-root user (already implemented)
USER sbdr

# Use read-only filesystem where possible
read_only: true
tmpfs:
  - /tmp
  - /var/run
```

### Performance Optimization

#### Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '1.0'
      memory: 1G
```

#### Scaling

```bash
# Horizontal scaling
docker-compose up -d --scale sbdr-system=3

# Load balancer configuration (nginx example)
upstream sbdr_backend {
    server sbdr-system:8000;
    server sbdr-system:8000;
    server sbdr-system:8000;
}
```

### High Availability

#### Database Backup

```bash
#!/bin/bash
# Automated backup script
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U sbdr_user sbdr_db | gzip > "backup_${DATE}.sql.gz"

# Keep only last 30 days
find . -name "backup_*.sql.gz" -mtime +30 -delete
```

#### Health Monitoring

```yaml
# Enhanced health checks
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

### Deployment Automation

#### CI/CD Integration

```yaml
# Example GitHub Actions
name: Deploy SBDR System
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and Deploy
        run: |
          ./scripts/build.sh --env production
          ./scripts/run.sh --detach
```

#### Rolling Updates

```bash
#!/bin/bash
# Rolling update script
docker-compose pull
docker-compose up -d --no-deps --scale sbdr-system=2 sbdr-system
sleep 30
docker-compose up -d --no-deps --remove-orphans
```

## 📚 Additional Resources

### Documentation

- [Multi-Agent System Architecture](MULTIAGENT_README.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Configuration Reference](.env.example)

### Monitoring

- [Prometheus Configuration](docker/prometheus.yml)
- [Grafana Dashboards](docker/grafana/dashboards/)
- [Database Schema](docker/init.sql)

### Support

- System logs: `./scripts/run.sh logs`
- Health check: `./scripts/run.sh status`
- Shell access: `./scripts/run.sh shell`
- Test system: `./scripts/run.sh test`

## 🎯 Next Steps

After successful deployment:

1. **Configure Integrations**: Set up Crisp, Shopify, and OpenAI integrations
2. **Customize Knowledge Base**: Update `knowledge_base.json` with your content
3. **Monitor Performance**: Use Grafana dashboards to monitor system health
4. **Scale as Needed**: Adjust container resources and scaling based on usage
5. **Set Up Backups**: Implement automated backup procedures for production

---

For additional support or questions about Docker deployment, please refer to the main [MULTIAGENT_README.md](MULTIAGENT_README.md) or check the troubleshooting section above.