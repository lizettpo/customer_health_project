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

##### Backend Testing (Python/Pytest)

```bash
# Quick test run using custom script
cd backend
python run_tests.py

# Standard pytest command
cd backend
pytest

# Run with verbose output
pytest -v

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest -m unit              # Tests marked as 'unit'
pytest -m integration       # Tests marked as 'integration'

# Run specific test files
pytest tests/unit/test_customer_service.py
pytest tests/integration/test_api_endpoints.py

# Run with coverage report
pytest --cov=. --cov-report=html
pytest --cov=. --cov-report=term-missing

# Run tests and fail if coverage below 85%
pytest --cov-fail-under=85

# Run in Docker container
docker-compose -f docker-compose.dev.yml exec backend python run_tests.py
```

##### Frontend Testing (React/Jest)

```bash
# Run all tests
cd frontend
npm test

# Run tests in watch mode (default)
npm test

# Run tests once (no watch mode)
npm test -- --watchAll=false

# Run tests with coverage
npm test -- --coverage --watchAll=false

# Run specific test files
npm test -- --testPathPattern=src/components/Dashboard

# Update snapshots
npm test -- --updateSnapshot
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
GET / api / customers;

// Get detailed health breakdown
GET / api / customers / { customer_id } / health;

// Get dashboard statistics
GET / api / dashboard / stats;
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

### Testing Framework

- **Backend**: 116 unit tests + 16 integration tests using Pytest
- **Frontend**: Jest + React Testing Library (setup ready)
- **Minimum Coverage**: 85% required
- **Test Command**: `python run_tests.py` (backend), `npm test` (frontend)

---

## 🧪 Testing

### Test Structure

#### Backend Tests (`backend/tests/`)

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── unit/                    # Unit tests (116 tests)
│   ├── test_customer_service.py
│   ├── test_health_score_calculator.py
│   ├── test_api_usage_factor.py
│   ├── test_login_frequency_factor.py
│   ├── test_payment_timeliness_factor.py
│   ├── test_feature_adoption_factor.py
│   ├── test_support_tickets_factor.py
│   ├── test_customer_controller.py
│   ├── test_health_score_controller.py
│   └── test_health_score_service.py
└── integration/             # Integration tests (16 tests)
    └── test_api_endpoints.py
```

### Running Backend Tests

#### Quick Testing

```bash
# Recommended: Use custom test runner
cd backend
python run_tests.py
```

#### Pytest Commands

```bash
cd backend

# Run all tests
pytest

# Verbose output with test names
pytest -v

# Run specific test categories
pytest tests/unit/                    # Unit tests only (116 tests)
pytest tests/integration/             # Integration tests only (16 tests)
pytest -m unit                        # Tests marked as 'unit'
pytest -m integration                 # Tests marked as 'integration'
pytest -m slow                        # Slow-running tests

# Run specific test files
pytest tests/unit/test_customer_service.py
pytest tests/unit/test_health_score_calculator.py
pytest tests/integration/test_api_endpoints.py

# Run specific test methods
pytest tests/unit/test_customer_service.py::TestCustomerService::test_create_customer
pytest -k "test_login_frequency"      # Run tests matching pattern
pytest -k "not slow"                  # Skip slow tests
```

#### Coverage Testing

```bash
cd backend

# Generate coverage report (HTML + terminal)
pytest --cov=. --cov-report=html --cov-report=term-missing

# Coverage with minimum threshold (85%)
pytest --cov=. --cov-fail-under=85

# Coverage for specific modules
pytest --cov=domain --cov=services --cov-report=term-missing

# View HTML coverage report
# Opens: backend/htmlcov/index.html
```

#### Docker Testing

```bash
# Test in Docker environment
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml exec backend python run_tests.py

# Run specific tests in Docker
docker-compose -f docker-compose.dev.yml exec backend pytest tests/unit/
docker-compose -f docker-compose.dev.yml exec backend pytest -v
```

### Running Frontend Tests

#### Basic Jest Testing

```bash
cd frontend

# Run all tests (watch mode by default)
npm test

# Run tests once (CI mode)
npm test -- --watchAll=false

# Run tests with coverage
npm test -- --coverage --watchAll=false

# Verbose output
npm test -- --verbose --watchAll=false
```

#### Advanced Frontend Testing

```bash
cd frontend

# Test specific patterns
npm test -- --testPathPattern=src/components
npm test -- --testPathPattern=Dashboard
npm test -- --testNamePattern="should render"

# Update snapshots
npm test -- --updateSnapshot

# Debug mode
npm test -- --detectOpenHandles --forceExit

# Silent mode (less output)
npm test -- --silent --watchAll=false
```

### Test Configuration

#### Backend Configuration (`backend/pytest.ini`)

```ini
[tool:pytest]
minversion = 7.0
addopts =
    --strict-markers
    --strict-config
    --verbose
    --cov=.
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
    --cov-fail-under=85
    --tb=short
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
```

#### Frontend Configuration (`frontend/package.json`)

```json
{
  "scripts": {
    "test": "react-scripts test"
  }
}
```

### Test Types and Coverage

#### Unit Tests (116 tests)

- **Domain Logic**: Health score calculations, business rules
- **Health Factors**: All 5 health factors individually tested
- **Services**: Customer service, health score service
- **Controllers**: Application controllers and workflows
- **Models**: Domain models and validation

#### Integration Tests (16 tests)

- **API Endpoints**: Full HTTP request/response testing
- **Database Operations**: End-to-end data persistence
- **Health Score Workflows**: Complete calculation pipelines
- **Event Processing**: Customer event recording and processing

#### Test Coverage Requirements

- **Minimum Coverage**: 85% across all modules
- **Current Coverage**: ~90%+ (exceeds requirement)
- **Coverage Reports**: Generated in `backend/htmlcov/`

### Continuous Integration

#### GitHub Actions (Example)

```yaml
name: Tests
on: [push, pull_request]
jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          python run_tests.py

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "18"
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage --watchAll=false
```

### Test Data and Fixtures

#### Backend Test Fixtures (`tests/conftest.py`)

- **Database Setup**: In-memory SQLite for tests
- **Sample Customers**: Test customer data
- **Mock Events**: Customer events for testing
- **Isolated Environment**: Each test runs in clean state

#### Test Database

```bash
# Test database is automatically created/destroyed
# Location: backend/test_customer_health.db (temporary)
# No manual setup required
```

### Debugging Tests

#### Backend Test Debugging

```bash
cd backend

# Run with Python debugger
pytest -s --pdb tests/unit/test_customer_service.py

# Print output (disable capture)
pytest -s tests/unit/test_customer_service.py

# Stop at first failure
pytest -x tests/

# Show local variables on failure
pytest -l tests/
```

#### Frontend Test Debugging

```bash
cd frontend

# Debug mode with more information
npm test -- --verbose --no-cache --watchAll=false

# Run with debugger statements
npm test -- --runInBand --no-cache --watchAll=false
```

### Test Performance

#### Parallel Testing

```bash
# Backend: Run tests in parallel (faster)
cd backend
pytest -n auto  # Requires pytest-xdist

# Frontend: Parallel by default
cd frontend
npm test -- --watchAll=false  # Uses available CPU cores
```

#### Fast Test Runs

```bash
# Backend: Skip slow tests
cd backend
pytest -m "not slow" --cov=.

# Frontend: Only changed files
cd frontend
npm test -- --onlyChanged --watchAll=false
```

### Adding New Tests

#### Backend Test Example

```python
# tests/unit/test_new_feature.py
import pytest
from domain.models import Customer

class TestNewFeature:
    def test_new_functionality(self, sample_customer):
        # Test implementation
        assert sample_customer.name is not None

    @pytest.mark.slow
    def test_performance_critical(self):
        # Slow test marked appropriately
        pass
```

#### Frontend Test Example

```javascript
// src/components/__tests__/NewComponent.test.js
import { render, screen } from "@testing-library/react";
import NewComponent from "../NewComponent";

test("renders new component", () => {
  render(<NewComponent />);
  const element = screen.getByText(/expected text/i);
  expect(element).toBeInTheDocument();
});
```

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
