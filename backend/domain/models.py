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
        """Check if customer is enterprise segment"""
        return self.segment.lower() == "enterprise"
    
    def is_new_customer(self, days: int = 30) -> bool:
        """Check if customer is new (created within specified days)"""
        if not self.created_at:
            return False
        return (datetime.utcnow() - self.created_at).days <= days
    
    def get_expected_api_calls(self) -> int:
        """Get expected API calls based on customer segment"""
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
        """Check if event occurred within specified days"""
        return (datetime.utcnow() - self.timestamp).days <= days
    
    def get_feature_name(self) -> Optional[str]:
        """Extract feature name from feature use events"""
        if self.event_type == "feature_use" and self.event_data:
            return self.event_data.get('feature_name')
        return None
    
    def get_payment_status(self) -> Optional[str]:
        """Extract payment status from payment events"""
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
        if not 0 <= self.score <= 100:
            raise ValueError(f"Health score must be between 0 and 100, got {self.score}")
    
    def is_healthy(self) -> bool:
        """Check if customer is in healthy status"""
        return self.status == "healthy"
    
    def is_at_risk(self) -> bool:
        """Check if customer is at risk"""
        return self.status == "at_risk"
    
    def is_critical(self) -> bool:
        """Check if customer is critical"""
        return self.status == "critical"
    
    def get_lowest_factor(self) -> tuple[str, FactorScore]:
        """Get the factor with the lowest score"""
        return min(self.factors.items(), key=lambda x: x[1].score)
    
    def get_highest_factor(self) -> tuple[str, FactorScore]:
        """Get the factor with the highest score"""
        return max(self.factors.items(), key=lambda x: x[1].score)