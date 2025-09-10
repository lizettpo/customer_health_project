"""
Service Layer - Customer Service
No business logic - only orchestrates domain and data layer calls
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from data.repositories import CustomerRepository, EventRepository, HealthScoreRepository
from domain.exceptions import CustomerNotFoundError


class CustomerService:
    """Service layer for customer operations - no business logic"""
    
    def __init__(self, db: Session):
        self.customer_repo = CustomerRepository(db)
        self.event_repo = EventRepository(db)
        self.health_score_repo = HealthScoreRepository(db)
    
    def get_customers_with_health_scores(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        health_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get customers with their latest health scores - delegates to repositories"""
        
        # Get customers from repository
        if health_status:
            customers = self.customer_repo.get_by_health_status(health_status)
            # Apply pagination manually
            if offset:
                customers = customers[offset:]
            if limit:
                customers = customers[:limit]
        else:
            customers = self.customer_repo.get_all(limit=limit, offset=offset)
        
        # Get health scores for each customer
        result = []
        for customer in customers:
            latest_health_score = self.health_score_repo.get_latest_by_customer(customer.id)
            
            customer_data = {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "company": customer.company,
                "segment": customer.segment,
                "created_at": customer.created_at,
                "last_activity": customer.last_activity,
                "health_score": latest_health_score.score if latest_health_score else 0,
                "health_status": latest_health_score.status if latest_health_score else "unknown"
            }
            result.append(customer_data)
        
        return result
    
    def get_customer_by_id(self, customer_id: int):
        """Get customer by ID - delegates to repository"""
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"Customer {customer_id} not found")
        return customer
    
    def record_event(
        self,
        customer_id: int,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Record customer event - delegates to repositories"""
        
        # Check if customer exists
        customer = self.get_customer_by_id(customer_id)
        
        # Create and save event
        event = self.event_repo.create_event(
            customer_id=customer_id,
            event_type=event_type,
            event_data=event_data or {},
            timestamp=timestamp or datetime.utcnow()
        )
        
        # Update customer's last activity
        self.customer_repo.update_last_activity(customer_id, event.timestamp)
        
        return {
            "message": "Event recorded successfully",
            "event_id": event.id,
            "customer_id": customer_id,
            "event_type": event_type,
            "timestamp": event.timestamp
        }
    
    def get_customer_events(self, customer_id: int, days: int = 90):
        """Get customer events - delegates to repository"""
        return self.event_repo.get_recent_events(customer_id, days)