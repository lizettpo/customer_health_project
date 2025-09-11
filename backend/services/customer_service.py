"""
Service Layer - Customer Service
Pure orchestration - calls controllers only
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from domain.controllers.customer_controller import CustomerController


class CustomerService:
    """Service layer for customer operations - pure orchestration"""
    
    def __init__(self, db: Session):
        self.customer_controller = CustomerController(db)
    
    def get_customers_with_health_scores(
        self,

        health_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get customers with their latest health scores"""
        return self.customer_controller.get_customers_with_health_scores(
            health_status=health_status
        )
    
    def get_customer_by_id(self, customer_id: int):
        """Get customer by ID"""
        return self.customer_controller.get_customer_by_id(customer_id)
    
    def record_event(
        self,
        customer_id: int,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Record customer event"""
        return self.customer_controller.record_customer_event(
            customer_id=customer_id,
            event_type=event_type,
            event_data=event_data,
            timestamp=timestamp
        )
    
    def get_customer_events(self, customer_id: int, days: int = 90):
        """Get customer events"""
        return self.customer_controller.get_customer_events(customer_id, days)