"""
Domain Layer - Payment Timeliness Health Factor
Business logic for calculating payment timeliness scores
"""

from typing import List
from datetime import datetime, timedelta

from domain.models import Customer, CustomerEvent, FactorScore
from domain.health_factors.base import HealthFactor


class PaymentTimelinessFactor(HealthFactor):
    """Payment timeliness health factor - measures financial health signals"""
    
    @property
    def name(self) -> str:
        return "payment_timeliness"
    
    @property
    def weight(self) -> float:
        return 0.15
    
    @property
    def description(self) -> str:
        return "Measures financial health through payment behavior patterns"
    
    def calculate_score(self, customer: Customer, events: List[CustomerEvent]) -> FactorScore:
        """Calculate payment timeliness score based on payment history"""
        
        # Filter payment events from last 90 days
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        payment_events = [
            event for event in events 
            if event.event_type == "payment" and event.timestamp >= ninety_days_ago
        ]
        
        if not payment_events:
            # No payment history - neutral score for new customers
            metadata = {
                "total_payments": 0,
                "payment_methods": {},
                "average_amount": 0
            }
            return FactorScore(
                score=70.0,
                value=0,
                description="No recent payment history",
                metadata=metadata
            )
        
        # Analyze payment patterns
        on_time_payments = 0
        late_payments = 0
        overdue_payments = 0
        payment_methods = {}
        total_amount = 0
        
        for event in payment_events:
            if event.event_data:
                status = event.get_payment_status()
                method = event.event_data.get('payment_method', 'unknown')
                amount = event.event_data.get('amount', 0)
                
                if status == 'paid_on_time':
                    on_time_payments += 1
                elif status == 'paid_late':
                    late_payments += 1
                elif status == 'overdue':
                    overdue_payments += 1
                
                payment_methods[method] = payment_methods.get(method, 0) + 1
                total_amount += amount
        
        total_payments = len(payment_events)
        on_time_percentage = (on_time_payments / total_payments) * 100
        average_amount = total_amount / total_payments if total_payments > 0 else 0
        
        # Score based on on-time percentage with penalties
        score = on_time_percentage
        if overdue_payments > 0:
            score = max(0.0, score - (overdue_payments * 15))
        
        metadata = {
            "total_payments": total_payments,
            "late_payments": late_payments,
            "overdue_payments": overdue_payments,
            "on_time_percentage": round(on_time_percentage, 1),
            "payment_methods": payment_methods,
            "average_amount": round(average_amount, 2)
        }
        
        return FactorScore(
            score=score,
            value=on_time_payments,
            description=f"{on_time_percentage:.1f}% payments on time ({on_time_payments}/{total_payments})",
            metadata=metadata
        )
    
    def generate_recommendations(self, score: FactorScore, customer: Customer) -> List[str]:
        """Generate payment timeliness recommendations"""
        recommendations = []
        
        if score.score < 50:
            recommendations.append("CRITICAL: Payment issues detected - contact customer immediately")
            recommendations.append("Offer payment plan or billing support")
        elif score.score < 80:
            recommendations.append("Review billing process and consider payment automation")
            recommendations.append("Send payment reminders and offer autopay setup")
        elif score.score >= 95:
            recommendations.append("Excellent payment history - consider offering payment discounts")
        
        return recommendations