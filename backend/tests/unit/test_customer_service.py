"""
Unit tests for CustomerService
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from services.customer_service import CustomerService


class TestCustomerService:
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock()
        self.service = CustomerService(self.mock_db)
        
        # Mock the controller
        self.service.customer_controller = Mock()
    
    def test_get_customers_with_health_scores(self):
        """Test getting customers with health scores"""
        mock_customers = [
            {
                "id": 1,
                "name": "Customer 1",
                "health_score": 85.0,
                "health_status": "healthy"
            },
            {
                "id": 2,
                "name": "Customer 2", 
                "health_score": 60.0,
                "health_status": "at_risk"
            }
        ]
        
        self.service.customer_controller.get_customers_with_health_scores.return_value = mock_customers
        
        result = self.service.get_customers_with_health_scores(limit=10, offset=0)
        
        assert result == mock_customers
        self.service.customer_controller.get_customers_with_health_scores.assert_called_once_with(
            limit=10, offset=0, health_status=None
        )
    
    def test_get_customers_with_health_scores_filtered(self):
        """Test getting customers filtered by health status"""
        mock_customers = [
            {
                "id": 1,
                "name": "At Risk Customer",
                "health_score": 55.0,
                "health_status": "at_risk"
            }
        ]
        
        self.service.customer_controller.get_customers_with_health_scores.return_value = mock_customers
        
        result = self.service.get_customers_with_health_scores(
            limit=20, 
            offset=5, 
            health_status="at_risk"
        )
        
        assert result == mock_customers
        self.service.customer_controller.get_customers_with_health_scores.assert_called_once_with(
            limit=20, offset=5, health_status="at_risk"
        )
    
    def test_get_customer_by_id(self):
        """Test getting customer by ID"""
        mock_customer = Mock()
        mock_customer.id = 1
        mock_customer.name = "Test Customer"
        
        self.service.customer_controller.get_customer_by_id.return_value = mock_customer
        
        result = self.service.get_customer_by_id(1)
        
        assert result == mock_customer
        self.service.customer_controller.get_customer_by_id.assert_called_once_with(1)
    
    def test_record_event(self):
        """Test recording customer event"""
        mock_response = {
            "message": "Event recorded successfully",
            "event_id": 123,
            "customer_id": 1,
            "event_type": "api_call"
        }
        
        self.service.customer_controller.record_customer_event.return_value = mock_response
        
        timestamp = datetime.utcnow()
        result = self.service.record_event(
            customer_id=1,
            event_type="api_call",
            event_data={"endpoint": "/test"},
            timestamp=timestamp
        )
        
        assert result == mock_response
        self.service.customer_controller.record_customer_event.assert_called_once_with(
            customer_id=1,
            event_type="api_call",
            event_data={"endpoint": "/test"},
            timestamp=timestamp
        )
    
    def test_record_event_minimal_params(self):
        """Test recording event with minimal parameters"""
        mock_response = {
            "message": "Event recorded successfully",
            "event_id": 124,
            "customer_id": 2,
            "event_type": "login"
        }
        
        self.service.customer_controller.record_customer_event.return_value = mock_response
        
        result = self.service.record_event(
            customer_id=2,
            event_type="login"
        )
        
        assert result == mock_response
        self.service.customer_controller.record_customer_event.assert_called_once_with(
            customer_id=2,
            event_type="login",
            event_data=None,
            timestamp=None
        )
    
    def test_get_customer_events(self):
        """Test getting customer events"""
        mock_events = {
            "customer": {"id": 1, "name": "Test Customer"},
            "events_summary": {
                "total_events": 5,
                "events_by_type": {"api_call": 3, "login": 2}
            }
        }
        
        self.service.customer_controller.get_customer_events.return_value = mock_events
        
        result = self.service.get_customer_events(1, days=30)
        
        assert result == mock_events
        self.service.customer_controller.get_customer_events.assert_called_once_with(1, 30)
    
    def test_get_customer_events_default_days(self):
        """Test getting customer events with default days parameter"""
        mock_events = {
            "customer": {"id": 1, "name": "Test Customer"},
            "events_summary": {"total_events": 10}
        }
        
        self.service.customer_controller.get_customer_events.return_value = mock_events
        
        result = self.service.get_customer_events(1)
        
        assert result == mock_events
        self.service.customer_controller.get_customer_events.assert_called_once_with(1, 90)
    
    def test_singleton_pattern(self):
        """Test that CustomerService follows singleton pattern"""
        service1 = CustomerService(self.mock_db)
        service2 = CustomerService(self.mock_db)
        
        assert service1 is service2

    # =========================
    # SAD PATH / ERROR SCENARIOS
    # =========================
    
    def test_get_customers_with_health_scores_database_error(self):
        """Test error handling when database fails"""
        from domain.exceptions import DatabaseError, DataErrorCode
        self.service.customer_controller.get_customers_with_health_scores.side_effect = DatabaseError("query", "customers", DataErrorCode.DATABASE_CONNECTION_FAILED)
        
        with pytest.raises(DatabaseError):
            self.service.get_customers_with_health_scores()
    
    def test_get_customers_with_invalid_pagination(self):
        """Test handling of invalid pagination parameters"""
        # Service should pass through invalid params to controller for validation
        self.service.customer_controller.get_customers_with_health_scores.return_value = []
        
        result = self.service.get_customers_with_health_scores(limit=-1, offset=-10)
        
        # Controller should be called with invalid params (let controller handle validation)
        self.service.customer_controller.get_customers_with_health_scores.assert_called_once_with(
            limit=-1, offset=-10, health_status=None
        )
    
    def test_get_customer_by_id_not_found(self):
        """Test getting non-existent customer"""
        from domain.exceptions import CustomerNotFoundError
        self.service.customer_controller.get_customer_by_id.side_effect = CustomerNotFoundError(999)
        
        with pytest.raises(CustomerNotFoundError):
            self.service.get_customer_by_id(999)
    
    def test_get_customer_by_id_invalid_type(self):
        """Test getting customer with invalid ID type"""
        # Service passes through to controller - let controller handle validation
        self.service.customer_controller.get_customer_by_id.return_value = None
        
        result = self.service.get_customer_by_id("invalid_id")
        
        # Service should call controller with the invalid parameter
        self.service.customer_controller.get_customer_by_id.assert_called_once_with("invalid_id")
    
    def test_record_event_invalid_customer(self):
        """Test recording event for non-existent customer"""
        from domain.exceptions import CustomerNotFoundError
        self.service.customer_controller.record_customer_event.side_effect = CustomerNotFoundError(999)
        
        with pytest.raises(CustomerNotFoundError):
            self.service.record_event(999, "login")
    
    def test_record_event_empty_event_type(self):
        """Test recording event with empty event type"""
        # Service should pass through to controller for validation
        self.service.customer_controller.record_customer_event.return_value = {"success": True}
        
        result = self.service.record_event(1, "")
        
        self.service.customer_controller.record_customer_event.assert_called_once_with(
            customer_id=1, event_type="", event_data=None, timestamp=None
        )
    
    def test_record_event_none_event_type(self):
        """Test recording event with None event type"""
        # Service should pass through to controller for validation
        self.service.customer_controller.record_customer_event.return_value = {"success": True}
        
        result = self.service.record_event(1, None)
        
        self.service.customer_controller.record_customer_event.assert_called_once_with(
            customer_id=1, event_type=None, event_data=None, timestamp=None
        )
    
    def test_record_event_invalid_event_data(self):
        """Test recording event with invalid event data structure"""
        # Test with non-dict event data
        invalid_data = "not_a_dict"
        self.service.customer_controller.record_customer_event.return_value = {"success": True}
        
        # Service should pass through - let controller validate
        result = self.service.record_event(1, "login", invalid_data)
        
        self.service.customer_controller.record_customer_event.assert_called_once_with(
            customer_id=1, event_type="login", event_data=invalid_data, timestamp=None
        )
    
    def test_get_customer_events_invalid_customer(self):
        """Test getting events for non-existent customer"""
        from domain.exceptions import CustomerNotFoundError
        self.service.customer_controller.get_customer_events.side_effect = CustomerNotFoundError(999)
        
        with pytest.raises(CustomerNotFoundError):
            self.service.get_customer_events(999)
    
    def test_get_customer_events_negative_days(self):
        """Test getting events with negative days parameter"""
        self.service.customer_controller.get_customer_events.return_value = []
        
        result = self.service.get_customer_events(1, days=-30)
        
        # Service should pass through negative days to controller
        self.service.customer_controller.get_customer_events.assert_called_once_with(1, -30)
    
    def test_get_customer_events_zero_days(self):
        """Test getting events with zero days parameter"""
        self.service.customer_controller.get_customer_events.return_value = []
        
        result = self.service.get_customer_events(1, days=0)
        
        self.service.customer_controller.get_customer_events.assert_called_once_with(1, 0)
        assert result == []