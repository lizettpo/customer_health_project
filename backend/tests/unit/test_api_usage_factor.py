"""
Unit tests for ApiUsageFactor
"""
import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

from domain.health_factors.api_usage import ApiUsageFactor
from domain.models import Customer, CustomerEvent, FactorScore


class TestApiUsageFactor:
    
    def setup_method(self):
        """Set up test fixtures"""
        self.factor = ApiUsageFactor()
        
        # Mock customer
        self.customer = Mock(spec=Customer)
        self.customer.id = 1
        self.customer.segment = "Enterprise"
        self.customer.is_enterprise.return_value = True
        self.customer.get_expected_api_calls.return_value = 1000
    
    def test_factor_properties(self):
        """Test factor properties are correctly defined"""
        assert self.factor.name == "api_usage"
        assert self.factor.weight == 0.15
        assert "integration depth" in self.factor.description.lower()
    
    def test_calculate_score_high_usage(self):
        """Test score calculation for high API usage"""
        # Create 1200 API call events in last 30 days
        events = []
        base_time = datetime.utcnow() - timedelta(days=15)
        
        for i in range(1200):
            event = Mock(spec=CustomerEvent)
            event.event_type = "api_call"
            event.timestamp = base_time + timedelta(hours=i % 24, minutes=i % 60)
            event.event_data = {
                "endpoint": f"/api/endpoint{i % 3}",
                "method": "GET" if i % 2 == 0 else "POST",
                "response_code": 200 if i % 10 != 0 else 400
            }
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert isinstance(result, FactorScore)
        assert result.score == 100.0  # Capped at 100
        assert result.value == 1200
        assert "1200 API calls" in result.description
        assert result.trend in ["improving", "declining", "stable"]
        assert "expected_calls" in result.metadata
        assert "endpoints" in result.metadata
        assert "error_rate" in result.metadata
    
    def test_calculate_score_low_usage(self):
        """Test score calculation for low API usage"""
        # Create only 100 API call events (10% of expected 1000)
        events = []
        base_time = datetime.utcnow() - timedelta(days=20)
        
        for i in range(100):
            event = Mock(spec=CustomerEvent)
            event.event_type = "api_call"
            event.timestamp = base_time + timedelta(hours=i)
            event.event_data = {
                "endpoint": "/api/test",
                "method": "GET",
                "response_code": 200
            }
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.score == 10.0  # 100/1000 * 100 = 10
        assert result.value == 100
        assert "100 API calls" in result.description
        assert result.metadata["expected_calls"] == 1000
    
    def test_calculate_score_no_api_calls(self):
        """Test score calculation with no API calls"""
        # Create events that are not API calls
        events = []
        for i in range(50):
            event = Mock(spec=CustomerEvent)
            event.event_type = "login"  # Not an API call
            event.timestamp = datetime.utcnow() - timedelta(days=i % 30)
            event.event_data = {}
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.score == 0.0
        assert result.value == 0
        assert "0 API calls" in result.description
        assert result.metadata["error_rate"] == 0
    
    def test_calculate_score_old_events_excluded(self):
        """Test that events older than 30 days are excluded"""
        events = []
        
        # Add 50 recent events (within 30 days)
        recent_time = datetime.utcnow() - timedelta(days=10)
        for i in range(50):
            event = Mock(spec=CustomerEvent)
            event.event_type = "api_call"
            event.timestamp = recent_time + timedelta(hours=i)
            event.event_data = {"endpoint": "/api/test", "method": "GET", "response_code": 200}
            events.append(event)
        
        # Add 100 old events (older than 30 days)
        old_time = datetime.utcnow() - timedelta(days=35)
        for i in range(100):
            event = Mock(spec=CustomerEvent)
            event.event_type = "api_call"
            event.timestamp = old_time + timedelta(hours=i)
            event.event_data = {"endpoint": "/api/old", "method": "GET", "response_code": 200}
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        # Should only count the 50 recent events
        assert result.value == 50
        assert result.score == 5.0  # 50/1000 * 100 = 5
    
    def test_calculate_score_trend_improving(self):
        """Test trend calculation for improving usage"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=30)
        
        # Add 10 events in first 15 days
        for i in range(10):
            event = Mock(spec=CustomerEvent)
            event.event_type = "api_call"
            event.timestamp = base_time + timedelta(days=i)
            event.event_data = {"endpoint": "/api/test", "method": "GET", "response_code": 200}
            events.append(event)
        
        # Add 30 events in last 15 days (more recent usage)
        recent_time = datetime.utcnow() - timedelta(days=15)
        for i in range(30):
            event = Mock(spec=CustomerEvent)
            event.event_type = "api_call"
            event.timestamp = recent_time + timedelta(hours=i)
            event.event_data = {"endpoint": "/api/test", "method": "GET", "response_code": 200}
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.trend == "improving"
        assert result.metadata["recent_calls"] >= 29  # Allow for boundary conditions
    
    def test_calculate_score_trend_declining(self):
        """Test trend calculation for declining usage"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=30)
        
        # Add 30 events in first 15 days
        for i in range(30):
            event = Mock(spec=CustomerEvent)
            event.event_type = "api_call"
            event.timestamp = base_time + timedelta(hours=i)
            event.event_data = {"endpoint": "/api/test", "method": "GET", "response_code": 200}
            events.append(event)
        
        # Add 10 events in last 15 days (less recent usage)
        recent_time = datetime.utcnow() - timedelta(days=15)
        for i in range(10):
            event = Mock(spec=CustomerEvent)
            event.event_type = "api_call"
            event.timestamp = recent_time + timedelta(days=i)
            event.event_data = {"endpoint": "/api/test", "method": "GET", "response_code": 200}
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.trend == "declining"
        assert result.metadata["recent_calls"] <= 11  # Allow for boundary conditions
    
    def test_calculate_score_error_rate(self):
        """Test error rate calculation"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=10)
        
        # Add 80 successful API calls
        for i in range(80):
            event = Mock(spec=CustomerEvent)
            event.event_type = "api_call"
            event.timestamp = base_time + timedelta(hours=i)
            event.event_data = {"endpoint": "/api/test", "method": "GET", "response_code": 200}
            events.append(event)
        
        # Add 20 error API calls (400, 401, 500)
        error_codes = [400, 401, 500]
        for i in range(20):
            event = Mock(spec=CustomerEvent)
            event.event_type = "api_call"
            event.timestamp = base_time + timedelta(hours=80 + i)
            event.event_data = {
                "endpoint": "/api/test", 
                "method": "GET", 
                "response_code": error_codes[i % 3]
            }
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.metadata["error_rate"] == 20.0  # 20/100 * 100 = 20%
        assert result.metadata["response_codes"]["400"] > 0
        assert result.metadata["response_codes"]["401"] > 0
        assert result.metadata["response_codes"]["500"] > 0
    
    def test_generate_recommendations_very_low_usage(self):
        """Test recommendations for very low API usage"""
        score = FactorScore(score=25.0, value=250, description="Low usage")
        
        recommendations = self.factor.generate_recommendations(score, self.customer)
        
        assert len(recommendations) > 0
        assert any("very low" in rec.lower() for rec in recommendations)
        assert any("technical consultation" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_low_usage(self):
        """Test recommendations for moderately low API usage"""
        score = FactorScore(score=45.0, value=450, description="Moderate usage")
        
        recommendations = self.factor.generate_recommendations(score, self.customer)
        
        assert len(recommendations) > 0
        assert any("integration support" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_high_usage_enterprise(self):
        """Test recommendations for high usage enterprise customer"""
        score = FactorScore(score=85.0, value=850, description="High usage")
        
        recommendations = self.factor.generate_recommendations(score, self.customer)
        
        assert len(recommendations) > 0
        assert any("upselling" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_excellent_usage(self):
        """Test recommendations for excellent API usage"""
        score = FactorScore(score=95.0, value=950, description="Excellent usage")
        
        # Use non-enterprise customer to get the >90 recommendation
        non_enterprise_customer = Mock()
        non_enterprise_customer.is_enterprise.return_value = False
        
        recommendations = self.factor.generate_recommendations(score, non_enterprise_customer)
        
        assert len(recommendations) > 0
        assert any("integration case study" in rec.lower() for rec in recommendations)
    
  