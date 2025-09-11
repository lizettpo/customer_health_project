"""
Integration tests for API endpoints
Tests the complete flow from API request to database
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

from data.models import Customer, Event, HealthScore
from schemas import CustomerEventCreate


class TestCustomerEndpoints:
    """Integration tests for customer-related endpoints"""
    
    def test_get_customers_success(self, client: TestClient, db_session: Session):
        """Test GET /api/customers endpoint"""
        # Create test data
        customer = Customer(
            name="Test Customer",
            email="test@example.com",
            company="Test Company",
            segment="Enterprise"
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)
        
        # Create health score
        health_score = HealthScore(
            customer_id=customer.id,
            score=85.5,
            status="healthy",
            factors={},
            recommendations=[],
            calculated_at=datetime.utcnow()
        )
        db_session.add(health_score)
        db_session.commit()
        
        # Make API request
        response = client.get("/api/customers")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Test Customer"
        assert data["data"][0]["health_score"] == 85.5
        assert data["data"][0]["health_status"] == "healthy"
    
    def test_get_customers_with_pagination(self, client: TestClient, db_session: Session):
        """Test GET /api/customers with pagination"""
        # Create multiple customers
        for i in range(5):
            customer = Customer(
                name=f"Customer {i}",
                email=f"customer{i}@example.com",
                company=f"Company {i}",
                segment="SMB"
            )
            db_session.add(customer)
        db_session.commit()
        
        # Test with limit
        response = client.get("/api/customers?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 3
        
        # Test with offset
        response = client.get("/api/customers?limit=2&offset=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
    
    def test_get_customers_filtered_by_health_status(self, client: TestClient, db_session: Session):
        """Test GET /api/customers filtered by health status"""
        # Create customers with different health statuses
        healthy_customer = Customer(
            name="Healthy Customer",
            email="healthy@example.com",
            company="Healthy Co",
            segment="Enterprise"
        )
        at_risk_customer = Customer(
            name="At Risk Customer", 
            email="risk@example.com",
            company="Risk Co",
            segment="SMB"
        )
        db_session.add_all([healthy_customer, at_risk_customer])
        db_session.commit()
        
        # Add health scores
        healthy_score = HealthScore(
            customer_id=healthy_customer.id,
            score=85.0,
            status="healthy",
            factors={},
            recommendations=[],
            calculated_at=datetime.utcnow()
        )
        at_risk_score = HealthScore(
            customer_id=at_risk_customer.id,
            score=55.0,
            status="at_risk",
            factors={},
            recommendations=[],
            calculated_at=datetime.utcnow()
        )
        db_session.add_all([healthy_score, at_risk_score])
        db_session.commit()
        
        # Test filtering by health status
        response = client.get("/api/customers?health_status=healthy")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Healthy Customer"
        assert data["data"][0]["health_status"] == "healthy"
    
    def test_get_customers_empty_result(self, client: TestClient, db_session: Session):
        """Test GET /api/customers with no customers"""
        response = client.get("/api/customers")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"] == []


class TestHealthScoreEndpoints:
    """Integration tests for health score endpoints"""
    
    def test_get_customer_health_detail_success(self, client: TestClient, db_session: Session):
        """Test GET /api/customers/{id}/health endpoint"""
        # Create test customer
        customer = Customer(
            name="Test Customer",
            email="test@example.com", 
            company="Test Company",
            segment="Enterprise"
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)
        
        # Create some events
        events = [
            Event(
                customer_id=customer.id,
                event_type="login",
                event_data={},
                timestamp=datetime.utcnow() - timedelta(days=i)
            )
            for i in range(10)
        ]
        db_session.add_all(events)
        db_session.commit()
        
        # Make API request
        response = client.get(f"/api/customers/{customer.id}/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        health_data = data["data"]
        assert health_data["customer_id"] == customer.id
        assert health_data["customer_name"] == "Test Customer"
        assert "overall_score" in health_data
        assert "status" in health_data
        assert "factors" in health_data
    
    def test_get_customer_health_detail_not_found(self, client: TestClient, db_session: Session):
        """Test GET /api/customers/{id}/health for non-existent customer"""
        response = client.get("/api/customers/999/health")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "error" in data
        assert "Customer not found" in data["detail"]
    
    def test_get_dashboard_stats_success(self, client: TestClient, db_session: Session):
        """Test GET /api/dashboard/stats endpoint"""
        # Create test customers with health scores
        customers = []
        for i in range(3):
            customer = Customer(
                name=f"Customer {i}",
                email=f"customer{i}@example.com",
                company=f"Company {i}",
                segment="Enterprise"
            )
            customers.append(customer)
            db_session.add(customer)
        db_session.commit()
        
        # Create health scores
        statuses = ["healthy", "at_risk", "critical"]
        scores = [85.0, 60.0, 30.0]
        for i, (customer, status, score) in enumerate(zip(customers, statuses, scores)):
            health_score = HealthScore(
                customer_id=customer.id,
                score=score,
                status=status,
                factors={},
                recommendations=[],
                calculated_at=datetime.utcnow()
            )
            db_session.add(health_score)
        db_session.commit()
        
        # Make API request
        response = client.get("/api/dashboard/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        stats = data["data"]
        assert stats["total_customers"] == 3
        assert stats["healthy_customers"] == 1
        assert stats["at_risk_customers"] == 1
        assert stats["critical_customers"] == 1
        assert "average_health_score" in stats
        assert "distribution" in stats


class TestEventEndpoints:
    """Integration tests for event-related endpoints"""
    
    def test_record_customer_event_success(self, client: TestClient, db_session: Session):
        """Test POST /api/customers/{id}/events endpoint"""
        # Create test customer
        customer = Customer(
            name="Test Customer",
            email="test@example.com",
            company="Test Company", 
            segment="Enterprise"
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)
        
        # Prepare event data
        event_data = {
            "event_type": "api_call",
            "event_data": {
                "endpoint": "/api/test",
                "method": "GET",
                "response_code": 200
            }
        }
        
        # Make API request
        response = client.post(
            f"/api/customers/{customer.id}/events",
            json=event_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Event recorded successfully" in data["data"]["message"]
        assert data["data"]["customer_id"] == customer.id
        assert data["data"]["event_type"] == "api_call"
        
        # Verify event was created in database
        db_events = db_session.query(Event).filter_by(customer_id=customer.id).all()
        assert len(db_events) == 1
        assert db_events[0].event_type == "api_call"
    
    def test_record_customer_event_customer_not_found(self, client: TestClient, db_session: Session):
        """Test POST /api/customers/{id}/events for non-existent customer"""
        event_data = {
            "event_type": "login",
            "event_data": {}
        }
        
        response = client.post("/api/customers/999/events", json=event_data)
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "Customer not found" in data["detail"]
    
    def test_record_customer_event_minimal_data(self, client: TestClient, db_session: Session):
        """Test POST /api/customers/{id}/events with minimal data"""
        # Create test customer
        customer = Customer(
            name="Test Customer",
            email="test@example.com",
            company="Test Company",
            segment="SMB"
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)
        
        # Event with minimal data
        event_data = {
            "event_type": "login"
        }
        
        response = client.post(
            f"/api/customers/{customer.id}/events", 
            json=event_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["event_type"] == "login"
    
    def test_record_customer_event_with_timestamp(self, client: TestClient, db_session: Session):
        """Test POST /api/customers/{id}/events with custom timestamp"""
        # Create test customer
        customer = Customer(
            name="Test Customer",
            email="test@example.com",
            company="Test Company",
            segment="Startup"
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)
        
        # Event with custom timestamp
        custom_time = datetime.utcnow() - timedelta(hours=2)
        event_data = {
            "event_type": "feature_use",
            "event_data": {"feature": "dashboard"},
            "timestamp": custom_time.isoformat()
        }
        
        response = client.post(
            f"/api/customers/{customer.id}/events",
            json=event_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify timestamp was used
        db_event = db_session.query(Event).filter_by(customer_id=customer.id).first()
        assert db_event is not None
        assert abs((db_event.timestamp - custom_time).total_seconds()) < 1


class TestHealthCheckEndpoint:
    """Integration tests for health check endpoint"""
    
    def test_health_check_success(self, client: TestClient):
        """Test GET /health endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "healthy"
        assert "timestamp" in data["data"]


class TestRootEndpoint:
    """Integration tests for root endpoint"""
    
    def test_root_endpoint(self, client: TestClient):
        """Test GET / endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Customer Health Score API" in data["data"]["message"]
        assert "/docs" in data["data"]["docs"]


class TestErrorHandling:
    """Integration tests for error handling scenarios"""
    
    def test_server_error_handling(self, client: TestClient, db_session: Session):
        """Test server error handling with database issues"""
        # Close the database connection to simulate a database error
        db_session.close()
        
        response = client.get("/api/customers")
        
        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert "error" in data
        assert "Server error" in data["error"]
    
    def test_invalid_json_payload(self, client: TestClient, db_session: Session):
        """Test handling of invalid JSON payloads"""
        # Create test customer
        customer = Customer(
            name="Test Customer",
            email="test@example.com", 
            company="Test Company",
            segment="Enterprise"
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)
        
        # Send invalid JSON
        response = client.post(
            f"/api/customers/{customer.id}/events",
            data="invalid json"
        )
        
        # Should return 422 for validation error
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client: TestClient, db_session: Session):
        """Test handling of missing required fields"""
        # Create test customer
        customer = Customer(
            name="Test Customer",
            email="test@example.com",
            company="Test Company", 
            segment="Enterprise"
        )
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)
        
        # Send event without event_type
        response = client.post(
            f"/api/customers/{customer.id}/events",
            json={"event_data": {"test": "value"}}
        )
        
        # Should return 422 for validation error
        assert response.status_code == 422