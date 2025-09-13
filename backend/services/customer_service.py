"""
Service Layer - Customer Service

This module implements the Customer Service, which serves as the orchestration layer
between the API endpoints and the domain controllers in the Clean Architecture.
The service layer coordinates business workflows, manages transactions, and provides
a clean interface for customer-related operations.

"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from domain.controllers.customer_controller import CustomerController


class CustomerService:
    """
    Service layer for customer operations - pure orchestration.
    
    This service provides a clean API for customer-related operations
    by orchestrating calls to the appropriate controllers. It follows the
    service layer pattern where business logic is delegated to controllers
    and the service focuses on coordination and transaction management.
    """
    
    def __init__(self, db: Session):
        """
        Initialize customer service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.customer_controller = CustomerController(db)
    
    def get_customers_with_health_scores(
        self,
        health_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get customers with their latest health scores.
        
        Retrieves all customers along with their most recent health score
        calculations, optionally filtered by health status.
        
        Args:
            health_status: Optional health status filter ('healthy', 'at_risk', 'critical')
            
        Returns:
            List[Dict[str, Any]]: List of customer data dictionaries containing:
                - Customer basic information (id, name, email, company, segment)
                - Latest health score and status
                - Calculation timestamp
                
        Raises:
            DatabaseError: If database query fails
        """
        return self.customer_controller.get_customers_with_health_scores(
            health_status=health_status
        )
    
    def get_customer_by_id(self, customer_id: int):
        """
        Get customer by ID.
        
        Args:
            customer_id: Unique customer identifier
            
        Returns:
            Customer: Customer domain entity if found
            
        Raises:
            CustomerNotFoundError: If customer doesn't exist
        """
        return self.customer_controller.get_customer_by_id(customer_id)
    
    def record_event(
        self,
        customer_id: int,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Record customer event.
        
        Records a new customer event and triggers background health score
        recalculation if the event type affects health metrics.
        
        Args:
            customer_id: ID of the customer the event belongs to
            event_type: Type of event (e.g., 'api_call', 'login', 'payment', 'feature_use')
            event_data: Optional dictionary containing event-specific data
            timestamp: Optional event timestamp (defaults to current time)
            
        Returns:
            Dict[str, Any]: Event recording confirmation containing:
                - Event ID
                - Success status
                - Any additional processing information
                
        Raises:
            CustomerNotFoundError: If customer doesn't exist
            InvalidEventDataError: If event data is malformed
        """
        return self.customer_controller.record_customer_event(
            customer_id=customer_id,
            event_type=event_type,
            event_data=event_data,
            timestamp=timestamp
        )
    
    def get_customer_events(self, customer_id: int, days: int = 90):
        """
        Get customer events.
        
        Retrieves recent customer events for analysis or display purposes.
        
        Args:
            customer_id: ID of the customer
            days: Number of days to look back for events (default: 90)
            
        Returns:
            Dict containing customer information and event summary
            
        Raises:
            CustomerNotFoundError: If customer doesn't exist
        """
        return self.customer_controller.get_customer_events(customer_id, days)