"""
Unit tests for FeatureAdoptionFactor
"""
import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

from domain.health_factors.feature_adoption import FeatureAdoptionFactor
from domain.models import Customer, CustomerEvent, FactorScore


class TestFeatureAdoptionFactor:
    
    def setup_method(self):
        """Set up test fixtures"""
        self.factor = FeatureAdoptionFactor()
        
        # Mock customer
        self.customer = Mock(spec=Customer)
        self.customer.id = 1
        self.customer.segment = "Enterprise"
    
    def test_factor_properties(self):
        """Test factor properties are correctly defined"""
        assert self.factor.name == "feature_adoption"
        assert self.factor.weight == 0.25
        assert "platform utilization" in self.factor.description.lower()
    
    def test_calculate_score_perfect_adoption(self):
        """Test score calculation for perfect feature adoption"""
        # Create events for exactly 8 unique features (expected amount)
        events = []
        features = ["dashboard", "reports", "analytics", "notifications", 
                   "integrations", "workflows", "templates", "exports"]
        base_time = datetime.utcnow() - timedelta(days=15)
        
        for i, feature in enumerate(features):
            event = Mock(spec=CustomerEvent)
            event.event_type = "feature_use"
            event.timestamp = base_time + timedelta(days=i)
            event.get_feature_name.return_value = feature
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert isinstance(result, FactorScore)
        assert result.score == 100.0
        assert result.value == 8
        assert "8 unique features" in result.description
        assert result.metadata["expected_features"] == 8
        assert len(result.metadata["features_used"]) == 8
    
    def test_calculate_score_high_adoption(self):
        """Test score calculation for high feature adoption (more than expected)"""
        # Create events for 10 unique features (125% of expected)
        events = []
        features = ["dashboard", "reports", "analytics", "notifications", 
                   "integrations", "workflows", "templates", "exports", 
                   "admin", "billing"]
        base_time = datetime.utcnow() - timedelta(days=20)
        
        for i, feature in enumerate(features):
            event = Mock(spec=CustomerEvent)
            event.event_type = "feature_use"
            event.timestamp = base_time + timedelta(days=i * 2)
            event.get_feature_name.return_value = feature
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.score == 100.0  # Capped at 100
        assert result.value == 10
        assert "10 unique features" in result.description
    
    def test_calculate_score_low_adoption(self):
        """Test score calculation for low feature adoption"""
        # Create events for only 2 unique features (25% of expected 8)
        events = []
        features = ["dashboard", "reports"]
        base_time = datetime.utcnow() - timedelta(days=10)
        
        for i, feature in enumerate(features):
            # Add multiple events for same features
            for j in range(5):
                event = Mock(spec=CustomerEvent)
                event.event_type = "feature_use"
                event.timestamp = base_time + timedelta(days=i, hours=j)
                event.get_feature_name.return_value = feature
                events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.score == 25.0  # 2/8 * 100 = 25
        assert result.value == 2
        assert "2 unique features" in result.description
        assert result.metadata["feature_usage_count"]["dashboard"] == 5
        assert result.metadata["feature_usage_count"]["reports"] == 5
    
    def test_calculate_score_no_feature_usage(self):
        """Test score calculation with no feature usage events"""
        # Create non-feature-use events
        events = []
        for i in range(10):
            event = Mock(spec=CustomerEvent)
            event.event_type = "login"  # Not feature_use
            event.timestamp = datetime.utcnow() - timedelta(days=i)
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.score == 0.0
        assert result.value == 0
        assert "0 unique features" in result.description
        assert len(result.metadata["features_used"]) == 0
    
    def test_calculate_score_old_events_excluded(self):
        """Test that events older than 30 days are excluded"""
        events = []
        
        # Add 3 recent feature usage events (within 30 days)
        recent_features = ["dashboard", "reports", "analytics"]
        recent_time = datetime.utcnow() - timedelta(days=15)
        for i, feature in enumerate(recent_features):
            event = Mock(spec=CustomerEvent)
            event.event_type = "feature_use"
            event.timestamp = recent_time + timedelta(days=i)
            event.get_feature_name.return_value = feature
            events.append(event)
        
        # Add 5 old feature usage events (older than 30 days)
        old_features = ["workflows", "templates", "exports", "integrations", "admin"]
        old_time = datetime.utcnow() - timedelta(days=35)
        for i, feature in enumerate(old_features):
            event = Mock(spec=CustomerEvent)
            event.event_type = "feature_use"
            event.timestamp = old_time + timedelta(days=i)
            event.get_feature_name.return_value = feature
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        # Should only count the 3 recent features
        assert result.value == 3
        assert result.score == 37.5  # 3/8 * 100 = 37.5
        assert set(result.metadata["features_used"]) == {"dashboard", "reports", "analytics"}
    
    def test_calculate_score_most_and_least_used_features(self):
        """Test identification of most and least used features"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=20)
        
        # Dashboard used 10 times (most used)
        for i in range(10):
            event = Mock(spec=CustomerEvent)
            event.event_type = "feature_use"
            event.timestamp = base_time + timedelta(hours=i)
            event.get_feature_name.return_value = "dashboard"
            events.append(event)
        
        # Reports used 5 times
        for i in range(5):
            event = Mock(spec=CustomerEvent)
            event.event_type = "feature_use"
            event.timestamp = base_time + timedelta(hours=10 + i)
            event.get_feature_name.return_value = "reports"
            events.append(event)
        
        # Analytics used 1 time (least used)
        event = Mock(spec=CustomerEvent)
        event.event_type = "feature_use"
        event.timestamp = base_time + timedelta(hours=20)
        event.get_feature_name.return_value = "analytics"
        events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        assert result.metadata["most_used_feature"] == "dashboard"
        assert result.metadata["least_used_feature"] == "analytics"
        assert result.metadata["feature_usage_count"]["dashboard"] == 10
        assert result.metadata["feature_usage_count"]["reports"] == 5
        assert result.metadata["feature_usage_count"]["analytics"] == 1
    
    def test_calculate_score_feature_name_none(self):
        """Test handling of events where get_feature_name returns None"""
        events = []
        base_time = datetime.utcnow() - timedelta(days=10)
        
        # Add some valid feature events
        for i in range(3):
            event = Mock(spec=CustomerEvent)
            event.event_type = "feature_use"
            event.timestamp = base_time + timedelta(days=i)
            event.get_feature_name.return_value = f"feature_{i}"
            events.append(event)
        
        # Add events with None feature names
        for i in range(5):
            event = Mock(spec=CustomerEvent)
            event.event_type = "feature_use"
            event.timestamp = base_time + timedelta(days=3 + i)
            event.get_feature_name.return_value = None
            events.append(event)
        
        result = self.factor.calculate_score(self.customer, events)
        
        # Should only count features with valid names
        assert result.value == 3
        assert len(result.metadata["features_used"]) == 3
        assert None not in result.metadata["features_used"]
    
    def test_generate_recommendations_critical_adoption(self):
        """Test recommendations for critical low feature adoption"""
        score = FactorScore(score=20.0, value=2, description="Very low adoption")
        
        recommendations = self.factor.generate_recommendations(score, self.customer)
        
        assert len(recommendations) > 0
        assert any("CRITICAL" in rec for rec in recommendations)
        assert any("onboarding review" in rec.lower() for rec in recommendations)
        assert any("guided tour" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_low_adoption(self):
        """Test recommendations for low feature adoption"""
        score = FactorScore(score=45.0, value=4, description="Low adoption")
        
        recommendations = self.factor.generate_recommendations(score, self.customer)
        
        assert len(recommendations) > 0
        assert any("product demo" in rec.lower() for rec in recommendations)
        assert any("feature education" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_excellent_adoption(self):
        """Test recommendations for excellent feature adoption"""
        score = FactorScore(score=85.0, value=7, description="Excellent adoption")
        
        recommendations = self.factor.generate_recommendations(score, self.customer)
        
        assert len(recommendations) > 0
        assert any("great feature adoption" in rec.lower() for rec in recommendations)
        assert any("advanced feature training" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_medium_adoption(self):
        """Test recommendations for medium feature adoption (no specific recommendations)"""
        score = FactorScore(score=70.0, value=6, description="Medium adoption")
        
        recommendations = self.factor.generate_recommendations(score, self.customer)
        
        # Should return empty list for medium scores
        assert len(recommendations) == 0
    
