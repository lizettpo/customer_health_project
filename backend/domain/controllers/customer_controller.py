"""
Controller Layer - Customer Controller
Loads data into memory and coordinates it (not just calling DB every time)
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from data.repositories import CustomerRepository, EventRepository, HealthScoreRepository
from domain.exceptions import CustomerNotFoundError


class CustomerController:
    """Controller that LOADS DATA and keeps it in memory for coordination"""
    _instance = None
    _initialized = False
    
    def __new__(cls, db: Session = None):
        if cls._instance is None:
            cls._instance = super(CustomerController, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, db: Session):
        if not self._initialized:
            self.customer_repo = CustomerRepository(db)
            self.event_repo = EventRepository(db)
            self.health_score_repo = HealthScoreRepository(db)
            
            # Data will be loaded here when needed
            self._loaded_customers = None
            self._loaded_health_scores = None
            CustomerController._initialized = True
    
    def get_customers_with_health_scores(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        health_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        LOADS DATA ONCE: Load customers and health scores, then coordinate in memory
        """
        
        # 🔥 LOAD CUSTOMERS DATA - Load once and store
        if health_status:
            loaded_customers = self.customer_repo.get_by_health_status(health_status)
            # Apply pagination to loaded data
            if offset:
                loaded_customers = loaded_customers[offset:]
            if limit:
                loaded_customers = loaded_customers[:limit]
        else:
            loaded_customers = self.customer_repo.get_all(limit=limit, offset=offset)
        
        # 🔥 LOAD ALL HEALTH SCORES DATA - Load once for all customers
        customer_ids = [customer.id for customer in loaded_customers]
        loaded_health_scores = {}
        
        for customer_id in customer_ids:
            health_score = self.health_score_repo.get_latest_by_customer(customer_id)
            loaded_health_scores[customer_id] = health_score
        
        # 🔥 COORDINATE LOADED DATA - Work with loaded data in memory
        result = []
        for customer in loaded_customers:
            health_score = loaded_health_scores.get(customer.id)
            
            # FORMAT loaded data
            customer_data = {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "company": customer.company,
                "segment": customer.segment,
                "created_at": customer.created_at.isoformat() if customer.created_at else None,
                "last_activity": customer.last_activity.isoformat() if customer.last_activity else None,
                "health_score": health_score.score if health_score else 0,
                "health_status": health_score.status if health_score else "unknown"
            }
            result.append(customer_data)
        
        return result
    
    def get_customer_with_events(self, customer_id: int, days: int = 90) -> Dict[str, Any]:
        """
        LOADS DATA ONCE: Load customer and all their events, coordinate in memory
        """
        
        # 🔥 LOAD CUSTOMER DATA
        loaded_customer = self.customer_repo.get_by_id(customer_id)
        if not loaded_customer:
            raise CustomerNotFoundError(f"Customer {customer_id} not found")
        
        # 🔥 LOAD EVENTS DATA
        loaded_events = self.event_repo.get_recent_events(customer_id, days)
        
        # 🔥 COORDINATE LOADED DATA - Group events by type
        events_by_type = {}
        for event in loaded_events:
            event_type = event.event_type
            if event_type not in events_by_type:
                events_by_type[event_type] = []
            events_by_type[event_type].append(event)
        
        # 🔥 FORMAT COORDINATED DATA
        return {
            "customer": {
                "id": loaded_customer.id,
                "name": loaded_customer.name,
                "email": loaded_customer.email,
                "company": loaded_customer.company,
                "segment": loaded_customer.segment
            },
            "events_summary": {
                "total_events": len(loaded_events),
                "events_by_type": {
                    event_type: len(events) 
                    for event_type, events in events_by_type.items()
                },
                "latest_events": loaded_events[:5]  # Last 5 events
            }
        }
    
    def get_customer_by_id(self, customer_id: int):
        """
        LOADS DATA: Load and validate customer
        """
        # 🔥 LOAD CUSTOMER DATA
        loaded_customer = self.customer_repo.get_by_id(customer_id)
        if not loaded_customer:
            raise CustomerNotFoundError(f"Customer {customer_id} not found")
        return loaded_customer
    
    def record_customer_event(
        self,
        customer_id: int,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        LOADS DATA + SAVES: Load customer, save event, update data
        """
        
        # 🔥 LOAD CUSTOMER DATA - Validate customer exists
        loaded_customer = self.get_customer_by_id(customer_id)
        
        # 🔥 SAVE NEW DATA - Create and save event
        saved_event = self.event_repo.create_event(
            customer_id=customer_id,
            event_type=event_type,
            event_data=event_data or {},
            timestamp=timestamp or datetime.utcnow()
        )
        
        # 🔥 UPDATE LOADED DATA - Update customer's last activity
        self.customer_repo.update_last_activity(customer_id, saved_event.timestamp)
        
        # FORMAT response with loaded data
        return {
            "message": "Event recorded successfully",
            "event_id": saved_event.id,
            "customer_id": loaded_customer.id,
            "customer_name": loaded_customer.name,
            "event_type": event_type,
            "timestamp": saved_event.timestamp.isoformat() if saved_event.timestamp else None
        }
    
    def get_customer_count(self) -> int:
        """
        LOADS DATA: Get count (could cache this)
        """
        # 🔥 LOAD COUNT DATA
        return self.customer_repo.count()