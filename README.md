# Customer Health Scoring System

A comprehensive customer health monitoring and scoring platform built with FastAPI and React, featuring real-time health analytics and configurable scoring algorithms.

## 🚀 Quick Start

### Access URLs
- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **API Info**: http://localhost:8000/ (Basic API information)

### Prerequisites
- Docker and Docker Compose
- Git

### 🐳 Docker Setup (Recommended)

#### Option 1: Production Build (Full Stack)
```bash
# Clone the repository
git clone <repository-url>
cd customer_health_project

# Build and run all services
docker-compose up -d --build

# View logs
docker-compose logs -f
```

#### Option 2: Development Mode (Faster Iteration)
```bash
# Run development version with hot reload
docker-compose -f docker-compose.dev-all.yml up -d --build

# View logs
docker-compose -f docker-compose.dev-all.yml logs -f
```

#### Option 3: Backend Only
```bash
# Run only the backend API
docker-compose -f docker-compose.dev.yml up -d --build
```

### 💻 Local Development Setup

#### Backend Setup
```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run the server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend

# Install Node.js dependencies
npm install

# Start development server
npm start
```

#### Running Tests
```bash
# Backend tests
cd backend
python run_tests.py

# Frontend tests
cd frontend
npm test
```

## 📊 Features

### Core Functionality
- **Real-time Health Scoring**: Dynamic customer health calculation based on multiple factors
- **Interactive Dashboard**: Visual overview of customer health metrics and trends
- **Event Tracking**: Record and analyze customer activities (API usage, logins, payments, etc.)
- **Configurable Factors**: Modular health scoring system with pluggable factors
- **Customer Segmentation**: Different scoring expectations based on customer tiers

### Health Factors
- **API Usage Factor**: Monitors API call frequency and patterns
- **Login Frequency Factor**: Tracks user engagement and activity levels
- **Payment Timeliness Factor**: Analyzes payment behavior and history
- **Feature Adoption Factor**: Measures feature usage and adoption rates
- **Support Tickets Factor**: Evaluates support interaction patterns

### Customer Segments
- **Enterprise**: 1000+ expected API calls/month
- **SMB**: 500+ expected API calls/month
- **Startup**: 200+ expected API calls/month

## 🔧 Configuration

### Database Configuration
The system uses SQLite for data persistence:
- Database file: `data/customer_health.db`
- Auto-creates tables on startup
- Sample data populated automatically
- Persistent storage via Docker volumes

### Environment Variables
```bash
# Backend Configuration
DATABASE_URL=sqlite:///./data/customer_health.db
ENVIRONMENT=production

# Frontend Configuration
REACT_APP_API_BASE_URL=http://localhost:8000
```

## 📚 Usage Examples

### Recording Customer Events
```javascript
// Via Frontend Form
- Navigate to http://localhost:3000
- Select customer and event type
- Fill required fields and submit

// Via API
POST /api/customers/{customer_id}/events
{
  "event_type": "api_call",
  "event_data": {
    "endpoint": "/api/users",
    "response_time": 250,
    "status_code": 200
  }
}
```

### Viewing Health Scores
```javascript
// Get customer list with health scores
GET /api/customers

// Get detailed health breakdown
GET /api/customers/{customer_id}/health

// Get dashboard statistics
GET /api/dashboard/stats
```

## 🛠️ Development

### Project Structure
```
customer_health_project/
├── backend/                 # FastAPI backend
│   ├── domain/             # Business logic layer
│   │   ├── models.py       # Domain entities
│   │   ├── calculators.py  # Health score algorithms
│   │   └── health_factors/ # Pluggable scoring factors
│   ├── services/           # Application services
│   ├── data/              # Data access layer
│   └── tests/             # Test suites
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API service layer
│   │   ├── hooks/         # Custom React hooks
│   │   └── types/         # TypeScript definitions
├── docs/                  # Documentation
├── screenshots/           # Application screenshots
└── docker-compose*.yml    # Docker configurations
```

### Adding New Health Factors
1. Create a new class inheriting from `BaseHealthFactor`
2. Implement the `calculate_score()` method
3. Register in the health calculator
4. Add corresponding frontend form fields

### Testing
- **Backend**: 116 unit tests + 16 integration tests
- **Minimum Coverage**: 85%
- **Test Command**: `python run_tests.py`

## 🚢 Deployment

### Docker Production Deployment
```bash
# Build optimized production images
docker-compose up -d --build

# Scale services if needed
docker-compose up -d --scale backend=2 --scale frontend=2

# Monitor services
docker-compose ps
docker-compose logs -f
```

### Health Monitoring
- Health check endpoint: `/health`
- Docker health checks configured
- Auto-restart on failure

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   netstat -tulpn | grep :8000

   # Kill the process or use different ports
   docker-compose down
   ```

2. **Database Connection Issues**
   ```bash
   # Check SQLite file permissions
   ls -la backend/data/

   # Recreate volume if needed
   docker-compose down -v
   docker-compose up -d --build
   ```

3. **Frontend Build Fails**
   ```bash
   # Clear npm cache
   cd frontend
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Slow Docker Performance**
   - Use development compose file for faster iteration
   - Ensure Docker has sufficient resources allocated
   - Use `--build` flag only when necessary

### Performance Optimization
- Docker layer caching enabled
- Nginx compression configured
- Resource limits set for containers
- Static asset caching optimized

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📞 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the API documentation at http://localhost:8000/docs
3. Check existing GitHub issues
4. Create a new issue with detailed information