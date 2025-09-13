"""
Domain Layer - Login Frequency Health Factor
Business logic for calculating login frequency scores
"""

from typing import List
from datetime import datetime, timedelta

from domain.models import Customer, CustomerEvent, FactorScore
from domain.health_factors.base_factor import HealthFactor


class LoginFrequencyFactor(HealthFactor):
    """Login frequency health factor - measures user engagement patterns"""
    
    @property
    def name(self) -> str:
        return "login_frequency"
    
    @property
    def weight(self) -> float:
        return 0.25
    
    @property
    def description(self) -> str:
        return "Measures user engagement through login activity patterns"
    
    def calculate_score(self, customer: Customer, events: List[CustomerEvent]) -> FactorScore:
        """Calculate login frequency score based on recent login events"""
        
        # Filter login events from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_logins = [
            event for event in events 
            if event.event_type == "login" and event.timestamp >= thirty_days_ago
        ]
        
        login_count = len(recent_logins)
        expected_logins = 20  # Expected logins per month for healthy customer
        
        # Calculate base score
        score = min(100.0, (login_count / expected_logins) * 100) if expected_logins > 0 else 0
        
        # Calculate trend (recent 15 days vs previous 15 days)
        fifteen_days_ago = datetime.utcnow() - timedelta(days=15)
        recent_15_days = [
            event for event in recent_logins 
            if event.timestamp >= fifteen_days_ago
        ]
        
        older_logins = login_count - len(recent_15_days)
        recent_logins_count = len(recent_15_days)
        
        if recent_logins_count > older_logins:
            trend = "improving"
        elif recent_logins_count < older_logins:
            trend = "declining"
        else:
            trend = "stable"
        
        metadata = {
            "expected_logins": expected_logins,
            "recent_activity": recent_logins_count,
            "previous_activity": older_logins
        }
        
        return FactorScore(
            score=score,
            value=login_count,
            description=f"{login_count} logins in last 30 days",
            trend=trend,
            metadata=metadata
        )
    
    def generate_recommendations(self, score: FactorScore, customer: Customer) -> List[str]:
        """Generate login frequency recommendations"""
        recommendations = []
        
        if score.score < 30:
            recommendations.append("CRITICAL: Schedule immediate check-in call to understand usage barriers")
            recommendations.append("Consider personalized re-onboarding program")
        elif score.score < 60:
            recommendations.append("Increase user engagement with personalized feature highlights")
            recommendations.append("Send usage tips and best practices via email")
        elif score.score >= 80:
            recommendations.append("Excellent engagement! Consider asking for case study or testimonial")
        
        return recommendations