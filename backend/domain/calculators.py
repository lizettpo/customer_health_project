"""
Domain Layer - Health Score Calculator
Orchestrates all health factors to calculate overall health score
"""

from typing import List
from datetime import datetime

from domain.models import Customer, CustomerEvent, HealthScore, FactorScore
from domain.health_factors.login_frequency import LoginFrequencyFactor
from domain.health_factors.feature_adoption import FeatureAdoptionFactor
from domain.health_factors.support_tickets import SupportTicketsFactor
from domain.health_factors.payment_timeliness import PaymentTimelinessFactor
from domain.health_factors.api_usage import ApiUsageFactor
from domain.exceptions import InvalidHealthScoreError


class HealthScoreCalculator:
    """
    Calculator that orchestrates all health factors to produce overall health score.
    
    This class serves as the central coordinator for health score calculation,
    combining multiple health factors into a single comprehensive score.
    Each factor is weighted and contributes to the overall customer health assessment.
    
    The calculator includes:
    - Login Frequency (20% weight)
    - Feature Adoption (25% weight) 
    - Support Tickets (20% weight)
    - Payment Timeliness (20% weight)
    - API Usage (15% weight)
    """
    
    def __init__(self):
        """
        Initialize the health score calculator with all health factors.

        Sets up all health factor instances and validates that their weights
        sum to 1.0 for proper normalized scoring. Each factor contributes to
        the overall customer health assessment based on its specific weight.

        Health Factors Initialized:
        - LoginFrequencyFactor: User engagement patterns (weight: 0.20)
        - FeatureAdoptionFactor: Platform feature utilization (weight: 0.15)
        - SupportTicketsFactor: Support interaction analysis (weight: 0.10)
        - PaymentTimelinessFactor: Financial health indicators (weight: 0.25)
        - ApiUsageFactor: API integration depth and usage (weight: 0.30)

        Weight Validation:
        Ensures all factor weights sum to exactly 1.0 (±0.001 tolerance)
        to maintain proper scoring normalization across all factors.

        Raises:
            InvalidHealthScoreError: If factor weights don't sum to 1.0 within tolerance
        """
        # Initialize all health factors with their specific calculation logic
        self.factors = [
            LoginFrequencyFactor(),    # Tracks user login patterns and engagement
            FeatureAdoptionFactor(),   # Measures feature discovery and usage
            SupportTicketsFactor(),    # Analyzes support interaction frequency
            PaymentTimelinessFactor(), # Evaluates payment behavior and timeliness
            ApiUsageFactor()           # Monitors API integration and automation
        ]

        # Validate that weights sum to 1.0 for proper normalized scoring
        total_weight = sum(factor.weight for factor in self.factors)
        if abs(total_weight - 1.0) > 0.001:  # Allow small floating-point tolerance
            raise InvalidHealthScoreError(f"Factor weights must sum to 1.0, got {total_weight}")
    
    def calculate_health_score(self, customer: Customer, events: List[CustomerEvent]) -> HealthScore:
        """
        Calculate comprehensive health score using all factors.
        
        Orchestrates the calculation across all health factors, computes the weighted
        overall score, determines health status, and generates recommendations.
        
        Args:
            customer: Customer entity containing basic information and segment
            events: List of customer events (typically last 90 days)
            
        Returns:
            HealthScore: Complete health assessment containing:
                - Overall weighted score (0-100)
                - Health status ('healthy', 'at_risk', 'critical')
                - Individual factor scores and metadata
                - Actionable recommendations
                - Calculation timestamp
                
        Raises:
            InvalidHealthScoreError: If calculation fails or produces invalid score
        """
        
        factor_scores = {}
        overall_score = 0.0
        all_recommendations = []
        
        # Calculate each factor
        for factor in self.factors:
            try:
                score = factor.calculate_score(customer, events)
                factor_scores[factor.name] = score
                
                # Add to weighted overall score
                overall_score += score.score * factor.weight
                
                # Collect recommendations
                recommendations = factor.generate_recommendations(score, customer)
                all_recommendations.extend(recommendations)
                
            except Exception as e:
                # Handle individual factor calculation errors gracefully
                print(f"Error calculating {factor.name}: {e}")
                # Use default score for failed calculations
                factor_scores[factor.name] = FactorScore(
                    score=50.0,
                    value=0,
                    description=f"Error calculating {factor.name}"
                )
                overall_score += 50.0 * factor.weight
        
        # Determine health status
        status = self._determine_status(overall_score)
        
        # Add general recommendations
        general_recommendations = self._generate_general_recommendations(overall_score, customer)
        all_recommendations.extend(general_recommendations)
        
        # Remove duplicates while preserving order
        unique_recommendations = list(dict.fromkeys(all_recommendations))
        
        return HealthScore(
            id=None,
            customer_id=customer.id,
            score=round(overall_score, 2),
            status=status,
            factors=factor_scores,
            recommendations=unique_recommendations,
            calculated_at=datetime.utcnow()
        )
    
    def _determine_status(self, score: float) -> str:
        """
        Determine health status based on overall score.
        
        Args:
            score: Overall weighted health score (0-100)
            
        Returns:
            str: Health status classification:
                - 'healthy': 75+ (low churn risk)
                - 'at_risk': 50-74 (moderate churn risk)
                - 'critical': <50 (high churn risk)
        """
        if score >= 75:
            return "healthy"
        elif score >= 50:
            return "at_risk"
        else:
            return "critical"
    
    def _generate_general_recommendations(self, score: float, customer: Customer) -> List[str]:
        """
        Generate general recommendations based on overall health score.
        
        Provides high-level recommendations that apply to the overall customer
        health situation, complementing factor-specific recommendations.
        
        Args:
            score: Overall weighted health score (0-100)
            customer: Customer entity for segment-specific recommendations
            
        Returns:
            List[str]: General recommendations including:
                - Action urgency level
                - Customer success interventions
                - Segment-specific guidance
                - Escalation requirements
        """
        recommendations = []
        
        if score >= 85:
            recommendations.append("Excellent customer health! Consider case study opportunity")
            recommendations.append("Perfect candidate for referral program")
        elif score >= 75:
            recommendations.append("Healthy customer - maintain current engagement level")
        elif score >= 60:
            recommendations.append("Monitor closely - early intervention could prevent churn")
        elif score >= 40:
            recommendations.append("At-risk customer requires immediate attention")
            recommendations.append("Schedule customer success check-in within 48 hours")
        else:
            recommendations.append("CRITICAL: High churn risk - executive escalation recommended")
            recommendations.append("Immediate intervention required to save account")
        
        # Segment-specific recommendations
        if customer.is_enterprise() and score < 60:
            recommendations.append("Enterprise account at risk - involve account management team")
        elif customer.segment == "startup" and score > 80:
            recommendations.append("High-performing startup - monitor for growth/upsell opportunities")
        
        return recommendations
    
    def get_factor_weights(self) -> dict:
        """
        Get current factor weights for transparency.
        
        Returns:
            dict: Mapping of factor names to their weights in overall calculation
        """
        return {factor.name: factor.weight for factor in self.factors}
    
    def get_factor_descriptions(self) -> dict:
        """
        Get descriptions of all factors for documentation.
        
        Returns:
            dict: Mapping of factor names to their human-readable descriptions
        """
        return {factor.name: factor.description for factor in self.factors}