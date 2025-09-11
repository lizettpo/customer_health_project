"""
Unit tests for HealthScoreCalculator
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from domain.calculators import HealthScoreCalculator
from domain.models import Customer, CustomerEvent, HealthScore, FactorScore
from domain.exceptions import InvalidHealthScoreError


class TestHealthScoreCalculator:
    
    def setup_method(self):
        """Set up test fixtures"""
        self.calculator = HealthScoreCalculator()
        
        # Mock customer
        self.customer = Mock(spec=Customer)
        self.customer.id = 1
        self.customer.name = "Test Customer"
        self.customer.segment = "Enterprise"
        self.customer.is_enterprise.return_value = True
        
        # Mock events
        self.events = [
            Mock(spec=CustomerEvent),
            Mock(spec=CustomerEvent),
            Mock(spec=CustomerEvent)
        ]
    
    def test_calculator_initialization(self):
        """Test that calculator initializes with proper factors"""
        assert len(self.calculator.factors) == 5
        
        # Check that factor weights sum to 1.0
        total_weight = sum(factor.weight for factor in self.calculator.factors)
        assert abs(total_weight - 1.0) < 0.001
    
    def test_calculate_health_score_success(self):
        """Test successful health score calculation"""
        # Mock factor scores
        mock_factor_score = FactorScore(
            score=80.0,
            value=100,
            description="Good performance"
        )
        
        # Mock all factors to return the same score
        for factor in self.calculator.factors:
            factor.calculate_score = Mock(return_value=mock_factor_score)
            factor.generate_recommendations = Mock(return_value=["Test recommendation"])
        
        result = self.calculator.calculate_health_score(self.customer, self.events)
        
        assert isinstance(result, HealthScore)
        assert result.customer_id == 1
        assert result.score == 80.0
        assert result.status == "healthy"
        assert len(result.factors) == 5
        assert len(result.recommendations) > 0
    
    def test_calculate_health_score_with_factor_error(self):
        """Test health score calculation when a factor fails"""
        # Mock first factor to raise an error
        self.calculator.factors[0].calculate_score = Mock(side_effect=Exception("Test error"))
        self.calculator.factors[0].generate_recommendations = Mock(return_value=[])
        
        # Mock other factors normally
        mock_factor_score = FactorScore(score=75.0, value=100, description="Good")
        for factor in self.calculator.factors[1:]:
            factor.calculate_score = Mock(return_value=mock_factor_score)
            factor.generate_recommendations = Mock(return_value=[])
        
        result = self.calculator.calculate_health_score(self.customer, self.events)
        
        # Should still return a valid result with default score for failed factor
        assert isinstance(result, HealthScore)
        assert result.customer_id == 1
        assert len(result.factors) == 5
    
    def test_determine_status_healthy(self):
        """Test status determination for healthy score"""
        assert self.calculator._determine_status(85.0) == "healthy"
        assert self.calculator._determine_status(75.0) == "healthy"
    
    def test_determine_status_at_risk(self):
        """Test status determination for at-risk score"""
        assert self.calculator._determine_status(65.0) == "at_risk"
        assert self.calculator._determine_status(50.0) == "at_risk"
    
    def test_determine_status_critical(self):
        """Test status determination for critical score"""
        assert self.calculator._determine_status(40.0) == "critical"
        assert self.calculator._determine_status(25.0) == "critical"
    
    def test_generate_general_recommendations_excellent(self):
        """Test recommendations for excellent scores"""
        recommendations = self.calculator._generate_general_recommendations(90.0, self.customer)
        
        assert "Excellent customer health!" in " ".join(recommendations)
        assert "referral program" in " ".join(recommendations)
    
    def test_generate_general_recommendations_healthy(self):
        """Test recommendations for healthy scores"""
        recommendations = self.calculator._generate_general_recommendations(78.0, self.customer)
        
        assert "Healthy customer" in " ".join(recommendations)
    
    def test_generate_general_recommendations_at_risk(self):
        """Test recommendations for at-risk scores"""
        recommendations = self.calculator._generate_general_recommendations(55.0, self.customer)
        
        assert "Monitor closely" in " ".join(recommendations)
    
    def test_generate_general_recommendations_critical(self):
        """Test recommendations for critical scores"""
        recommendations = self.calculator._generate_general_recommendations(30.0, self.customer)
        
        assert "CRITICAL" in " ".join(recommendations)
        assert "executive escalation" in " ".join(recommendations)
    
    def test_generate_general_recommendations_enterprise_at_risk(self):
        """Test enterprise-specific recommendations for at-risk customers"""
        recommendations = self.calculator._generate_general_recommendations(55.0, self.customer)
        
        assert "Enterprise account at risk" in " ".join(recommendations)
    
    def test_generate_general_recommendations_startup_high_performing(self):
        """Test startup-specific recommendations for high-performing customers"""
        startup_customer = Mock(spec=Customer)
        startup_customer.segment = "startup"
        startup_customer.is_enterprise.return_value = False
        
        recommendations = self.calculator._generate_general_recommendations(85.0, startup_customer)
        
        assert "upsell opportunities" in " ".join(recommendations)
    
    def test_get_factor_weights(self):
        """Test getting factor weights"""
        weights = self.calculator.get_factor_weights()
        
        assert isinstance(weights, dict)
        assert len(weights) == 5
        assert all(isinstance(weight, (int, float)) for weight in weights.values())
    
    def test_get_factor_descriptions(self):
        """Test getting factor descriptions"""
        descriptions = self.calculator.get_factor_descriptions()
        
        assert isinstance(descriptions, dict)
        assert len(descriptions) == 5
        assert all(isinstance(desc, str) for desc in descriptions.values())
    
    def test_invalid_weights_raise_error(self):
        """Test that invalid factor weights raise an error"""
        with patch('domain.calculators.LoginFrequencyFactor') as mock_factor:
            mock_factor.return_value.weight = 0.5  # This would make total != 1.0
            
            with pytest.raises(InvalidHealthScoreError):
                HealthScoreCalculator()
    
    def test_score_rounding(self):
        """Test that scores are properly rounded to 2 decimal places"""
        # Mock factors to return scores that would result in a non-round number
        mock_factor_score = FactorScore(score=77.777, value=100, description="Test")
        
        for factor in self.calculator.factors:
            factor.calculate_score = Mock(return_value=mock_factor_score)
            factor.generate_recommendations = Mock(return_value=[])
        
        result = self.calculator.calculate_health_score(self.customer, self.events)
        
        # Check that the score is rounded to 2 decimal places
        assert isinstance(result.score, float)
        assert len(str(result.score).split('.')[-1]) <= 2
    
    def test_unique_recommendations(self):
        """Test that duplicate recommendations are removed"""
        # Mock factors to return duplicate recommendations
        for factor in self.calculator.factors:
            factor.calculate_score = Mock(return_value=FactorScore(score=75.0, value=100, description="Test"))
            factor.generate_recommendations = Mock(return_value=["Duplicate rec", "Unique rec"])
        
        result = self.calculator.calculate_health_score(self.customer, self.events)
        
        # Count occurrences of "Duplicate rec" - should only appear once
        duplicate_count = sum(1 for rec in result.recommendations if "Duplicate rec" in rec)
        assert duplicate_count == 1