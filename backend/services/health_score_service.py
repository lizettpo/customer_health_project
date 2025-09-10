"""
Service Layer - Health Score Service
No business logic - only orchestrates domain and data layer calls
"""

from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

from data.repositories import CustomerRepository, EventRepository, HealthScoreRepository
from domain.calculators import HealthScoreCalculator
from domain.exceptions import CustomerNotFoundError


class HealthScoreService:
    """Service layer for health score operations - no business logic"""
    
    def __init__(self, db: Session):
        self.customer_repo = CustomerRepository(db)
        self.event_repo = EventRepository(db)
        self.health_score_repo = HealthScoreRepository(db)
        self.calculator = HealthScoreCalculator()
    
    def get_customer_health_detail(self, customer_id: int) -> Dict[str, Any]:
        """Get detailed health breakdown - delegates to domain calculator"""
        
        # Get customer from repository
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"Customer {customer_id} not found")
        
        # Calculate fresh health score using domain calculator
        health_score = self.calculate_and_save_health_score(customer_id)
        
        # Get historical scores from repository
        historical_scores = self.health_score_repo.get_historical_scores(customer_id, limit=30)
        
        # Format response
        return {
            "customer_id": customer.id,
            "customer_name": customer.name,
            "overall_score": health_score.score,
            "status": health_score.status,
            "factors": health_score.factors,
            "calculated_at": health_score.calculated_at,
            "historical_scores": [
                {
                    "score": hs.score,
                    "status": hs.status,
                    "calculated_at": hs.calculated_at
                }
                for hs in historical_scores
            ],
            "recommendations": health_score.recommendations
        }
    
    def calculate_and_save_health_score(self, customer_id: int):
        """Calculate and save health score - delegates to domain calculator"""
        
        # Get customer and events from repositories
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"Customer {customer_id} not found")
        
        events = self.event_repo.get_recent_events(customer_id, days=90)
        
        # Calculate health score using domain calculator
        health_score = self.calculator.calculate_health_score(customer, events)
        
        # Save health score using repository
        saved_health_score = self.health_score_repo.save_health_score(health_score)
        
        return saved_health_score
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics - delegates to repositories"""
        
        # Get counts from repositories
        total_customers = self.customer_repo.count()
        healthy_count = self.health_score_repo.count_by_status("healthy")
        at_risk_count = self.health_score_repo.count_by_status("at_risk")
        critical_count = self.health_score_repo.count_by_status("critical")
        average_score = self.health_score_repo.get_average_score()
        
        return {
            "total_customers": total_customers,
            "healthy_customers": healthy_count,
            "at_risk_customers": at_risk_count,
            "critical_customers": critical_count,
            "average_health_score": round(average_score, 2),
            "last_updated": datetime.utcnow()
        }