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
            "historical_scores": [
                {"score": 83.0, "status": "healthy", "calculated_at": datetime.utcnow()},
                {"score": 81.0, "status": "healthy", "calculated_at": datetime.utcnow()}
            ],
            "recommendations": ["Keep up the good work"],
            "data_summary": {
                "events_analyzed": 100,
                "history_points": 30,
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
    
    def test_singleton_pattern(self):
        """Test that HealthScoreService follows singleton pattern"""
        service1 = HealthScoreService(self.mock_db)
        service2 = HealthScoreService(self.mock_db)
        
        assert service1 is service2