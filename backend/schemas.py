"""
Pydantic Schemas for API Request/Response Validation

This module defines all Pydantic models used for API request and response validation
in the Customer Health Scoring System. These schemas ensure data integrity,
type safety, and automatic API documentation generation.

Schema Categories:
- Customer schemas: Customer creation, updates, and responses
- Event schemas: Customer event recording and responses
- Health score schemas: Health score details and breakdowns
- Dashboard schemas: Statistics and summary data

Key Features:
- Automatic validation of incoming request data
- Type conversion and coercion where appropriate
- Email validation using EmailStr
- Optional fields with sensible defaults
- Nested models for complex data structures
- Configuration for ORM compatibility

Validation Benefits:
- Prevents invalid data from entering the system
- Provides clear error messages for API consumers
- Generates accurate OpenAPI/Swagger documentation
- Ensures consistent data types across API endpoints

Usage:
    from schemas import CustomerCreate, CustomerEventCreate

    # Validate incoming data
    customer_data = CustomerCreate(**request_json)
    event_data = CustomerEventCreate(**event_json)

Author: Customer Health Team
"""

from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, Dict, List, Any

# Customer schemas
class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    company: str
    segment: str

class CustomerCreate(CustomerBase):
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    monthly_revenue: Optional[float] = None
    plan_type: Optional[str] = "basic"

class CustomerResponse(CustomerBase):
    id: int
    industry: Optional[str]
    employee_count: Optional[int]
    monthly_revenue: Optional[float]
    plan_type: str
    created_at: datetime
    last_activity: Optional[datetime]
    
    class Config:
        from_attributes = True

class CustomerListResponse(BaseModel):
    id: int
    name: str
    email: str
    company: str
    segment: str
    created_at: datetime
    health_score: float
    health_status: str
    last_activity: Optional[datetime]

# Event schemas
class CustomerEventCreate(BaseModel):
    event_type: str
    event_data: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None

class CustomerEventResponse(BaseModel):
    id: int
    customer_id: int
    event_type: str
    event_data: Optional[Dict[str, Any]]
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Health score schemas
class HealthScoreResponse(BaseModel):
    id: int
    customer_id: int
    score: float
    status: str
    calculated_at: datetime
    
    class Config:
        from_attributes = True

class HealthFactorDetail(BaseModel):
    score: float
    value: Any
    description: str
    trend: Optional[str] = None

class HealthScoreDetailResponse(BaseModel):
    customer_id: int
    customer_name: str
    overall_score: float
    status: str
    factors: Dict[str, Any]
    calculated_at: datetime
    recommendations: List[str]

# Dashboard schemas
class DashboardStats(BaseModel):
    total_customers: int
    healthy_customers: int
    at_risk_customers: int
    critical_customers: int
    last_updated: datetime