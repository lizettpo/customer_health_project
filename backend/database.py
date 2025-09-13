"""
Database Configuration and Setup Module

This module configures the SQLAlchemy database engine, session management, and
declarative base for the Customer Health Scoring System.

The system uses SQLite by default for simplified deployment and development,
but retains configuration flexibility for PostgreSQL if needed in production.

Key Components:
- Database engine with optimized connection settings
- Session factory for database transactions
- Declarative base for ORM model definitions
- Environment-specific configuration handling

Database Schema:
- customers: Core customer information and metadata
- health_scores: Calculated health scores and status
- factor_scores: Individual factor contributions to health scores
- customer_events: Timestamped customer activity events

Connection Management:
- SQLite: Uses file-based database with thread safety disabled for FastAPI
- Connection pooling and recycling optimized for each database type
- Auto-commit disabled for explicit transaction control
- Session factory pattern for proper resource management

Usage:
    from database import engine, SessionLocal, Base

    # Create database session
    db = SessionLocal()
    try:
        # Database operations
        pass
    finally:
        db.close()

Author: Customer Health Team
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL configuration
# Default to SQLite for development and simplified deployment
# Can be overridden via environment variable for production PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/customer_health.db")

# Create SQLAlchemy engine with database-specific optimizations
if "sqlite" in DATABASE_URL:
    # SQLite-specific configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Allow FastAPI threading
        pool_recycle=-1,  # Disable connection recycling for SQLite
        echo=False,  # Set to True for SQL query debugging
        future=True  # Use SQLAlchemy 2.0 style
    )
else:
    # PostgreSQL-specific configuration
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Validate connections before use
        pool_recycle=300,  # Recycle connections every 5 minutes
        pool_size=10,  # Connection pool size
        max_overflow=20,  # Additional connections beyond pool_size
        echo=False,  # Set to True for SQL debugging
        future=True  # Use SQLAlchemy 2.0 style
    )

# Create SessionLocal class for database session management
# Sessions are created per request and properly closed after use
SessionLocal = sessionmaker(
    autocommit=False,  # Explicit transaction control
    autoflush=False,   # Manual flush control for better performance
    bind=engine,
    expire_on_commit=False  # Keep objects usable after commit
)

# Create Base class for all ORM models
# All domain models inherit from this base class
Base = declarative_base()