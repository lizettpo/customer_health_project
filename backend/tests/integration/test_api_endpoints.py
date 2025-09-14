"""
Integration tests for API endpoints
Tests the complete flow from API request to database using memory store
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

from data.models import Customer, CustomerEvent, HealthScore
from schemas import CustomerEventCreate


class TestCustomerEndpoints:
    """Integration tests for customer-related endpoints"""

    def test_get_customers_success(self, client: TestClient, memory_store_setup):
        """Test GET /api/customers endpoint with memory store"""
        # Make API request (data comes from memory store setup)
        response = client.get("/api/customers")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert len(data["data"]) >= 1

    def test_get_customers_filtered_by_health_status(self, client: TestClient, memory_store_setup):
        """Test GET /api/customers with health status filter"""
        # Test filtering by health status
        response = client.get("/api/customers?health_status=healthy")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        # All returned customers should have healthy status
        for customer in data["data"]:
            assert customer["health_status"] == "healthy"

    def test_get_customers_empty_result(self, client: TestClient, db_session: Session, clean_db):
        """Test GET /api/customers with no customers"""
        # Initialize empty memory store for this test
        from domain.memory_store import memory_store
        memory_store.customers.clear()
        memory_store.health_scores.clear()
        memory_store.events.clear()

        response = client.get("/api/customers")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"] == []


class TestHealthScoreEndpoints:
    """Integration tests for health score endpoints"""

    def test_get_customer_health_detail_success(self, client: TestClient, memory_store_setup):
        """Test GET /api/customers/{id}/health endpoint"""
        # Test with customer ID 1 (should exist in memory store)
        response = client.get("/api/customers/1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        health_data = data["data"]
        assert "customer_id" in health_data
        assert "overall_score" in health_data
        assert "status" in health_data
        assert "factors" in health_data

    def test_get_customer_health_detail_not_found(self, client: TestClient, memory_store_setup):
        """Test GET /api/customers/{id}/health with non-existent customer"""
        response = client.get("/api/customers/999/health")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["detail"].lower()

    def test_get_dashboard_stats_success(self, client: TestClient, memory_store_setup):
        """Test GET /api/dashboard/stats endpoint"""
        response = client.get("/api/dashboard/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

        stats = data["data"]
        assert "total_customers" in stats
        assert "healthy_customers" in stats
        assert "at_risk_customers" in stats
        assert "critical_customers" in stats
        assert "distribution" in stats

        # Should have at least some customers
        assert stats["total_customers"] >= 1

    def test_get_dashboard_stats_empty(self, client: TestClient, db_session: Session, clean_db):
        """Test GET /api/dashboard/stats with no customers"""
        # Initialize empty memory store for this test
        from domain.memory_store import memory_store
        memory_store.customers.clear()
        memory_store.health_scores.clear()
        memory_store.events.clear()

        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        stats = data["data"]
        assert stats["total_customers"] == 0


class TestEventEndpoints:
    """Integration tests for event recording endpoints"""

    def test_record_customer_event_success(self, client: TestClient, memory_store_setup):
        """Test POST /api/customers/{id}/events endpoint"""
        event_data = {
            "event_type": "api_call",
            "event_data": {
                "endpoint": "/api/test",
                "method": "GET",
                "response_code": 200
            }
        }

        response = client.post("/api/customers/1/events", json=event_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        result = data["data"]
        assert result["customer_id"] == 1
        assert result["event_type"] == "api_call"
        assert "Event recorded successfully" in result["message"] or "recorded successfully" in result["message"]

    def test_record_customer_event_customer_not_found(self, client: TestClient, memory_store_setup):
        """Test POST /api/customers/{id}/events with non-existent customer"""
        event_data = {
            "event_type": "api_call",
            "event_data": {
                "endpoint": "/api/test"
            }
        }

        response = client.post("/api/customers/999/events", json=event_data)
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False

    def test_record_customer_event_minimal_data(self, client: TestClient, memory_store_setup):
        """Test POST /api/customers/{id}/events with minimal valid data"""
        event_data = {
            "event_type": "support_ticket",
            "event_data": {}  # Support tickets have no required fields
        }

        response = client.post("/api/customers/1/events", json=event_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        result = data["data"]
        assert result["customer_id"] == 1
        assert result["event_type"] == "support_ticket"

    def test_record_customer_event_with_timestamp(self, client: TestClient, memory_store_setup):
        """Test POST /api/customers/{id}/events with custom timestamp"""
        custom_time = datetime.utcnow() - timedelta(hours=1)
        event_data = {
            "event_type": "login",
            "event_data": {
                "ip_address": "192.168.1.1"
            },
            "timestamp": custom_time.isoformat()
        }

        response = client.post("/api/customers/1/events", json=event_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        result = data["data"]
        assert result["customer_id"] == 1
        assert result["event_type"] == "login"

    def test_record_customer_event_invalid_data(self, client: TestClient, memory_store_setup):
        """Test POST /api/customers/{id}/events with invalid event data"""
        event_data = {
            "event_type": "api_call",
            "event_data": {}  # Missing required 'endpoint' field
        }

        response = client.post("/api/customers/1/events", json=event_data)
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "Invalid event data" in data["error"]

    def test_record_customer_event_malformed_json(self, client: TestClient, memory_store_setup):
        """Test POST /api/customers/{id}/events with malformed request"""
        # Send invalid JSON
        response = client.post("/api/customers/1/events",
                             data="invalid json",
                             headers={"Content-Type": "application/json"})

        assert response.status_code == 422  # FastAPI validation error