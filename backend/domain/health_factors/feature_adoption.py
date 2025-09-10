"""
Domain Layer - Feature Adoption Health Factor
Business logic for calculating feature adoption scores
"""

from typing import List
from datetime import datetime, timedelta

from domain.models import Customer, CustomerEvent, FactorScore
from domain.health_factors.base import HealthFactor


class FeatureAdoptionFactor(HealthFactor):
    """Feature adoption health factor - measures platform utilization depth"""
    
    @property
    def name(self) -> str:
        return "feature_adoption"
    
    @property
    def weight(self) -> float:
        return 0.25
    
    @property
    def description(self) -> str:
        return "Measures depth of platform utilization through feature usage"
    
    def calculate_score(self, customer: Customer, events: List[CustomerEvent]) -> FactorScore:
        """Calculate feature adoption score based on unique features used"""
        
        # Filter feature usage events from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        feature_events = [
            event for event in events 
            if event.event_type == "feature_use" and event.timestamp >= thirty_days_ago
        ]
        
        # Extract unique features used
        unique_features = set()
        feature_usage_count = {}
        
        for event in feature_events:
            feature_name = event.get_feature_name()
            if feature_name:
                unique_features.add(feature_name)
                feature_usage_count[feature_name] = feature_usage_count.get(feature_name, 0) + 1
        
        # Calculate score
        expected_features = 8
        score = min(100.0, (len(unique_features) / expected_features) * 100)
        
        # Identify most and least used features
        most_used = max(feature_usage_count, key=feature_usage_count.get) if feature_usage_count else None
        least_used = min(feature_usage_count, key=feature_usage_count.get) if feature_usage_count else None
        
        metadata = {
            "expected_features": expected_features,
            "features_used": list(unique_features),
            "feature_usage_count": feature_usage_count,
            "most_used_feature": most_used,
            "least_used_feature": least_used
        }
        
        return FactorScore(
            score=score,
            value=len(unique_features),
            description=f"{len(unique_features)} unique features used in last 30 days",
            metadata=metadata
        )
    
    def generate_recommendations(self, score: FactorScore, customer: Customer) -> List[str]:
        """Generate feature adoption recommendations"""
        recommendations = []
        
        if score.score < 30:
            recommendations.append("CRITICAL: Feature adoption is very low - schedule onboarding review")
            recommendations.append("Provide guided tour of key features relevant to their use case")
        elif score.score < 60:
            recommendations.append("Schedule product demo to showcase unused features")
            recommendations.append("Send targeted feature education emails")
        elif score.score >= 80:
            recommendations.append("Great feature adoption! Consider advanced feature training")
        
        return recommendations