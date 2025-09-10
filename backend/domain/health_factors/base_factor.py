"""
Domain Layer - Abstract Base Class for Health Factors
Defines the contract for all health factor implementations
"""

from abc import ABC, abstractmethod
from typing import List
from domain.models import Customer, CustomerEvent, FactorScore


class HealthFactor(ABC):
    """Abstract base class for health factor calculations"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this factor"""
        pass
    
    @property
    @abstractmethod
    def weight(self) -> float:
        """Weight of this factor in overall calculation (0.0 to 1.0)"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this factor measures"""
        pass
    
    @abstractmethod
    def calculate_score(self, customer: Customer, events: List[CustomerEvent]) -> FactorScore:
        """
        Calculate the factor score based on customer data and events
        
        Args:
            customer: The customer entity
            events: List of relevant customer events
            
        Returns:
            FactorScore containing the calculated score and metadata
        """
        pass
    
    @abstractmethod
    def generate_recommendations(self, score: FactorScore, customer: Customer) -> List[str]:
        """Generate actionable recommendations based on factor score"""
        pass