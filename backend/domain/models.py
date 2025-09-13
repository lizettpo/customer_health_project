"""
Domain Layer - Domain Models
Business entities and value objects
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any


@dataclass
class Customer:
    """Customer domain entity"""
    id: int
    name: str
    email: str
    company: str
    segment: str
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    monthly_revenue: Optional[float] = None
    plan_type: str = "basic"
    created_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    
    def is_enterprise(self) -> bool:
        """
        Check if customer is enterprise segment.
        
        Returns:
            bool: True if customer segment is 'enterprise' (case insensitive)
        """
        return self.segment.lower() == "enterprise"
    
    def is_new_customer(self, days: int = 30) -> bool:
        """
        Check if customer is new (created within specified days).
        
        Args:
            days (int): Number of days to consider as 'new'. Defaults to 30.
            
        Returns:
            bool: True if customer was created within the specified days, 
                  False if created_at is None or customer is older than specified days.
        """
        if not self.created_at:
            return False
        return (datetime.utcnow() - self.created_at).days <= days
    
    def get_expected_api_calls(self) -> int:
        """
        Get expected API calls based on customer segment.
        
        Returns:
            int: Expected monthly API calls based on segment:
                 - Enterprise: 1000 calls
                 - SMB: 500 calls  
                 - Startup: 200 calls
                 - Default: 300 calls for unknown segments
        """
        expectations = {
            "enterprise": 1000,
            "smb": 500,
            "startup": 200
        }
        return expectations.get(self.segment.lower(), 300)


@dataclass
class CustomerEvent:
    """Customer event domain entity"""
    id: Optional[int]
    customer_id: int
    event_type: str
    event_data: Dict[str, Any]
    timestamp: datetime
    
    def is_recent(self, days: int = 30) -> bool:
        """
        Check if event occurred within specified days.
        
        Args:
            days (int): Number of days to consider as 'recent'. Defaults to 30.
            
        Returns:
            bool: True if event timestamp is within the specified days from now.
        """
        return (datetime.utcnow() - self.timestamp).days <= days
    
    def get_feature_name(self) -> Optional[str]:
        """
        Extract feature name from feature use events.
        
        Returns:
            Optional[str]: Feature name if event is 'feature_use' type and has valid data,
                          None otherwise.
        """
        if self.event_type == "feature_use" and self.event_data:
            return self.event_data.get('feature_name')
        return None
    
    def get_payment_status(self) -> Optional[str]:
        """
        Extract payment status from payment events.
        
        Returns:
            Optional[str]: Payment status if event is 'payment' type and has valid data,
                          None otherwise. Common statuses: 'paid_on_time', 'paid_late', 'overdue', 'failed'.
        """
        if self.event_type == "payment" and self.event_data:
            return self.event_data.get('status')
        return None


@dataclass
class FactorScore:
    """Value object for health factor scores"""
    score: float
    value: Any
    description: str
    trend: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """
        Post-initialization validation and setup.
        
        Raises:
            ValueError: If score is not between 0 and 100.
        """
        if self.metadata is None:
            self.metadata = {}
        if not 0 <= self.score <= 100:
            raise ValueError(f"Score must be between 0 and 100, got {self.score}")


@dataclass
class HealthScore:
    """Health score domain entity"""
    id: Optional[int]
    customer_id: int
    score: float
    status: str
    factors: Dict[str, FactorScore]
    recommendations: List[str]
    calculated_at: datetime
    
    def __post_init__(self):
        """
        Post-initialization validation.
        
        Raises:
            ValueError: If overall health score is not between 0 and 100.
        """
        if not 0 <= self.score <= 100:
            raise ValueError(f"Health score must be between 0 and 100, got {self.score}")
    
    def is_healthy(self) -> bool:
        """
        Check if customer is in healthy status.
        
        Returns:
            bool: True if status is 'healthy', False otherwise.
        """
        return self.status == "healthy"
    
    def is_at_risk(self) -> bool:
        """
        Check if customer is at risk.
        
        Returns:
            bool: True if status is 'at_risk', False otherwise.
        """
        return self.status == "at_risk"
    
    def is_critical(self) -> bool:
        """
        Check if customer is critical.
        
        Returns:
            bool: True if status is 'critical', False otherwise.
        """
        return self.status == "critical"
    
    def get_lowest_factor(self) -> tuple[str, FactorScore]:
        """
        Get the factor with the lowest score.
        
        Returns:
            tuple[str, FactorScore]: A tuple containing the factor name and its FactorScore
                                   representing the lowest scoring health factor.
                                   
        Raises:
            ValueError: If no factors are present.
        """
        return min(self.factors.items(), key=lambda x: x[1].score)
    
    def get_highest_factor(self) -> tuple[str, FactorScore]:
        """
        Get the factor with the highest score.
        
        Returns:
            tuple[str, FactorScore]: A tuple containing the factor name and its FactorScore
                                   representing the highest scoring health factor.
                                   
        Raises:
            ValueError: If no factors are present.
        """
        return max(self.factors.items(), key=lambda x: x[1].score)