# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (FastAPI + SQLAlchemy)
- **Run server**: `cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- **Run tests**: `cd backend && python run_tests.py`
- **Install dependencies**: `cd backend && pip install -r requirements.txt`
- **Database migrations**: Uses SQLAlchemy with auto-create tables on startup

### Testing
- **Single command**: `cd backend && python run_tests.py` 
- **Coverage**: Minimum 85% code coverage required
- **Test types**: Unit tests (116 tests) + Integration tests (16 tests)
- **Test structure**: 
  - `tests/unit/` - Unit tests for individual components
  - `tests/integration/` - API endpoint integration tests
  - `tests/conftest.py` - Test configuration and fixtures

### Docker
- **Build**: `cd backend && docker build -t customer-health-api .`
- **Run**: `docker run -p 8000:8000 customer-health-api`

## Architecture Overview

This is a **Clean Architecture** customer health scoring system with clear separation of concerns:

### Core Structure
```
backend/
├── domain/           # Business logic layer
│   ├── models.py    # Domain entities (Customer, HealthScore, FactorScore)
│   ├── calculators.py # Health score calculation logic
│   ├── controllers/ # Application controllers
│   ├── health_factors/ # Pluggable health factors
│   └── exceptions.py # Domain exceptions
├── services/        # Application services layer
├── data/           # Data access layer (repositories, ORM models)
├── schemas.py      # Pydantic schemas for API
└── main.py         # FastAPI application entry point
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
- PostgreSQL database with connection string: `postgresql://postgres:password123@localhost:5432/customer_health`
- Uses SQLAlchemy ORM with auto-table creation
- Sample data populated automatically on first run

### API Endpoints
- `GET /api/customers` - List customers with health scores
- `GET /api/customers/{id}/health` - Detailed health breakdown
- `POST /api/customers/{id}/events` - Record customer events (triggers background health recalculation)
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /health` - Health check

### Health Score Calculation
Health scores are calculated using weighted factors and stored in the database. The system supports background recalculation when new events are recorded. Each factor contributes to an overall score (0-100) with status classification (healthy/at_risk/critical).
- when adding or editing function signertures always update the 
  tests and if function is new add new tests in the relevent test 
  file