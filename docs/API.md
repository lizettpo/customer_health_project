# API Documentation

## Base URL
- **Production**: `http://localhost:8000`
- **Development**: `http://localhost:8000`
- **Interactive Documentation**: `http://localhost:8000/docs` (Swagger UI)

## Authentication
Currently, no authentication is required. All endpoints are publicly accessible.

---

## Endpoints

### Root Endpoint

#### `GET /`
Basic API information and documentation link.

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Customer Health Score API",
    "docs": "/docs"
  }
}
```

**Status Codes:**
- `200`: Service is running

---

### Customers

#### `GET /api/customers`
Retrieve all customers with their current health scores.

**Query Parameters:**
- `health_status` (optional, string): Filter by health status ('healthy', 'at_risk', 'critical')

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Acme Corp",
      "email": "contact@acme.com",
      "company": "Acme Corp",
      "segment": "enterprise",
      "created_at": "2024-01-01T00:00:00Z",
      "health_score": 85.5,
      "health_status": "healthy",
      "last_activity": "2024-01-15T10:00:00Z"
    }
  ]
}
```

**Status Codes:**
- `200`: Success
- `500`: Internal server error


### Health Scores

#### `GET /api/customers/{customer_id}/health`
Get detailed health score breakdown for a customer.

**Path Parameters:**
- `customer_id` (integer): The customer's unique identifier

**Response:**
```json
{
  "success": true,
  "data": {
    "customer_id": 1,
    "customer_name": "Acme Corp",
    "overall_score": 85.5,
    "status": "healthy",
    "factors": {
      "api_usage": {
        "score": 90.0,
        "value": 1200,
        "description": "API calls per month",
        "trend": "up"
      },
      "login_frequency": {
        "score": 100.0,
        "value": 28,
        "description": "Login sessions per month",
        "trend": "stable"
      },
      "payment_timeliness": {
        "score": 75.0,
        "value": 5.2,
        "description": "Average days late",
        "trend": "down"
      },
      "feature_adoption": {
        "score": 80.0,
        "value": 0.8,
        "description": "Feature adoption rate",
        "trend": "up"
      },
      "support_tickets": {
        "score": 85.0,
        "value": 2,
        "description": "Support tickets last 30 days",
        "trend": "stable"
      }
    },
    "calculated_at": "2024-01-15T10:00:00Z",
    "recommendations": [
      "Consider upgrading payment automation",
      "Excellent API usage patterns"
    ]
  }
}
```

**Status Codes:**
- `200`: Success
- `404`: Customer not found
- `500`: Internal server error

---

### Events

#### `POST /api/customers/{customer_id}/events`
Record a new customer event (triggers health score recalculation).

**Path Parameters:**
- `customer_id` (integer): The customer's unique identifier

**Request Body:**
```json
{
  "event_type": "api_call",
  "event_data": {
    "endpoint": "/api/users",
    "method": "GET",
    "response_time": 250,
    "status_code": 200
  }
}
```

#### Event Types and Required Data

##### API Call Events
```json
{
  "event_type": "api_call",
  "event_data": {
    "endpoint": "/api/users",           // Required
    "method": "GET",                    // Optional
    "response_time": 250,              // Optional (ms)
    "status_code": 200                 // Optional
  }
}
```

##### Login Events
```json
{
  "event_type": "login",
  "event_data": {
    "ip_address": "192.168.1.100",     // Required
    "user_agent": "Mozilla/5.0...",    // Optional
    "session_duration": 3600           // Optional (seconds)
  }
}
```

##### Payment Events
```json
{
  "event_type": "payment",
  "event_data": {
    "amount": 99.99,                   // Required
    "currency": "USD",                 // Optional
    "payment_method": "credit_card",   // Optional
    "transaction_id": "txn_12345"      // Optional
  }
}
```

##### Feature Usage Events
```json
{
  "event_type": "feature_use",
  "event_data": {
    "feature_name": "advanced_analytics", // Required
    "usage_duration": 1800,              // Optional (seconds)
    "feature_category": "analytics"       // Optional
  }
}
```

##### Support Ticket Events
```json
{
  "event_type": "support_ticket",
  "event_data": {
    "ticket_id": "TICKET-001",         // Optional
    "priority": "high",                // Optional
    "category": "technical",           // Optional
    "resolution_time": 7200            // Optional (seconds)
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "event_id": 12345,
    "customer_id": 1,
    "event_type": "api_call",
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "message": "Event recorded successfully"
}
```

**Status Codes:**
- `200`: Event recorded successfully
- `400`: Invalid request data
- `404`: Customer not found
- `422`: Validation error (missing required fields)
- `500`: Internal server error

---

---

### Dashboard

#### `GET /api/dashboard/stats`
Get overall dashboard statistics and metrics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_customers": 150,
    "healthy_customers": 89,
    "at_risk_customers": 45,
    "critical_customers": 16,
    "distribution": {
      "healthy_percent": 59.3,
      "at_risk_percent": 30.0,
      "critical_percent": 10.7
    },
    "last_updated": "2024-01-15T10:30:00Z"
  }
}
```

**Status Codes:**
- `200`: Success
- `500`: Internal server error

#### `GET /api/dashboard`
Serve the React dashboard interface (returns HTML file).

**Response:**
- Returns the React application HTML file

**Status Codes:**
- `200`: HTML file served successfully

---

## Error Response Format

All error responses follow this structure:

```json
{
  "success": false,
  "error": "Error category",
  "detail": "Detailed error message"
}
```

### Common Error Codes
- `CUSTOMER_NOT_FOUND`: Customer with specified ID doesn't exist
- `INVALID_EVENT_TYPE`: Unsupported event type provided
- `MISSING_REQUIRED_FIELD`: Required field missing from event data
- `VALIDATION_ERROR`: Data validation failed
- `DATABASE_ERROR`: Database operation failed

---

## Rate Limiting
Currently no rate limiting is implemented. In production, consider implementing:
- 1000 requests per hour per IP
- 100 event submissions per minute per customer

---

## Data Models

### Customer Segments
- `startup`: 200+ expected API calls/month
- `smb`: 500+ expected API calls/month
- `enterprise`: 1000+ expected API calls/month

### Health Score Status
- `critical`: Score < 50
- `at_risk`: Score 50-74
- `healthy`: Score >= 75

### Supported Event Types
- `api_call`: API usage tracking
- `login`: User authentication events
- `payment`: Payment and billing events
- `feature_use`: Feature usage tracking
- `support_ticket`: Support interaction events

---

## WebSocket Support
Not currently implemented. Consider adding for real-time health score updates.

---

## Pagination
List endpoints support pagination via `skip` and `limit` parameters:
- Default `limit`: 100
- Maximum `limit`: 1000
- Use `skip` for offset-based pagination

---

## Filtering and Sorting
Currently not implemented. Future enhancements may include:
- Filter customers by segment, health status
- Sort by score, last activity, creation date
- Search by customer name or email