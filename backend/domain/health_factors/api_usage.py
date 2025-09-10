"""
Domain Layer - API Usage Health Factor
Business logic for calculating API usage scores
"""

from typing import List
from datetime import datetime, timedelta

from domain.models import Customer, CustomerEvent, FactorScore
from domain.health_factors.base import HealthFactor


class ApiUsageFactor(HealthFactor):
    """API usage health factor - measures integration depth and automation adoption"""
    
    @property
    def name(self) -> str:
        return "api_usage"
    
    @property
    def weight(self) -> float:
        return 0.15
    
    @property
    def description(self) -> str:
        return "Measures integration depth through API usage patterns"
    
    def calculate_score(self, customer: Customer, events: List[CustomerEvent]) -> FactorScore:
        """Calculate API usage score based on segment-specific expectations"""
        
        # Filter API call events from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        api_events = [
            event for event in events 
            if event.event_type == "api_call" and event.timestamp >= thirty_days_ago
        ]
        
        api_call_count = len(api_events)
        
        # Analyze API usage patterns
        endpoints = {}
        methods = {}
        response_codes = {}
        daily_usage = {}
        
        for event in api_events:
            if event.event_data:
                endpoint = event.event_data.get('endpoint', 'unknown')
                method = event.event_data.get('method', 'GET')
                response_code = event.event_data.get('response_code', 200)
                
                endpoints[endpoint] = endpoints.get(endpoint, 0) + 1
                methods[method] = methods.get(method, 0) + 1
                response_codes[str(response_code)] = response_codes.get(str(response_code), 0) + 1
                
                # Track daily usage
                day = event.timestamp.date().isoformat()
                daily_usage[day] = daily_usage.get(day, 0) + 1
        
        # Calculate score based on customer segment expectations
        expected_calls = customer.get_expected_api_calls()
        score = min(100.0, (api_call_count / expected_calls) * 100)
        
        # Calculate trend
        fifteen_days_ago = datetime.utcnow() - timedelta(days=15)
        recent_15_days = [
            event for event in api_events 
            if event.timestamp >= fifteen_days_ago
        ]
        recent_calls = len(recent_15_days)
        older_calls = api_call_count - recent_calls
        
        if recent_calls > older_calls:
            trend = "improving"
        elif recent_calls < older_calls:
            trend = "declining"
        else:
            trend = "stable"
        
        # Calculate error rate
        error_calls = (response_codes.get('400', 0) + 
                      response_codes.get('401', 0) + 
                      response_codes.get('500', 0))
        error_rate = (error_calls / api_call_count * 100) if api_call_count > 0 else 0
        
        metadata = {
            "expected_calls": expected_calls,
            "endpoints": endpoints,
            "methods": methods,
            "response_codes": response_codes,
            "error_rate": round(error_rate, 2),
            "daily_usage": daily_usage,
            "recent_calls": recent_calls
        }
        
        return FactorScore(
            score=score,
            value=api_call_count,
            description=f"{api_call_count} API calls in last 30 days",
            trend=trend,
            metadata=metadata
        )
    
    def generate_recommendations(self, score: FactorScore, customer: Customer) -> List[str]:
        """Generate API usage recommendations"""
        recommendations = []
        
        if score.score < 30:
            recommendations.append("API adoption is very low - offer technical consultation")
            recommendations.append("Provide API documentation and integration examples")
        elif score.score < 50:
            recommendations.append("Consider integration support or developer onboarding")
        elif score.score > 80 and customer.is_enterprise():
            recommendations.append("High API usage indicates success - consider upselling")
        elif score.score > 90:
            recommendations.append("Excellent API adoption - consider featuring as integration case study")
        
        return recommendations