"""
Unit tests for HealthScoreService
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from services.health_score_service import HealthScoreService


class TestHealthScoreService:
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock()
        self.service = HealthScoreService(self.mock_db)
        
        # Mock the controller
        self.service.health_score_controller = Mock()
    
    def test_get_customer_health_detail(self):
        """Test getting customer health detail"""
        mock_health_detail = {
            "customer_id": 1,
            "customer_name": "Test Customer",
            "overall_score": 85.0,
            "status": "healthy",
            "factors": {
                "api_usage": {
                    "score": 90.0,
                    "value": 1000,
                    "description": "High API usage"
                },
                "login_frequency": {
                    "score": 80.0,
                    "value": 25,
                    "description": "Good login frequency"
                }
            },
            "calculated_at": datetime.utcnow(),
            "recommendations": ["Keep up the good work"],
            "data_summary": {
                "events_analyzed": 100,
                "customer_segment": "Enterprise"
            }
        }
        
        self.service.health_score_controller.get_customer_health_detail.return_value = mock_health_detail
        
        result = self.service.get_customer_health_detail(1)
        
        assert result == mock_health_detail
        self.service.health_score_controller.get_customer_health_detail.assert_called_once_with(1)
    
    def test_calculate_and_save_health_score(self):
        """Test calculating and saving health score"""
        mock_result = {
            "customer_id": 1,
            "score": 75.0,
            "status": "healthy",
            "calculated_at": datetime.utcnow()
        }
        
        self.service.health_score_controller.calculate_and_save_health_score.return_value = mock_result
        
        result = self.service.calculate_and_save_health_score(1)
        
        assert result == mock_result
        self.service.health_score_controller.calculate_and_save_health_score.assert_called_once_with(1)
    
    def test_get_dashboard_stats(self):
        """Test getting dashboard statistics"""
        mock_stats = {
            "total_customers": 100,
            "healthy_customers": 60,
            "at_risk_customers": 30,
            "critical_customers": 10,
            "average_health_score": 72.5,
            "health_coverage_percentage": 100.0,
            "distribution": {
                "healthy_percent": 60.0,
                "at_risk_percent": 30.0,
                "critical_percent": 10.0
            },
            "last_updated": datetime.utcnow()
        }
        
        self.service.health_score_controller.get_dashboard_statistics.return_value = mock_stats
        
        result = self.service.get_dashboard_stats()
        
        assert result == mock_stats
        self.service.health_score_controller.get_dashboard_statistics.assert_called_once()
    

    # =========================
    # SAD PATH / ERROR SCENARIOS
    # =========================
    
    def test_get_customer_health_detail_not_found(self):
        """Test getting health detail for non-existent customer"""
        from domain.exceptions import CustomerNotFoundError
        self.service.health_score_controller.get_customer_health_detail.side_effect = CustomerNotFoundError(999)
        
        with pytest.raises(CustomerNotFoundError):
            self.service.get_customer_health_detail(999)
    
    def test_get_customer_health_detail_invalid_id_type(self):
        """Test getting health detail with invalid customer ID type"""
        # Service passes through to controller - let controller handle validation
        self.service.health_score_controller.get_customer_health_detail.return_value = None
        
        result = self.service.get_customer_health_detail("invalid_id")
        
        # Service should call controller with the invalid parameter
        self.service.health_score_controller.get_customer_health_detail.assert_called_once_with("invalid_id")
    
    def test_calculate_and_save_health_score_not_found(self):
        """Test calculating health score for non-existent customer"""
        from domain.exceptions import CustomerNotFoundError
        self.service.health_score_controller.calculate_and_save_health_score.side_effect = CustomerNotFoundError(999)
        
        with pytest.raises(CustomerNotFoundError):
            self.service.calculate_and_save_health_score(999)
    
    def test_calculate_and_save_health_score_calculation_error(self):
        """Test error during health score calculation"""
        from domain.exceptions import InvalidHealthScoreError
        self.service.health_score_controller.calculate_and_save_health_score.side_effect = InvalidHealthScoreError(150.0, "Score out of range")
        
        with pytest.raises(InvalidHealthScoreError):
            self.service.calculate_and_save_health_score(1)
    
    def test_get_dashboard_stats_database_error(self):
        """Test dashboard stats with database error"""
        from domain.exceptions import DatabaseError, DataErrorCode
        self.service.health_score_controller.get_dashboard_statistics.side_effect = DatabaseError("query", "health_scores", DataErrorCode.DATABASE_CONNECTION_FAILED)
        
        with pytest.raises(DatabaseError):
            self.service.get_dashboard_stats()
    
    def test_get_dashboard_stats_empty_database(self):
        """Test dashboard stats with empty database"""
        empty_stats = {
            "total_customers": 0,
            "healthy_customers": 0,
            "at_risk_customers": 0,
            "critical_customers": 0,
            "average_health_score": 0.0,
            "health_coverage_percentage": 0.0
        }
        self.service.health_score_controller.get_dashboard_statistics.return_value = empty_stats
        
        result = self.service.get_dashboard_stats()
        
        assert result == empty_stats
        assert result["total_customers"] == 0
        assert result["average_health_score"] == 0.0