# Architecture Overview

## System Architecture

The Customer Health Scoring System follows **Clean Architecture** principles with clear separation of concerns across multiple layers. The system is designed to be scalable, maintainable, and easily extensible.

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │ SQLite Database │
│   (Port 3000)    │◄──►│   (Port 8000)    │◄──►│                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
    ┌────▼────┐              ┌────▼────┐              ┌────▼────┐
    │ Nginx   │              │ Uvicorn │              │ Volume  │
    │ Proxy   │              │ ASGI    │              │ Storage │
    └─────────┘              └─────────┘              └─────────┘
```

---

## Backend Architecture

### Layer Structure

The backend follows a **Domain-Driven Design** approach with these layers:

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                      │
│  • HTTP endpoints        • Request validation               │
│  • Response formatting   • Error handling                   │
└─────────────────────────────────────────────────────────────┘
                                   │
┌─────────────────────────────────────────────────────────────┐
│                   Services Layer                            │
│  • Business workflows    • Event coordination               │
│  • External integrations • Background tasks                 │
└─────────────────────────────────────────────────────────────┘
                                   │
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                             │
│  • Business logic       • Health score calculation          │
│  • Domain entities      • Health factors                    │
│  • Controllers          • Domain exceptions                 │
└─────────────────────────────────────────────────────────────┘
                                   │
┌─────────────────────────────────────────────────────────────┐
│                  Data Access Layer                          │
│  • Repository pattern   • ORM models                        │
│  • Database operations  • Data persistence                  │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── schemas.py             # Pydantic schemas for API
├── domain/                # Business logic layer
│   ├── models.py          # Domain entities
│   ├── calculators.py     # Health score algorithms
│   ├── controllers/       # Application controllers
│   │   ├── customer_controller.py
│   │   └── dashboard_controller.py
│   ├── health_factors/    # Pluggable health scoring factors
│   │   ├── base_factor.py
│   │   ├── api_usage_factor.py
│   │   ├── login_frequency_factor.py
│   │   ├── payment_timeliness_factor.py
│   │   ├── feature_adoption_factor.py
│   │   └── support_tickets_factor.py
│   └── exceptions.py      # Domain-specific exceptions
├── services/              # Application services
│   ├── customer_service.py
│   ├── health_service.py
│   └── event_service.py
├── data/                  # Data access layer
│   ├── models.py          # SQLAlchemy ORM models
│   ├── repositories/      # Repository implementations
│   │   ├── customer_repository.py
│   │   ├── health_score_repository.py
│   │   └── event_repository.py
│   └── database.py        # Database configuration
└── tests/                 # Test suites
    ├── unit/              # Unit tests
    ├── integration/       # Integration tests
    └── conftest.py        # Test configuration
```

---

## Domain Model

### Core Entities

#### Customer
```python
class Customer:
    id: int
    name: str
    email: str
    segment: CustomerSegment  # startup, smb, enterprise
    created_at: datetime
    health_scores: List[HealthScore]
    events: List[CustomerEvent]
```

#### Health Score
```python
class HealthScore:
    id: int
    customer_id: int
    overall_score: float      # 0-100
    status: HealthStatus      # healthy, at_risk, critical
    calculated_at: datetime
    factor_scores: List[FactorScore]
```

#### Factor Score
```python
class FactorScore:
    factor_name: str
    score: float             # 0-100
    weight: float           # Factor weight in overall calculation
    details: Dict[str, Any] # Factor-specific details
```

#### Customer Event
```python
class CustomerEvent:
    id: int
    customer_id: int
    event_type: str         # api_call, login, payment, feature_use, support_ticket
    event_data: Dict[str, Any]
    timestamp: datetime
```

### Business Rules

#### Health Score Calculation
1. **Weighted Average**: Overall score = Σ(factor_score × weight)
2. **Status Classification**:
   - `healthy`: Score ≥ 75
   - `at_risk`: Score 50-74
   - `critical`: Score < 50
3. **Recalculation Triggers**: New events automatically trigger background recalculation

#### Customer Segments
- **Enterprise**: Expected 1000+ API calls/month, higher service expectations
- **SMB**: Expected 500+ API calls/month, balanced expectations
- **Startup**: Expected 200+ API calls/month, growth-focused metrics

---

## Health Factors System

### Pluggable Architecture

The health scoring system uses a pluggable architecture where each factor implements `BaseHealthFactor`:

```python
class BaseHealthFactor:
    def calculate_score(self, customer: Customer, events: List[CustomerEvent]) -> FactorScore:
        """Calculate score for this factor (0-100)"""
        pass

    def get_weight(self) -> float:
        """Return the weight of this factor in overall calculation"""
        pass
```

### Available Health Factors

#### 1. API Usage Factor (Weight: 0.30)
- **Purpose**: Measures API engagement and platform adoption
- **Calculation**: Compares actual vs expected API calls based on customer segment
- **Key Metrics**: Call volume, endpoint diversity, error rates

#### 2. Login Frequency Factor (Weight: 0.20)
- **Purpose**: Tracks user engagement and platform stickiness
- **Calculation**: Evaluates login patterns and session frequency
- **Key Metrics**: Login count, session duration, user activity

#### 3. Payment Timeliness Factor (Weight: 0.25)
- **Purpose**: Assesses financial health and payment behavior
- **Calculation**: Analyzes payment delays and billing compliance
- **Key Metrics**: Payment delays, on-time percentage, outstanding balances

#### 4. Feature Adoption Factor (Weight: 0.15)
- **Purpose**: Measures platform utilization and value realization
- **Calculation**: Tracks feature usage across available capabilities
- **Key Metrics**: Features used, adoption rate, advanced feature usage

#### 5. Support Tickets Factor (Weight: 0.10)
- **Purpose**: Evaluates customer satisfaction and platform issues
- **Calculation**: Analyzes support interaction patterns and resolution
- **Key Metrics**: Ticket volume, resolution time, satisfaction scores

---

## Frontend Architecture

### Component Structure

```
frontend/src/
├── App.tsx                # Main application component
├── components/            # Reusable UI components
│   ├── Dashboard/         # Dashboard-specific components
│   │   ├── CustomerList.jsx
│   │   ├── HealthMetrics.jsx
│   │   └── StatCards.jsx
│   └── HealthScore/       # Health score components
│       ├── CustomerActivityForm.jsx
│       ├── HealthScoreDetail.jsx
│       └── FactorBreakdown.jsx
├── services/              # API communication layer
│   └── api.js            # Axios-based API client
├── hooks/                 # Custom React hooks
│   ├── useCustomers.js   # Customer data management
│   ├── useHealthScores.js # Health score data
│   └── useDashboard.js   # Dashboard statistics
├── types/                 # TypeScript type definitions
├── utils/                 # Utility functions
│   ├── healthScore.js    # Score calculation helpers
│   └── formatters.js     # Data formatting utilities
└── styles/               # Styling (Tailwind CSS)
```

### State Management

The application uses **React Hooks** for state management:
- **Local State**: Component-specific state via `useState`
- **API State**: Custom hooks with caching and error handling
- **Form State**: Controlled components with validation

### Data Flow

```
User Action → Component → Custom Hook → API Service → Backend API
     ↑                                                      ↓
UI Update ← State Update ← Response Processing ← API Response
```

---

## Database Design

### Schema Overview

```sql
-- Customers table
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    segment VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Health scores table
CREATE TABLE health_scores (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    overall_score FLOAT NOT NULL,
    status VARCHAR(50) NOT NULL,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Factor scores table (JSON storage for flexibility)
CREATE TABLE factor_scores (
    id INTEGER PRIMARY KEY,
    health_score_id INTEGER REFERENCES health_scores(id),
    factor_name VARCHAR(100) NOT NULL,
    score FLOAT NOT NULL,
    weight FLOAT NOT NULL,
    details TEXT -- JSON data
);

-- Customer events table
CREATE TABLE customer_events (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    event_type VARCHAR(50) NOT NULL,
    event_data TEXT, -- JSON data
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Data Relationships

```
Customer (1) ──── (M) HealthScore
    │                    │
    │                    │
   (M)                  (M)
    │                    │
CustomerEvent        FactorScore
```

---

## Deployment Architecture

### Docker Containerization

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Host                             │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐               │
│  │   Frontend      │    │    Backend      │               │
│  │   Container     │    │   Container     │               │
│  │                 │    │                 │               │
│  │ • Nginx         │    │ • FastAPI       │               │
│  │ • React Build   │    │ • Uvicorn       │               │
│  │ • Port 3000     │    │ • Port 8000     │               │
│  └─────────────────┘    └─────────────────┘               │
│           │                       │                        │
│           └───────────────┬───────┘                        │
│                          │                                │
│                 ┌─────────▼─────────┐                     │
│                 │   SQLite Volume   │                     │
│                 │                   │                     │
│                 │ • Data persistence│                     │
│                 │ • Backup support  │                     │
│                 └───────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

### Service Communication

- **Frontend ↔ Backend**: HTTP REST API calls via Nginx proxy
- **Backend ↔ Database**: SQLAlchemy ORM with connection pooling
- **Inter-container**: Docker network with service discovery

---

## Security Considerations

### Current Implementation
- **Input Validation**: Pydantic schemas validate all API inputs
- **SQL Injection**: SQLAlchemy ORM prevents SQL injection
- **CORS**: Configured for local development
- **Error Handling**: Sanitized error responses

### Production Recommendations
- **Authentication**: JWT tokens or OAuth2
- **Rate Limiting**: Per-IP and per-customer limits
- **HTTPS**: SSL/TLS encryption
- **Input Sanitization**: Additional validation layers
- **Monitoring**: Request logging and anomaly detection

---

## Performance Considerations

### Current Optimizations
- **Database Indexing**: Indexes on frequently queried columns
- **Connection Pooling**: SQLAlchemy connection pool
- **Caching**: Docker layer caching for faster builds
- **Compression**: Nginx gzip compression for static assets

### Scaling Recommendations
- **Database**: Consider PostgreSQL for larger datasets
- **Caching**: Redis for session and query caching
- **Load Balancing**: Multiple backend instances
- **CDN**: Static asset distribution
- **Background Jobs**: Celery for async health score calculations

---

## Extension Points

### Adding New Health Factors
1. Create new class inheriting from `BaseHealthFactor`
2. Implement scoring algorithm
3. Add to factor registry in `calculators.py`
4. Create frontend form components
5. Add tests

### Custom Customer Segments
1. Extend `CustomerSegment` enum
2. Update factor calculation logic
3. Modify frontend segment selection
4. Update documentation

### Event Types
1. Add new event type to validation schemas
2. Implement event processing logic
3. Update frontend form
4. Add relevant health factor updates

### API Extensions
1. Version endpoints (`/api/v1/`, `/api/v2/`)
2. Add filtering and pagination
3. Implement WebSocket for real-time updates
4. Add bulk operations support

This architecture provides a solid foundation for a scalable customer health monitoring system while maintaining clean code organization and extensibility.