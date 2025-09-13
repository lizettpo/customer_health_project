# Docker Deployment Guide (SQLite)

This guide explains how to deploy the Customer Health Score system using Docker with SQLite.

## Prerequisites

- Docker and Docker Compose installed
- At least 2GB RAM available (reduced from PostgreSQL setup)
- Ports 3000 and 8000 available

## Quick Start Options

### Option 1: Development (Recommended)
**Backend in Docker, Frontend locally for fast development**

1. **Start backend with SQLite**:
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

2. **Start frontend locally** (separate terminal):
   ```bash
   cd frontend
   npm start
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000 (hot reload enabled)
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Full Docker Stack
**Both frontend and backend in containers**

1. **Start all services**:
   ```bash
   docker-compose up -d
   ```

2. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

### Option 3: Production Deployment

1. **Deploy using production compose file**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Access the application**:
   - Frontend: http://localhost (port 80)
   - Backend API: http://localhost:8000

## Available Commands

### Development
```bash
# Start backend only (recommended)
docker-compose -f docker-compose.dev.yml up -d

# Start full stack
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build -d

# Run backend tests
docker-compose exec backend python run_tests.py
```

### Production
```bash
# Deploy production
docker-compose -f docker-compose.prod.yml up -d

# View production logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop production
docker-compose -f docker-compose.prod.yml down
```

### SQLite Database Management
```bash
# Connect to SQLite database
docker-compose exec backend sqlite3 /app/data/customer_health.db

# View tables
docker-compose exec backend sqlite3 /app/data/customer_health.db ".tables"

# Backup database (single file)
docker cp customer-health-api:/app/data/customer_health.db ./backup.db

# Restore database
docker cp ./backup.db customer-health-api:/app/data/customer_health.db
docker-compose restart backend

# Check database size
docker-compose exec backend du -h /app/data/customer_health.db
```

## Service Architecture

- **backend**: FastAPI application with embedded SQLite (port 8000)
- **frontend**: React application with Nginx (port 3000/80)

*Note: No separate database container needed with SQLite!*

## Environment Variables

### Backend
- `DATABASE_URL`: SQLite file path (automatically set to `sqlite:///./data/customer_health.db`)
- `ENVIRONMENT`: Set to 'production' for production builds

### Frontend
- `REACT_APP_API_BASE_URL`: Backend API URL

## Health Checks

All services include health checks:
- **Backend**: HTTP health endpoint check (`/health`)
- **Frontend**: Nginx status check

## Volumes

- `sqlite_data`: Persistent SQLite database storage

## Networking

- **Development**: Services communicate via default Docker network
- **Production**: Isolated `customer-health-network` for security

## Troubleshooting

### Services won't start
```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs [service_name]
```

### SQLite database issues
```bash
# Check database file exists
docker-compose exec backend ls -la /app/data/

# Verify connection string
docker-compose exec backend python -c "from database import engine; print(engine.url)"

# Check database integrity
docker-compose exec backend sqlite3 /app/data/customer_health.db "PRAGMA integrity_check;"
```

### Frontend can't reach backend
```bash
# Check network connectivity
docker-compose exec frontend ping backend

# Verify API URL
docker-compose exec frontend env | grep REACT_APP_API_BASE_URL
```

### Reset everything
```bash
# Stop and remove all containers and volumes
docker-compose down -v
docker system prune -f

# Rebuild and start fresh
docker-compose up --build -d
```

## Performance Optimization

### For Production:
- Use `docker-compose.prod.yml`
- Set resource limits in compose file
- Regular database backups (single SQLite file)
- Enable log rotation
- Use reverse proxy (nginx) for SSL termination
- Monitor SQLite database size and performance

### Resource Limits Example:
Add to services in docker-compose.yml:
```yaml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '0.5'
```