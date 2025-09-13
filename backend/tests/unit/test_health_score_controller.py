"""
Unit tests for HealthScoreController
"""
import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

from domain.controllers.health_score_controller import HealthScoreController
from domain.exceptions import CustomerNotFoundError


class TestHealthScoreController:

    def test_get_customer_health_detail_success(self, memory_store_setup):
        """Test successful health detail retrieval with memory store"""
        controller = HealthScoreController(Mock())

        result = controller.get_customer_health_detail(1)

        assert result is not None
        assert "customer_id" in result
        assert "customer_name" in result
        assert "overall_score" in result
        assert "status" in result
        assert "factors" in result

    def test_get_customer_health_detail_not_found(self, memory_store_setup):
        """Test health detail retrieval for non-existent customer"""
        controller = HealthScoreController(Mock())

        with pytest.raises(CustomerNotFoundError):
            controller.get_customer_health_detail(999)

    def test_get_dashboard_statistics_fresh_data(self, memory_store_setup):
        """Test dashboard statistics with fresh data"""
        controller = HealthScoreController(Mock())

        result = controller.get_dashboard_statistics()

        assert "total_customers" in result
        assert "healthy_customers" in result
        assert "at_risk_customers" in result
        assert "critical_customers" in result
        assert "distribution" in result
        assert "last_updated" in result

        # Should have at least some customers from sample data
        assert result["total_customers"] >= 1

    def test_get_dashboard_statistics_percentage_calculation(self, memory_store_setup):
        """Test dashboard statistics percentage calculations"""
        controller = HealthScoreController(Mock())

        result = controller.get_dashboard_statistics()

        distribution = result["distribution"]
        assert "healthy_percent" in distribution
        assert "at_risk_percent" in distribution
        assert "critical_percent" in distribution

        # Percentages should be valid numbers
        total_percent = (
            distribution["healthy_percent"] +
            distribution["at_risk_percent"] +
            distribution["critical_percent"]
        )

        # Should add up to 100% (with some tolerance for rounding)
        assert abs(total_percent - 100.0) <= 1.0 or total_percent == 0

    def test_recalculate_all_health_scores(self, memory_store_setup):
        """Test recalculating all health scores with memory store"""
        controller = HealthScoreController(Mock())

        result = controller.recalculate_all_health_scores()

        # Should return number of processed customers
        assert isinstance(result, int)
        assert result >= 0