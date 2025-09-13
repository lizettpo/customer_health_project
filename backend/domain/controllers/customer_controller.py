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
        Get customers from memory store for instant access
        """
        from domain.memory_store import memory_store
        return memory_store.get_all_customers(health_status=health_status)
    
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
        Get customer from memory store with fallback to database
        """
        from domain.memory_store import memory_store
        customer = memory_store.get_customer_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"Customer {customer_id} not found")
        return customer
    
    def record_customer_event(
        self,
        customer_id: int,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Record event using memory store - updates both memory and database
        """
        from domain.memory_store import memory_store

        self._validate_event_data(event_type, event_data or {})

        # Use memory store to add event (handles database + memory updates)
        return memory_store.add_customer_event(
            customer_id=customer_id,
            event_type=event_type,
            event_data=event_data or {},
            timestamp=timestamp
        )
    
    def get_customer_count(self) -> int:
        """
        LOADS DATA: Get count (could cache this)
        """
        return self.customer_repo.count()
    
    def get_customer_events(self, customer_id: int, days: int = 90) -> List[Dict[str, Any]]:
        """
        Get customer events from memory store
        """
        from domain.memory_store import memory_store

        # Validate customer exists
        customer = memory_store.get_customer_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"Customer {customer_id} not found")

        return memory_store.get_customer_events(customer_id, days)

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