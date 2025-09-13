"""
Controller Layer - Customer Controller
Loads data into memory and coordinates it (not just calling DB every time)
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from data.repositories import CustomerRepository, EventRepository, HealthScoreRepository
from domain.exceptions import CustomerNotFoundError, InvalidEventDataError


class CustomerController:
    """Controller that LOADS DATA and keeps it in memory for coordination"""
    
    def __init__(self, db: Session):
        self.customer_repo = CustomerRepository(db)
        self.event_repo = EventRepository(db)
        self.health_score_repo = HealthScoreRepository(db)
        
        # Data will be loaded here when needed
        self._loaded_customers = None
        self._loaded_health_scores = None
        self._initialized = True
    
    def get_customers_with_health_scores(
        self,
        health_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        LOADS DATA ONCE: Load customers and use health score controller for calculations
        """
        
        if health_status:
            loaded_customers = self.customer_repo.get_by_health_status(health_status)
        else:
            loaded_customers = self.customer_repo.get_all()
        
        from domain.controllers.health_score_controller import HealthScoreController
        health_controller = HealthScoreController(self.customer_repo.db)
        
        result = []
        for customer in loaded_customers:
            # Get existing health score instead of recalculating
            existing_health_score = self.health_score_repo.get_latest_by_customer(customer.id)
            
            # FORMAT loaded data
            customer_data = {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "company": customer.company,
                "segment": customer.segment,
                "created_at": customer.created_at.isoformat() if customer.created_at else None,
                "last_activity": customer.last_activity.isoformat() if customer.last_activity else None,
                "health_score": existing_health_score.score if existing_health_score else 0,
                "health_status": existing_health_score.status if existing_health_score else "unknown"
            }
            result.append(customer_data)
        
        return result
    
    def get_customer_with_events(self, customer_id: int, days: int = 90) -> Dict[str, Any]:
        """
        LOADS DATA ONCE: Load customer and all their events, coordinate in memory
        """
        
        loaded_customer = self.customer_repo.get_by_id(customer_id)
        if not loaded_customer:
            raise CustomerNotFoundError(f"Customer {customer_id} not found")
        
        loaded_events = self.event_repo.get_recent_events(customer_id, days)
        
        events_by_type = {}
        for event in loaded_events:
            event_type = event.event_type
            if event_type not in events_by_type:
                events_by_type[event_type] = []
            events_by_type[event_type].append(event)
        
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

        self._validate_event_data(event_type, event_data or {})

        loaded_customer = self.get_customer_by_id(customer_id)
        
        saved_event = self.event_repo.create_event(
            customer_id=customer_id,
            event_type=event_type,
            event_data=event_data or {},
            timestamp=timestamp or datetime.utcnow()
        )
        
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
        return self.customer_repo.count()
    
    def get_customer_events(self, customer_id: int, days: int = 90) -> List[Dict[str, Any]]:
        """
        LOADS DATA: Get customer events
        """
        loaded_customer = self.get_customer_by_id(customer_id)
        
        loaded_events = self.event_repo.get_recent_events(customer_id, days)
        
        # FORMAT loaded events
        return [
            {
                "id": event.id,
                "event_type": event.event_type,
                "event_data": event.event_data,
                "timestamp": event.timestamp.isoformat() if event.timestamp else None
            }
            for event in loaded_events
        ]

    def _validate_event_data(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Validate that required fields are present and not empty for each event type.

        Args:
            event_type: The type of event being recorded
            event_data: The event data dictionary to validate

        Raises:
            InvalidEventDataError: If required fields are missing or empty
        """
        def _is_empty(value) -> bool:
            """Check if a value is empty (None, empty string, or whitespace only)"""
            if value is None:
                return True
            if isinstance(value, str):
                return not value.strip()
            return False

        # Define required fields for each event type
        required_fields = {
            "api_call": ["endpoint"],
            "payment": ["amount"],
            "feature_use": ["feature_name"],
            "login": ["ip_address"],
            "support_ticket": []  # No required fields - has defaults
        }

        # Get required fields for this event type
        required = required_fields.get(event_type, [])

        # Check each required field
        missing_fields = []
        for field in required:
            if field not in event_data or _is_empty(event_data[field]):
                missing_fields.append(field)

        # Additional validation for specific fields
        if event_type == "payment" and "amount" in event_data:
            try:
                amount = float(event_data["amount"])
                if amount <= 0:
                    missing_fields.append("amount (must be > 0)")
            except (ValueError, TypeError):
                missing_fields.append("amount (must be a valid number)")

        # Raise error if validation fails
        if missing_fields:
            field_list = ", ".join(missing_fields)
            raise InvalidEventDataError(
                event_type=event_type,
                field=field_list,
                message=f"Required fields missing or empty for {event_type} event: {field_list}"
            )