"""
Data Layer - SQLAlchemy Database Models
Database table definitions
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base   # <-- IMPORTANT: import Base from database.py (do NOT redefine)


class Customer(Base):
    """Customer database model"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    company = Column(String, nullable=False)
    segment = Column(String, nullable=False)  # enterprise, smb, startup
    plan_type = Column(String, default="basic")  # basic, pro, enterprise
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Customer profile data
    monthly_revenue = Column(Float, default=0.0)
    employee_count = Column(Integer, default=1)
    industry = Column(String)
    
    # Relationships
    events = relationship("CustomerEvent", back_populates="customer")
    health_scores = relationship("HealthScore", back_populates="customer")


class CustomerEvent(Base):
    """Customer event database model"""
    __tablename__ = "customer_events"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    event_type = Column(String, nullable=False)  # login, feature_use, support_ticket, payment, api_call
    event_data = Column(JSON)  # Additional event-specific data
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    customer = relationship("Customer", back_populates="events")


class HealthScore(Base):
    """Health score database model"""
    __tablename__ = "health_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    score = Column(Float, nullable=False)  # 0-100 score
    status = Column(String, nullable=False)  # healthy, at_risk, critical
    factors = Column(JSON)  # Breakdown of score factors
    recommendations = Column(JSON)  # Generated recommendations
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    customer = relationship("Customer", back_populates="health_scores")