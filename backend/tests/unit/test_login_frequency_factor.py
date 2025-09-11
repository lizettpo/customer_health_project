"""
Unit tests for LoginFrequencyFactor
"""
import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

from domain.health_factors.login_frequency import LoginFrequencyFactor
from domain.models import Customer, CustomerEvent, FactorScore


class TestLoginFrequencyFactor:
    
    def setup_method(self):
        """Set up test fixtures"""
        self.factor = LoginFrequencyFactor()
        
        # Mock customer
        self.customer = Mock(spec=Customer)
        self.customer.id = 1
        self.customer.segment = "Enterprise"
    
    def test_factor_properties(self):
        """Test factor properties are correctly defined"""
        assert self.factor.name == "login_frequency"
        assert self.factor.weight == 0.25
        assert "engagement" in self.factor.description.lower()
    
    def test_calculate_score_perfect_usage(self):
        """Test score calculation for perfect login frequency"""
        # Create exactly 20 login events (expected amount)
        events = []
        base_time = datetime.utcnow() - timedelta(days=25)
        
        for i in range(20):
            event = Mock(spec=CustomerEvent)
            event.event_type = "login"
            event.timestamp = base_time + timedelta(days=i)
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert isinstance(result, FactorScore)
        assert result.score == 100.0
        assert result.value == 20
        assert "20 logins" in result.description
        assert result.metadata["expected_logins"] == 20
    
    def test_calculate_score_high_usage(self):
        """Test score calculation for high login frequency"""
        # Create 30 login events (150% of expected)
        events = []
        base_time = datetime.utcnow() - timedelta(days=29)
        
        for i in range(30):
            event = Mock(spec=CustomerEvent)
            event.event_type = "login"
            event.timestamp = base_time + timedelta(hours=i * 23)  # Spread out
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.score == 100.0  # Capped at 100
        assert result.value == 30
        assert "30 logins" in result.description
    
    def test_calculate_score_low_usage(self):
        """Test score calculation for low login frequency"""
        # Create only 5 login events (25% of expected 20)
        events = []
        base_time = datetime.utcnow() - timedelta(days=20)
        
        for i in range(5):
            event = Mock(spec=CustomerEvent)
            event.event_type = "login"
            event.timestamp = base_time + timedelta(days=i * 4)
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.score == 25.0  # 5/20 * 100 = 25
        assert result.value == 5
        assert "5 logins" in result.description
    
    def test_calculate_score_no_logins(self):
        """Test score calculation with no login events"""
        # Create non-login events
        events = []
        for i in range(10):
            event = Mock(spec=CustomerEvent)
            event.event_type = "api_call"  # Not a login
            event.timestamp = datetime.utcnow() - timedelta(days=i)
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.score == 0.0
        assert result.value == 0
        assert "0 logins" in result.description
    
    def test_calculate_score_old_events_excluded(self):
        """Test that events older than 30 days are excluded"""
        events = []
        
        # Add 10 recent login events (within 30 days)
        recent_time = datetime.utcnow() - timedelta(days=25)
        for i in range(10):
            event = Mock(spec=CustomerEvent)
            event.event_type = "login"
            event.timestamp = recent_time + timedelta(days=i * 2)
            events.append(event)
        
        # Add 20 old login events (older than 30 days)
        old_time = datetime.utcnow() - timedelta(days=50)
        for i in range(20):
            event = Mock(spec=CustomerEvent)
            event.event_type = "login"
            event.timestamp = old_time + timedelta(days=i)
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        # Should only count the 10 recent events
        assert result.value == 10
        assert result.score == 50.0  # 10/20 * 100 = 50
    
    def test_calculate_score_trend_improving(self):
        """Test trend calculation for improving login frequency"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=30)
        
        # Add 5 events in first 15 days
        for i in range(5):
            event = Mock(spec=CustomerEvent)
            event.event_type = "login"
            event.timestamp = base_time + timedelta(days=i * 3)
            events.append(event)
        
        # Add 15 events in last 15 days (more recent activity)
        recent_time = datetime.utcnow() - timedelta(days=15)
        for i in range(15):
            event = Mock(spec=CustomerEvent)
            event.event_type = "login"
            event.timestamp = recent_time + timedelta(days=i)
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.trend == "improving"
        assert result.metadata["recent_activity"] >= 14  # Allow for boundary conditions
        assert result.metadata["previous_activity"] <= 6
    
    def test_calculate_score_trend_declining(self):
        """Test trend calculation for declining login frequency"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=30)
        
        # Add 15 events in first 15 days
        for i in range(15):
            event = Mock(spec=CustomerEvent)
            event.event_type = "login"
            event.timestamp = base_time + timedelta(days=i)
            events.append(event)
        
        # Add 5 events in last 15 days (less recent activity)
        recent_time = datetime.utcnow() - timedelta(days=15)
        for i in range(5):
            event = Mock(spec=CustomerEvent)
            event.event_type = "login"
            event.timestamp = recent_time + timedelta(days=i * 3)
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.trend == "declining"
        assert result.metadata["recent_activity"] <= 6  # Allow for boundary conditions
        assert result.metadata["previous_activity"] >= 14
    
    def test_calculate_score_trend_stable(self):
        """Test trend calculation for stable login frequency"""
        events = []
        now = datetime.utcnow()
        
        # Add 10 events in days 16-30 (older period - clearly outside recent 15 days)
        for i in range(10):
            event = Mock(spec=CustomerEvent)
            event.event_type = "login"
            event.timestamp = now - timedelta(days=16+i, hours=12)  # Days 16-25 ago
            events.append(event)
        
        # Add 10 events in last 15 days (recent period - clearly within recent 15 days)
        for i in range(10):
            event = Mock(spec=CustomerEvent)
            event.event_type = "login"
            event.timestamp = now - timedelta(days=1+i, hours=12)  # Days 1-10 ago
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.trend == "stable"
        # For stable trend, recent and previous should be equal
        recent = result.metadata["recent_activity"]
        previous = result.metadata["previous_activity"]
        assert recent == 10
        assert previous == 10
    
    def test_generate_recommendations_critical_usage(self):
        """Test recommendations for critical low usage"""
        score = FactorScore(score=25.0, value=5, description="Very low usage")
        
        recommendations = self.factor.generate_recommendations(score, self.customer)
        
        assert len(recommendations) > 0
        assert any("CRITICAL" in rec for rec in recommendations)
        assert any("immediate check-in" in rec.lower() for rec in recommendations)
        assert any("re-onboarding" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_low_usage(self):
        """Test recommendations for low usage"""
        score = FactorScore(score=50.0, value=10, description="Low usage")
        
        recommendations = self.factor.generate_recommendations(score, self.customer)
        
        assert len(recommendations) > 0
        assert any("engagement" in rec.lower() for rec in recommendations)
        assert any("usage tips" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_excellent_usage(self):
        """Test recommendations for excellent usage"""
        score = FactorScore(score=85.0, value=17, description="Excellent usage")
        
        recommendations = self.factor.generate_recommendations(score, self.customer)
        
        assert len(recommendations) > 0
        assert any("excellent" in rec.lower() for rec in recommendations)
        assert any("case study" in rec.lower() or "testimonial" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_medium_usage(self):
        """Test recommendations for medium usage (no specific recommendations)"""
        score = FactorScore(score=70.0, value=14, description="Medium usage")
        
        recommendations = self.factor.generate_recommendations(score, self.customer)
        
        # Should return empty list for medium scores
        assert len(recommendations) == 0