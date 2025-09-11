"""
Test configuration and fixtures
"""
import pytest
import os

# Set test environment and database before importing any modules
os.environ["TESTING"] = "true" 
os.environ["DATABASE_URL"] = "postgresql://postgres:password123@localhost:5434/customer_health_test"

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from unittest.mock import patch

# Prevent main.py from running initialization code during tests
with patch('main.Base.metadata.create_all'):
    from data.models import Base
    from main import app


# Test database URL - use PostgreSQL for integration tests
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:password123@localhost:5434/customer_health_test")

engine = create_engine(
    TEST_DATABASE_URL
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def clean_database():
    """Utility function to completely clean the test database"""
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        
        # Also drop any remaining tables that might not be in metadata
        with engine.connect() as connection:
            # Get all table names
            result = connection.execute(text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
            """))
            tables = [row[0] for row in result.fetchall()]
            
            # Drop each table with CASCADE to handle foreign key constraints
            for table in tables:
                connection.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
            connection.commit()
            
        # Dispose engine connections
        engine.dispose()
        
    except Exception as e:
        print(f"Error cleaning database: {e}")


@pytest.fixture(autouse=True, scope="session")
def setup_and_cleanup_database():
    """Setup and cleanup database before and after all tests"""
    # Clean database before tests
    clean_database()
    
    # Create tables for tests
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Clean after all tests
    clean_database()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    from main import get_db
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


def truncate_tables():
    """Truncate all tables but keep the schema"""
    try:
        with engine.connect() as connection:
            # Get all table names
            result = connection.execute(text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
            """))
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                # Disable foreign key checks, truncate all tables, re-enable
                connection.execute(text('SET session_replication_role = replica'))
                for table in tables:
                    connection.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE'))
                connection.execute(text('SET session_replication_role = DEFAULT'))
                connection.commit()
                
    except Exception as e:
        print(f"Error truncating tables: {e}")


# Remove automatic cleaning - only clean at session level for speed


@pytest.fixture
def clean_db():
    """Explicit fixture to clean database - can be used by tests that need extra cleanup"""
    yield
    truncate_tables()


@pytest.fixture
def sample_customer_data():
    """Sample customer data for tests"""
    return {
        "name": "Test Customer",
        "email": "test@example.com",
        "company": "Test Company",
        "segment": "Enterprise"
    }


@pytest.fixture
def sample_event_data():
    """Sample event data for tests"""
    return {
        "event_type": "api_call",
        "event_data": {"endpoint": "/api/test", "status": "success"}
    }