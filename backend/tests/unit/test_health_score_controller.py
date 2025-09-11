"""
Unit tests for HealthScoreController
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from domain.controllers.health_score_controller import HealthScoreController
from domain.exceptions import CustomerNotFoundError


class TestHealthScoreController:
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock()
        self.controller = HealthScoreController(self.mock_db)
        
        # Mock repositories and calculator
        self.controller.customer_repo = Mock()
        self.controller.event_repo = Mock()
        self.controller.health_score_repo = Mock()
        self.controller.calculator = Mock()
    
    def test_get_customer_health_detail_success(self):
        """Test successful health detail retrieval"""
        # Mock customer
        mock_customer = Mock()
        mock_customer.id = 1
        mock_customer.name = "Test Customer"
        mock_customer.segment = "Enterprise"
        
        # Mock events
        mock_events = [Mock(), Mock()]
        
        # Mock calculated health score
        mock_health_score = Mock()
        mock_health_score.score = 85.0
        mock_health_score.status = "healthy"
        mock_health_score.calculated_at = datetime.utcnow()
        mock_health_score.factors = {
            "api_usage": Mock(score=90.0, value=1000, description="High usage", trend="up", metadata={}),
            "login_frequency": Mock(score=80.0, value=25, description="Good engagement", trend="stable", metadata={})
        }
        mock_health_score.recommendations = ["Keep up the good work"]
        
        # Mock historical scores
        mock_historical = [Mock(), Mock()]
        mock_historical[0].score = 83.0
        mock_historical[0].status = "healthy"
        mock_historical[0].calculated_at = datetime.utcnow() - timedelta(days=1)
        mock_historical[1].score = 81.0
        mock_historical[1].status = "healthy"
        mock_historical[1].calculated_at = datetime.utcnow() - timedelta(days=2)
        
        # Configure mocks
        self.controller.customer_repo.get_by_id.return_value = mock_customer
        self.controller.event_repo.get_recent_events.return_value = mock_events
        self.controller.calculator.calculate_health_score.return_value = mock_health_score
        self.controller.health_score_repo.save_health_score.return_value = mock_health_score
        self.controller.health_score_repo.get_historical_scores.return_value = mock_historical
        
        result = self.controller.get_customer_health_detail(1)
        
        assert result["customer_id"] == 1
        assert result["customer_name"] == "Test Customer"
        assert result["overall_score"] == 85.0
        assert result["status"] == "healthy"
        assert "api_usage" in result["factors"]
        assert "login_frequency" in result["factors"]
        assert len(result["historical_scores"]) == 2
        assert result["data_summary"]["events_analyzed"] == 2
        assert result["data_summary"]["customer_segment"] == "Enterprise"
    
    def test_get_customer_health_detail_customer_not_found(self):
        """Test health detail retrieval for non-existent customer"""
        self.controller.customer_repo.get_by_id.return_value = None
        
        with pytest.raises(CustomerNotFoundError, match="Customer 999 not found"):
            self.controller.get_customer_health_detail(999)
    
    def test_get_dashboard_statistics_fresh_data(self):
        """Test dashboard statistics without cache"""
        # Clear cache
        self.controller._dashboard_data = None
        self.controller._last_dashboard_load = None
        
        # Mock repository responses
        self.controller.customer_repo.count.return_value = 100
        self.controller.health_score_repo.count_by_status.side_effect = [60, 30, 10]  # healthy, at_risk, critical
        self.controller.health_score_repo.get_average_score.return_value = 72.5
        
        result = self.controller.get_dashboard_statistics()
        
        assert result["total_customers"] == 100
        assert result["healthy_customers"] == 60
        assert result["at_risk_customers"] == 30
        assert result["critical_customers"] == 10
        assert result["average_health_score"] == 72.5
        assert result["health_coverage_percentage"] == 100.0
        assert result["distribution"]["healthy_percent"] == 60.0
        assert result["distribution"]["at_risk_percent"] == 30.0
        assert result["distribution"]["critical_percent"] == 10.0
    
    def test_get_dashboard_statistics_cached_data(self):
        """Test dashboard statistics with cached data"""
        # Set up cached data (less than 5 minutes old)
        cached_data = {
            "total_customers": 50,
            "healthy_customers": 30,
            "average_health_score": 75.0
        }
        self.controller._dashboard_data = cached_data
        self.controller._last_dashboard_load = datetime.utcnow() - timedelta(minutes=2)
        
        result = self.controller.get_dashboard_statistics()
        
        # Should return cached data without calling repositories
        assert result == cached_data
        self.controller.customer_repo.count.assert_not_called()
    
    def test_get_dashboard_statistics_expired_cache(self):
        """Test dashboard statistics with expired cache"""
        # Set up expired cached data (more than 5 minutes old)
        self.controller._dashboard_data = {"old": "data"}
        self.controller._last_dashboard_load = datetime.utcnow() - timedelta(minutes=10)
        
        # Mock fresh data
        self.controller.customer_repo.count.return_value = 80
        self.controller.health_score_repo.count_by_status.side_effect = [50, 20, 10]
        self.controller.health_score_repo.get_average_score.return_value = 70.0
        
        result = self.controller.get_dashboard_statistics()
        
        # Should fetch fresh data
        assert result["total_customers"] == 80
        assert result["healthy_customers"] == 50
        self.controller.customer_repo.count.assert_called_once()
    
    def test_bulk_calculate_health_scores_success(self):
        """Test bulk health score calculation"""
        customer_ids = [1, 2, 3]
        
        # Mock customers
        mock_customers = {}
        for i, cid in enumerate(customer_ids):
            customer = Mock()
            customer.id = cid
            customer.name = f"Customer {cid}"
            mock_customers[cid] = customer
        
        # Mock events
        mock_events = {1: [Mock()], 2: [Mock(), Mock()], 3: []}
        
        # Mock calculated scores
        mock_scores = []
        for cid in customer_ids:
            score = Mock()
            score.score = 70.0 + cid
            score.status = "healthy"
            mock_scores.append(score)
        
        # Configure mocks
        def get_by_id_side_effect(customer_id):
            return mock_customers.get(customer_id)
        
        def get_recent_events_side_effect(customer_id, days):
            return mock_events.get(customer_id, [])
        
        def calculate_side_effect(customer, events):
            return mock_scores[customer.id - 1]
        
        def save_side_effect(health_score):
            return health_score
        
        self.controller.customer_repo.get_by_id.side_effect = get_by_id_side_effect
        self.controller.event_repo.get_recent_events.side_effect = get_recent_events_side_effect
        self.controller.calculator.calculate_health_score.side_effect = calculate_side_effect
        self.controller.health_score_repo.save_health_score.side_effect = save_side_effect
        
        result = self.controller.bulk_calculate_health_scores(customer_ids)
        
        assert result["processed_customers"] == 3
        assert len(result["results"]) == 3
        assert result["results"][0]["customer_id"] == 1
        assert result["results"][0]["score"] == 71.0
        assert result["average_score"] == 72.0  # (71 + 72 + 73) / 3
    
    def test_bulk_calculate_health_scores_missing_customers(self):
        """Test bulk calculation with some missing customers"""
        customer_ids = [1, 999, 3]  # Customer 999 doesn't exist
        
        # Mock only existing customers
        mock_customer1 = Mock()
        mock_customer1.id = 1
        mock_customer3 = Mock()
        mock_customer3.id = 3
        
        def get_by_id_side_effect(customer_id):
            if customer_id == 1:
                return mock_customer1
            elif customer_id == 3:
                return mock_customer3
            return None
        
        self.controller.customer_repo.get_by_id.side_effect = get_by_id_side_effect
        self.controller.event_repo.get_recent_events.return_value = []
        
        # Mock calculation for existing customers
        mock_score = Mock()
        mock_score.score = 75.0
        mock_score.status = "healthy"
        self.controller.calculator.calculate_health_score.return_value = mock_score
        self.controller.health_score_repo.save_health_score.return_value = mock_score
        
        result = self.controller.bulk_calculate_health_scores(customer_ids)
        
        # Should only process existing customers
        assert result["processed_customers"] == 2
        assert len(result["results"]) == 2
    
    def test_get_latest_health_score(self):
        """Test getting latest health score for a customer"""
        mock_score = Mock()
        mock_score.score = 80.0
        mock_score.status = "healthy"
        
        self.controller.health_score_repo.get_latest_by_customer.return_value = mock_score
        
        result = self.controller.get_latest_health_score(1)
        
        assert result == mock_score
        self.controller.health_score_repo.get_latest_by_customer.assert_called_once_with(1)
    
    def test_singleton_pattern(self):
        """Test that HealthScoreController follows singleton pattern"""
        controller1 = HealthScoreController(self.mock_db)
        controller2 = HealthScoreController(self.mock_db)
        
        assert controller1 is controller2