"""
Test configuration and fixtures
"""
import pytest
import os

# Set test environment and use SQLite file for shared access between test and app
os.environ["TESTING"] = "true" 
os.environ["DATABASE_URL"] = "sqlite:///./test_database.db"

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from unittest.mock import patch

# Prevent main.py from running initialization code during tests
with patch('main.Base.metadata.create_all'):
    from data.models import Base
    from main import app


# Test database URL - use SQLite file for shared access
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test_database.db")

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True, scope="session")
def setup_database():
    """Setup database once for all tests - SQLite file needs manual cleanup"""
    import os
    
    # Remove test database file if it exists
    test_db_file = "./test_database.db"
    if os.path.exists(test_db_file):
        os.remove(test_db_file)
    
    # Create tables for tests
    Base.metadata.create_all(bind=engine)
    yield
    
    # Clean up test database file after tests - dispose engines first
    try:
        engine.dispose()
        # Also dispose main app engine
        from database import engine as main_engine
        main_engine.dispose()
    except:
        pass
        
    try:
        if os.path.exists(test_db_file):
            os.remove(test_db_file)
    except PermissionError:
        # File still in use - leave it for manual cleanup
        pass


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


@pytest.fixture
def clean_db():
    """Explicit fixture for tests that need clean slate - deletes all data but keeps tables"""
    # Clean BEFORE the test runs
    with engine.connect() as connection:
        # Delete all data from all tables in reverse order to handle foreign keys
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())
        connection.commit()
    yield
    # Also clean after the test (optional)
    with engine.connect() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())
        connection.commit()


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