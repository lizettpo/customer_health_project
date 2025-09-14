"""
Unit tests for CustomerController
"""
import pytest
from unittest.mock import Mock
from datetime import datetime

from domain.controllers.customer_controller import CustomerController
from domain.exceptions import CustomerNotFoundError, InvalidEventDataError


class TestCustomerController:

    def test_get_customers_with_health_scores_success(self, memory_store_setup):
        """Test successful retrieval of customers with memory store"""
        controller = CustomerController(Mock())
        result = controller.get_customers_with_health_scores()

        assert len(result) >= 1
        assert "id" in result[0]
        assert "name" in result[0]
        assert "health_score" in result[0]
        assert "health_status" in result[0]

    def test_get_customers_with_health_scores_by_status(self, memory_store_setup):
        """Test filtering customers by health status with memory store"""
        controller = CustomerController(Mock())
        result = controller.get_customers_with_health_scores(health_status="healthy")

        # Should return customers, might be 0 depending on sample data
        assert isinstance(result, list)
        for customer in result:
            assert customer["health_status"] == "healthy"

    def test_get_customers_with_no_health_score(self, memory_store_setup):
        """Test handling customers without health scores with memory store"""
        controller = CustomerController(Mock())
        result = controller.get_customers_with_health_scores()

        # Should return customers from memory store
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_get_customer_by_id_success(self, memory_store_setup):
        """Test successful customer retrieval by ID with memory store"""
        controller = CustomerController(Mock())

        # Assuming sample data has at least one customer with ID 1
        result = controller.get_customer_by_id(1)

        assert result is not None
        assert result.id == 1

    def test_get_customer_by_id_not_found(self, memory_store_setup):
        """Test customer not found scenario"""
        controller = CustomerController(Mock())

        with pytest.raises(CustomerNotFoundError, match="Customer 999 not found"):
            controller.get_customer_by_id(999)

    def test_record_customer_event_success(self, memory_store_setup):
        """Test successful event recording with memory store"""
        controller = CustomerController(Mock())

        result = controller.record_customer_event(
            customer_id=1,
            event_type="api_call",
            event_data={"endpoint": "/test"}
        )

        assert result["customer_id"] == 1
        assert "customer_name" in result
        assert result["event_type"] == "api_call"
        assert "Event recorded successfully" in result["message"] or "recorded successfully" in result["message"]

    def test_record_customer_event_customer_not_found(self, memory_store_setup):
        """Test event recording with non-existent customer"""
        controller = CustomerController(Mock())

        with pytest.raises(CustomerNotFoundError, match="Customer 999 not found"):
            controller.record_customer_event(
                customer_id=999,
                event_type="api_call",
                event_data={"endpoint": "/test"}  # Valid data to pass validation
            )

    def test_get_customer_events_success(self, memory_store_setup):
        """Test getting customer events from memory store"""
        controller = CustomerController(Mock())

        result = controller.get_customer_events(1, days=30)

        assert isinstance(result, list)
        # Events might be empty for new customer, but should be a valid list

    def test_get_customer_events_customer_not_found(self, memory_store_setup):
        """Test getting events for non-existent customer"""
        controller = CustomerController(Mock())

        with pytest.raises(CustomerNotFoundError, match="Customer 999 not found"):
            controller.get_customer_events(999)

    # Validation tests still work with instance methods
    def test_validate_event_data_api_call_valid(self):
        """Test validation passes for valid API call event"""
        controller = CustomerController(Mock())
        # Should not raise exception
        controller._validate_event_data("api_call", {"endpoint": "/api/test"})

    def test_validate_event_data_api_call_missing_endpoint(self):
        """Test validation fails when API call missing endpoint"""
        controller = CustomerController(Mock())
        with pytest.raises(InvalidEventDataError):
            controller._validate_event_data("api_call", {})

    def test_validate_event_data_api_call_empty_endpoint(self):
        """Test validation fails when API call has empty endpoint"""
        controller = CustomerController(Mock())
        with pytest.raises(InvalidEventDataError):
            controller._validate_event_data("api_call", {"endpoint": ""})

    def test_validate_event_data_api_call_whitespace_endpoint(self):
        """Test validation fails when API call has whitespace-only endpoint"""
        controller = CustomerController(Mock())
        with pytest.raises(InvalidEventDataError):
            controller._validate_event_data("api_call", {"endpoint": "   "})

    def test_validate_event_data_payment_valid(self):
        """Test validation passes for valid payment event"""
        controller = CustomerController(Mock())
        controller._validate_event_data("payment", {"amount": 100.50})

    def test_validate_event_data_payment_missing_amount(self):
        """Test validation fails when payment missing amount"""
        controller = CustomerController(Mock())
        with pytest.raises(InvalidEventDataError):
            controller._validate_event_data("payment", {})

    def test_validate_event_data_payment_zero_amount(self):
        """Test validation fails when payment amount is zero"""
        controller = CustomerController(Mock())
        with pytest.raises(InvalidEventDataError):
            controller._validate_event_data("payment", {"amount": 0})

    def test_validate_event_data_payment_negative_amount(self):
        """Test validation fails when payment amount is negative"""
        controller = CustomerController(Mock())
        with pytest.raises(InvalidEventDataError):
            controller._validate_event_data("payment", {"amount": -50})

    def test_validate_event_data_payment_invalid_amount(self):
        """Test validation fails when payment amount is not a number"""
        controller = CustomerController(Mock())
        with pytest.raises(InvalidEventDataError):
            controller._validate_event_data("payment", {"amount": "invalid"})

    def test_validate_event_data_feature_use_valid(self):
        """Test validation passes for valid feature use event"""
        controller = CustomerController(Mock())
        controller._validate_event_data("feature_use", {"feature_name": "dashboard"})

    def test_validate_event_data_feature_use_missing_feature_name(self):
        """Test validation fails when feature use missing feature_name"""
        controller = CustomerController(Mock())
        with pytest.raises(InvalidEventDataError):
            controller._validate_event_data("feature_use", {})

    def test_validate_event_data_login_valid(self):
        """Test validation passes for valid login event"""
        controller = CustomerController(Mock())
        controller._validate_event_data("login", {"ip_address": "192.168.1.1"})

    def test_validate_event_data_login_missing_ip_address(self):
        """Test validation fails when login missing ip_address"""
        controller = CustomerController(Mock())
        with pytest.raises(InvalidEventDataError):
            controller._validate_event_data("login", {})

    def test_validate_event_data_support_ticket_valid(self):
        """Test validation passes for support ticket event (no required fields)"""
        controller = CustomerController(Mock())
        controller._validate_event_data("support_ticket", {})
        controller._validate_event_data("support_ticket", {"priority": "high"})

    def test_validate_event_data_unknown_event_type(self):
        """Test validation passes for unknown event types (no validation)"""
        controller = CustomerController(Mock())
        controller._validate_event_data("unknown_type", {})

    def test_record_customer_event_with_validation_failure(self, memory_store_setup):
        """Test event recording fails validation before customer lookup"""
        controller = CustomerController(Mock())

        # Should fail validation before even checking customer exists
        with pytest.raises(InvalidEventDataError):
            controller.record_customer_event(
                customer_id=1,
                event_type="api_call",
                event_data={}
            )