"""
Domain Layer - Support Tickets Health Factor
Business logic for calculating support ticket scores
"""

from typing import List
from datetime import datetime, timedelta

from domain.models import Customer, CustomerEvent, FactorScore
from domain.health_factors.base import HealthFactor


class SupportTicketsFactor(HealthFactor):
    """Support tickets health factor - measures customer friction indicators"""
    
    @property
    def name(self) -> str:
        return "support_tickets"
    
    @property
    def weight(self) -> float:
        return 0.20
    
    @property
    def description(self) -> str:
        return "Measures customer friction through support ticket volume (inverse scoring)"
    
    def calculate_score(self, customer: Customer, events: List[CustomerEvent]) -> FactorScore:
        """Calculate support ticket score (fewer tickets = higher score)"""
        
        # Filter support ticket events from last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        ticket_events = [
            event for event in events 
            if event.event_type == "support_ticket" and event.timestamp >= thirty_days_ago
        ]
        
        ticket_count = len(ticket_events)
        
        # Analyze ticket types and priorities
        ticket_types = {}
        priorities = {'low': 0, 'medium': 0, 'high': 0, 'urgent': 0}
        
        for event in ticket_events:
            if event.event_data:
                ticket_type = event.event_data.get('ticket_type', 'unknown')
                priority = event.event_data.get('priority', 'medium')
                
                ticket_types[ticket_type] = ticket_types.get(ticket_type, 0) + 1
                if priority in priorities:
                    priorities[priority] += 1
        
        # Calculate base score (inverse relationship)
        if ticket_count == 0:
            score = 100.0
        elif ticket_count <= 2:
            score = 80.0
        elif ticket_count <= 4:
            score = 60.0
        elif ticket_count <= 6:
            score = 40.0
        else:
            score = max(10.0, 40.0 - (ticket_count - 6) * 5)
        
        # Apply penalties for high-priority tickets
        urgent_penalty = priorities['urgent'] * 10
        high_penalty = priorities['high'] * 5
        score = max(0.0, score - urgent_penalty - high_penalty)
        
        metadata = {
            "ticket_types": ticket_types,
            "priorities": priorities,
            "interpretation": "Lower ticket count indicates better product experience"
        }
        
        return FactorScore(
            score=score,
            value=ticket_count,
            description=f"{ticket_count} support tickets in last 30 days",
            metadata=metadata
        )
    
    def generate_recommendations(self, score: FactorScore, customer: Customer) -> List[str]:
        """Generate support ticket recommendations"""
        recommendations = []
        
        if score.score < 40:
            recommendations.append("CRITICAL: Very high support volume - investigate recurring issues")
            recommendations.append("Consider dedicated customer success manager")
        elif score.score < 70:
            recommendations.append("Proactive outreach recommended - support ticket volume indicates friction")
            recommendations.append("Review common issues and provide preventive resources")
        elif score.score == 100:
            recommendations.append("Excellent! Zero support tickets indicate smooth experience")
        
        return recommendations