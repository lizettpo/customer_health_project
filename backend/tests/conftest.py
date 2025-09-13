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
def memory_store_setup(db_session):
    """Setup memory store with fast mock data and database connection"""
    from domain.memory_store import memory_store
    from domain.models import Customer as DomainCustomer, HealthScore as DomainHealthScore
    from datetime import datetime
    from unittest.mock import Mock

    # Create fast mock data directly
    test_customer = DomainCustomer(
        id=1,
        name="Test Customer",
        email="test@example.com",
        company="Test Company",
        segment="Enterprise",
        created_at=datetime.utcnow(),
        last_activity=datetime.utcnow()
    )

    # Create mock health score with simple structure
    test_health_score = DomainHealthScore(
        id=1,
        customer_id=1,
        score=85.0,
        status="healthy",
        factors={
            "api_usage": type('obj', (object,), {
                'score': 85.0, 'value': 100, 'description': "Good usage",
                'trend': "stable", 'metadata': {}
            })()
        },
        calculated_at=datetime.utcnow(),
        recommendations=["Keep it up"]
    )

    # Set database connection for operations that need it
    memory_store.set_database(db_session)

    # Directly set memory store data - no database calls
    memory_store.customers = {1: test_customer}
    memory_store.health_scores = {1: test_health_score}
    memory_store.events = {1: []}

    # Mock the heavy database operations to return fast results
    from domain.exceptions import CustomerNotFoundError

    original_add_event = memory_store.add_customer_event
    def mock_add_event(customer_id, event_type, event_data, timestamp=None):
        if customer_id not in memory_store.customers:
            raise CustomerNotFoundError(f"Customer {customer_id} not found")

        return {
            "message": "Event recorded successfully",
            "event_id": 1,
            "customer_id": customer_id,
            "customer_name": memory_store.customers[customer_id].name,
            "event_type": event_type,
            "timestamp": (timestamp or datetime.utcnow()).isoformat(),
            "new_health_score": 85.0,
            "new_health_status": "healthy"
        }

    memory_store.add_customer_event = mock_add_event

    original_recalculate = memory_store.recalculate_all_health_scores
    def mock_recalculate():
        return len(memory_store.customers)

    memory_store.recalculate_all_health_scores = mock_recalculate

    yield memory_store

    # Restore original methods
    memory_store.add_customer_event = original_add_event
    memory_store.recalculate_all_health_scores = original_recalculate

    # Clean up
    memory_store.customers.clear()
    memory_store.events.clear()
    memory_store.health_scores.clear()


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