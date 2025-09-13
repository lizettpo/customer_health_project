# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## AI Development Assistance

This project was developed with AI assistance using Claude Code. Key areas where AI was utilized include:
- **Architecture Design**: Clean architecture implementation and separation of concerns
- **Testing Strategy**: Comprehensive test suite with 85%+ coverage requirement
- **Docker Optimization**: Multi-stage builds and performance optimizations
- **Documentation**: API documentation, architecture overview, and user guides
- **Code Quality**: Consistent patterns, error handling, and logging implementation

The core business logic, domain models, and health scoring algorithms represent the primary intellectual contribution, with AI assistance for implementation details and best practices.

## Development Commands

### Backend (FastAPI + SQLAlchemy)
- **Run server**: `cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- **Run tests**: `cd backend && python run_tests.py`
- **Install dependencies**: `cd backend && pip install -r requirements.txt`
- **Database**: Uses SQLite with auto-create tables on startup
- **Logging**: File logging with rotation enabled in `backend/logs/`

### Testing
- **Single command**: `cd backend && python run_tests.py` 
- **Coverage**: Minimum 85% code coverage required
- **Test types**: Unit tests (116 tests) + Integration tests (16 tests)
- **Test structure**: 
  - `tests/unit/` - Unit tests for individual components
  - `tests/integration/` - API endpoint integration tests
  - `tests/conftest.py` - Test configuration and fixtures

### Frontend (React + TypeScript)
- **Run development**: `cd frontend && npm start` (http://localhost:3000)
- **Install dependencies**: `cd frontend && npm install`
- **Build production**: `cd frontend && npm run build`
- **Run tests**: `cd frontend && npm test`

### Docker
- **Production**: `docker-compose up -d --build`
- **Development**: `docker-compose -f docker-compose.dev-all.yml up -d --build`
- **Backend Only**: `docker-compose -f docker-compose.dev.yml up -d --build`
- **View Logs**: `docker-compose logs -f`

## Architecture Overview

This is a **Clean Architecture** customer health scoring system with clear separation of concerns:

### Core Structure
```
customer_health_project/
├── README.md                    # Main project documentation
├── CLAUDE.md                    # AI development guidance
├── HEALTH_SCORE_GUIDE.md       # Health scoring documentation
├── docker-compose.yml          # Production deployment
├── docker-compose.dev.yml      # Backend-only development
├── docker-compose.dev-all.yml  # Full-stack development
├── docker-compose.prod.yml     # Production variant
├── .dockerignore               # Docker build exclusions
├── .gitignore                  # Git exclusions
├── backend/                    # FastAPI backend application
│   ├── main.py                # FastAPI application entry point
│   ├── schemas.py             # Pydantic schemas for API validation
│   ├── database.py            # SQLAlchemy database configuration
│   ├── sample_data.py         # Sample data generation
│   ├── requirements.txt       # Python dependencies
│   ├── pytest.ini            # Test configuration
│   ├── run_tests.py           # Custom test runner
│   ├── clean_test_db.py       # Test database cleanup
│   ├── Dockerfile             # Production container build
│   ├── Dockerfile.dev         # Development container build
│   ├── .dockerignore          # Backend build exclusions
│   ├── logs/                  # Application logs (auto-created)
│   ├── data/                  # SQLite database storage
│   │   ├── models.py          # SQLAlchemy ORM models
│   │   └── repositories.py    # Data access repositories
│   ├── domain/                # Business logic layer (Clean Architecture)
│   │   ├── models.py          # Domain entities (Customer, HealthScore)
│   │   ├── calculators.py     # Health score calculation orchestration
│   │   ├── exceptions.py      # Domain-specific exceptions
│   │   ├── controllers/       # Application controllers
│   │   │   ├── customer_controller.py    # Customer operations
│   │   │   └── health_score_controller.py # Health score operations
│   │   └── health_factors/    # Pluggable health scoring factors
│   │       ├── base_factor.py          # Base health factor interface
│   │       ├── api_usage.py            # API usage scoring
│   │       ├── login_frequency.py      # Login engagement scoring
│   │       ├── payment_timeliness.py   # Payment behavior scoring
│   │       ├── feature_adoption.py     # Feature usage scoring
│   │       └── support_tickets.py      # Support interaction scoring
│   ├── services/              # Application services layer
│   │   ├── customer_service.py         # Customer business workflows
│   │   └── health_score_service.py     # Health score workflows
│   └── tests/                 # Test suites (116 unit + 16 integration)
│       ├── conftest.py        # Pytest fixtures and configuration
│       ├── unit/              # Unit tests for individual components
│       │   ├── test_customer_service.py
│       │   ├── test_health_score_calculator.py
│       │   ├── test_api_usage_factor.py
│       │   ├── test_login_frequency_factor.py
│       │   ├── test_payment_timeliness_factor.py
│       │   ├── test_feature_adoption_factor.py
│       │   ├── test_support_tickets_factor.py
│       │   ├── test_customer_controller.py
│       │   ├── test_health_score_controller.py
│       │   └── test_health_score_service.py
│       └── integration/       # End-to-end API tests
│           └── test_api_endpoints.py
├── frontend/                  # React frontend application
│   ├── package.json           # Node.js dependencies and scripts
│   ├── package-lock.json      # Dependency lock file
│   ├── Dockerfile             # Production container build
│   ├── Dockerfile.dev         # Development container build
│   ├── nginx.conf             # Nginx configuration for production
│   ├── .dockerignore          # Frontend build exclusions
│   ├── tailwind.config.js     # Tailwind CSS configuration
│   ├── postcss.config.js      # PostCSS configuration
│   ├── build/                 # Production build output (generated)
│   ├── public/                # Static assets
│   │   ├── index.html         # Main HTML template
│   │   └── favicon.ico        # Application icon
│   └── src/                   # Source code
│       ├── index.js           # React application entry point
│       ├── App.jsx            # Main React application component
│       ├── App.css            # Application-wide styles
│       ├── index.css          # Global styles and Tailwind imports
│       ├── reportWebVitals.js # Performance monitoring
│       ├── components/        # React UI components
│       │   ├── Dashboard/     # Dashboard-related components
│       │   │   ├── CustomerList.jsx      # Customer listing
│       │   │   ├── DashboardStats.jsx    # Statistics overview
│       │   │   └── HealthDistribution.jsx # Health score distribution
│       │   └── HealthScore/   # Health score detail components
│       │       ├── CustomerActivityForm.jsx    # Event recording form
│       │       ├── CustomerActivityForm.css    # Form styles
│       │       ├── HealthScoreDetail.jsx       # Detailed score breakdown
│       │       └── FactorBreakdown.jsx         # Individual factor details
│       ├── services/          # API communication layer
│       │   └── api.js         # Axios-based API client
│       ├── hooks/             # Custom React hooks for state management
│       │   ├── useCustomers.js    # Customer data hooks
│       │   ├── useHealthScores.js # Health score data hooks
│       │   └── useDashboard.js    # Dashboard statistics hooks
│       └── utils/             # Utility functions
│           ├── healthScore.js     # Health score calculation helpers
│           └── formatters.js      # Data formatting utilities
├── docs/                      # Project documentation
│   ├── API.md                 # Complete API documentation
│   ├── ARCHITECTURE.md        # System architecture overview
│   ├── LOGGING.md             # Logging configuration guide
│   └── SCREENSHOTS.md         # Visual documentation template
└── screenshots/               # Application screenshots and demos
    ├── README.md              # Screenshot organization guide
    ├── *.png                  # Application screenshots
    ├── *.mp4                  # Screen recordings
    ├── dashboard/             # Dashboard screenshots (organized)
    ├── customers/             # Customer view screenshots
    ├── forms/                 # Form screenshots
    ├── api/                   # API documentation screenshots
    └── mobile/                # Mobile view screenshots
```

### Key Domain Concepts

**Health Factors**: Modular scoring components that inherit from `BaseHealthFactor`:
- `APIUsageFactor` - API call frequency scoring
- `LoginFrequencyFactor` - User engagement scoring  
- `PaymentTimelinessFactor` - Payment behavior scoring
- `FeatureAdoptionFactor` - Feature usage scoring
- `SupportTicketsFactor` - Support interaction scoring

**Customer Segments**: Affects expectations and calculations:
- Enterprise (1000+ expected API calls)
- SMB (500+ expected API calls)  
- Startup (200+ expected API calls)

### Database Configuration
- **SQLite database**: `data/customer_health.db`
- **Docker persistence**: Volume-mounted for data retention
- **Auto-creation**: Tables created automatically on startup
- **Sample data**: Populated automatically on first run

### API Endpoints
- `GET /` - Basic API information
- `GET /api/customers` - List customers with health scores
- `GET /api/customers/{id}/health` - Detailed health breakdown
- `POST /api/customers/{id}/events` - Record customer events
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard` - Serve React frontend

### Health Score Calculation
Health scores are calculated using weighted factors and stored in the database. The system calculates scores on-demand when requested. Each factor contributes to an overall score (0-100) with status classification (healthy/at_risk/critical).

## Development Guidelines

### Code Changes
- **Function signatures**: Always update tests when modifying function signatures
- **New functions**: Add comprehensive tests in relevant test files
- **Coverage requirement**: Maintain minimum 85% test coverage
- **Event validation**: All event types require specific data fields for form validation

### Project Status
- **Database**: Migrated from PostgreSQL to SQLite for simplified deployment
- **Docker**: Optimized with layer caching and resource limits
- **Logging**: Comprehensive file logging with rotation (10MB files, 5 backups)
- **Documentation**: Complete API docs, architecture guide, and testing instructions