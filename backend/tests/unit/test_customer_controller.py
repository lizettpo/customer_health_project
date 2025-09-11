"""
Unit tests for CustomerController
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from domain.controllers.customer_controller import CustomerController
from domain.exceptions import CustomerNotFoundError


class TestCustomerController:
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock()
        self.controller = CustomerController(self.mock_db)
        
        # Mock repositories
        self.controller.customer_repo = Mock()
        self.controller.event_repo = Mock()
        self.controller.health_score_repo = Mock()
    
    def test_get_customers_with_health_scores_success(self):
        """Test successful retrieval of customers with health scores"""
        # Mock customer data
        mock_customer = Mock()
        mock_customer.id = 1
        mock_customer.name = "Test Customer"
        mock_customer.email = "test@example.com"
        mock_customer.company = "Test Co"
        mock_customer.segment = "Enterprise"
        mock_customer.created_at = datetime.utcnow()
        mock_customer.last_activity = datetime.utcnow()
        
        # Mock health score
        mock_health_score = Mock()
        mock_health_score.score = 85.0
        mock_health_score.status = "healthy"
        
        # Configure mocks
        self.controller.customer_repo.get_all.return_value = [mock_customer]
        self.controller.health_score_repo.get_latest_by_customer.return_value = mock_health_score
        
        result = self.controller.get_customers_with_health_scores(limit=10, offset=0)
        
        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["name"] == "Test Customer"
        assert result[0]["health_score"] == 85.0
        assert result[0]["health_status"] == "healthy"
    
    def test_get_customers_with_health_scores_by_status(self):
        """Test filtering customers by health status"""
        mock_customer = Mock()
        mock_customer.id = 1
        mock_customer.name = "At Risk Customer"
        mock_customer.email = "risk@example.com"
        mock_customer.company = "Risk Co"
        mock_customer.segment = "SMB"
        mock_customer.created_at = datetime.utcnow()
        mock_customer.last_activity = datetime.utcnow()
        
        mock_health_score = Mock()
        mock_health_score.score = 55.0
        mock_health_score.status = "at_risk"
        
        self.controller.customer_repo.get_by_health_status.return_value = [mock_customer]
        self.controller.health_score_repo.get_latest_by_customer.return_value = mock_health_score
        
        result = self.controller.get_customers_with_health_scores(health_status="at_risk")
        
        assert len(result) == 1
        assert result[0]["health_status"] == "at_risk"
        self.controller.customer_repo.get_by_health_status.assert_called_once_with("at_risk")
    
    def test_get_customers_with_no_health_score(self):
        """Test handling customers without health scores"""
        mock_customer = Mock()
        mock_customer.id = 1
        mock_customer.name = "New Customer"
        mock_customer.email = "new@example.com"
        mock_customer.company = "New Co"
        mock_customer.segment = "Startup"
        mock_customer.created_at = datetime.utcnow()
        mock_customer.last_activity = datetime.utcnow()
        
        self.controller.customer_repo.get_all.return_value = [mock_customer]
        self.controller.health_score_repo.get_latest_by_customer.return_value = None
        
        result = self.controller.get_customers_with_health_scores()
        
        assert len(result) == 1
        assert result[0]["health_score"] == 0
        assert result[0]["health_status"] == "unknown"
    
    def test_get_customer_by_id_success(self):
        """Test successful customer retrieval by ID"""
        mock_customer = Mock()
        mock_customer.id = 1
        mock_customer.name = "Test Customer"
        
        self.controller.customer_repo.get_by_id.return_value = mock_customer
        
        result = self.controller.get_customer_by_id(1)
        
        assert result == mock_customer
        self.controller.customer_repo.get_by_id.assert_called_once_with(1)
    
    def test_get_customer_by_id_not_found(self):
        """Test customer not found scenario"""
        self.controller.customer_repo.get_by_id.return_value = None
        
        with pytest.raises(CustomerNotFoundError, match="Customer 999 not found"):
            self.controller.get_customer_by_id(999)
    
    def test_record_customer_event_success(self):
        """Test successful event recording"""
        mock_customer = Mock()
        mock_customer.id = 1
        mock_customer.name = "Test Customer"
        
        mock_event = Mock()
        mock_event.id = 1
        mock_event.timestamp = datetime.utcnow()
        
        self.controller.customer_repo.get_by_id.return_value = mock_customer
        self.controller.event_repo.create_event.return_value = mock_event
        
        result = self.controller.record_customer_event(
            customer_id=1,
            event_type="api_call",
            event_data={"endpoint": "/test"}
        )
        
        assert result["customer_id"] == 1
        assert result["customer_name"] == "Test Customer"
        assert result["event_type"] == "api_call"
        assert "Event recorded successfully" in result["message"]
        
        self.controller.event_repo.create_event.assert_called_once()
        self.controller.customer_repo.update_last_activity.assert_called_once()
    
    def test_record_customer_event_customer_not_found(self):
        """Test event recording with non-existent customer"""
        self.controller.customer_repo.get_by_id.return_value = None
        
        with pytest.raises(CustomerNotFoundError):
            self.controller.record_customer_event(
                customer_id=999,
                event_type="api_call"
            )
    
    def test_get_customer_with_events_success(self):
        """Test getting customer with events"""
        mock_customer = Mock()
        mock_customer.id = 1
        mock_customer.name = "Test Customer"
        mock_customer.email = "test@example.com"
        mock_customer.company = "Test Co"
        mock_customer.segment = "Enterprise"
        
        mock_events = [Mock(), Mock(), Mock()]
        mock_events[0].event_type = "api_call"
        mock_events[1].event_type = "login"
        mock_events[2].event_type = "api_call"
        
        self.controller.customer_repo.get_by_id.return_value = mock_customer
        self.controller.event_repo.get_recent_events.return_value = mock_events
        
        result = self.controller.get_customer_with_events(1, days=30)
        
        assert result["customer"]["id"] == 1
        assert result["events_summary"]["total_events"] == 3
        assert "api_call" in result["events_summary"]["events_by_type"]
        assert "login" in result["events_summary"]["events_by_type"]
        assert result["events_summary"]["events_by_type"]["api_call"] == 2
        assert result["events_summary"]["events_by_type"]["login"] == 1
    
    def test_get_customer_count(self):
        """Test getting customer count"""
        self.controller.customer_repo.count.return_value = 42
        
        result = self.controller.get_customer_count()
        
        assert result == 42
        self.controller.customer_repo.count.assert_called_once()
    
    def test_singleton_pattern(self):
        """Test that CustomerController follows singleton pattern"""
        controller1 = CustomerController(self.mock_db)
        controller2 = CustomerController(self.mock_db)
        
        assert controller1 is controller2