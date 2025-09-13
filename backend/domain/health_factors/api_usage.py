"""
Domain Layer - API Usage Health Factor
Business logic for calculating API usage scores
"""

from typing import List
from datetime import datetime, timedelta

from domain.models import Customer, CustomerEvent, FactorScore
from domain.health_factors.base_factor import HealthFactor


class ApiUsageFactor(HealthFactor):
    """
    API usage health factor - measures integration depth and automation adoption.
    
    This factor evaluates how well customers are utilizing the API to integrate
    with their systems. Higher API usage typically indicates deeper integration,
    automated workflows, and higher customer value realization.
    
    Scoring criteria:
    - Enterprise customers expected: 1000+ API calls/month
    - SMB customers expected: 500+ API calls/month  
    - Startup customers expected: 200+ API calls/month
    - Includes trend analysis and error rate considerations
    """
    
    @property
    def name(self) -> str:
        """
        Returns the unique identifier for this factor.
        
        Returns:
            str: 'api_usage'
        """
        return "api_usage"
    
    @property
    def weight(self) -> float:
        """
        Returns the weight of this factor in overall health score calculation.
        
        Returns:
            float: 0.15 (15% of total health score)
        """
        return 0.15
    
    @property
    def description(self) -> str:
        """
        Returns a description of what this factor measures.
        
        Returns:
            str: Description of API usage pattern analysis
        """
        return "Measures integration depth through API usage patterns"
    
    def calculate_score(self, customer: Customer, events: List[CustomerEvent]) -> FactorScore:
        """
        Calculate API usage score based on segment-specific expectations.
        
        Analyzes API call frequency, trends, error rates, and usage patterns
        to determine how well the customer is utilizing API integrations.
        
        Args:
            customer: Customer entity with segment information
            events: List of customer events (filtered to last 90 days)
            
        Returns:
            FactorScore: Score (0-100) with metadata including:
                - api_call_count: Total API calls in analysis period
                - expected_calls: Expected calls based on customer segment
                - error_rate: Percentage of failed API calls
                - endpoints: Dictionary of endpoint usage
                - trend: 'improving', 'declining', or 'stable'
                - recent_calls: API calls in last 15 days
        """
        
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
        score = min(100.0, (api_call_count / expected_calls) * 100) if expected_calls > 0 else 0
        
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
        """
        Generate API usage recommendations based on score and customer context.
        
        Provides actionable recommendations to improve API adoption and integration
        depth based on current usage patterns and customer segment.
        
        Args:
            score: FactorScore containing API usage metrics and metadata
            customer: Customer entity for segment-specific recommendations
            
        Returns:
            List[str]: Actionable recommendations such as:
                - Technical consultation for low usage
                - Developer onboarding for moderate usage
                - Upselling opportunities for high usage
                - Case study opportunities for excellent usage
        """
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