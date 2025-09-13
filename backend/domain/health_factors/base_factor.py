"""
Domain Layer - Abstract Base Class for Health Factors
Defines the contract for all health factor implementations
"""

from abc import ABC, abstractmethod
from typing import List
from domain.models import Customer, CustomerEvent, FactorScore


class HealthFactor(ABC):
    """
    Abstract base class for health factor calculations.
    
    This class defines the contract that all health factors must implement.
    Health factors are individual components that contribute to the overall
    customer health score, such as API usage, login frequency, payment behavior, etc.
    
    Each factor produces a score between 0-100 and provides recommendations
    based on customer behavior patterns.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique identifier for this factor.
        
        Returns:
            str: A unique string identifier used to reference this factor
                 in calculations and storage (e.g., 'api_usage', 'login_frequency')
        """
        pass
    
    @property
    @abstractmethod
    def weight(self) -> float:
        """
        Weight of this factor in overall health score calculation.
        
        Returns:
            float: Weight value between 0.0 and 1.0 representing the importance
                   of this factor. All factor weights should sum to 1.0.
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        Human-readable description of what this factor measures.
        
        Returns:
            str: A clear description of the customer behavior or metric
                 that this factor analyzes and scores.
        """
        pass
    
    @abstractmethod
    def calculate_score(self, customer: Customer, events: List[CustomerEvent]) -> FactorScore:
        """
        Calculate the factor score based on customer data and events.
        
        This is the core method that analyzes customer behavior and produces
        a standardized score between 0-100 along with supporting metadata.
        
        Args:
            customer: The customer entity containing basic customer information
            events: List of relevant customer events filtered by the caller
                   (typically last 90 days of events)
            
        Returns:
            FactorScore: Contains the calculated score (0-100), descriptive text,
                        trend information, and metadata dictionary with calculation details
                        
        Raises:
            FactorCalculationError: If calculation fails due to invalid data or computation errors
        """
        pass
    
    @abstractmethod
    def generate_recommendations(self, score: FactorScore, customer: Customer) -> List[str]:
        """
        Generate actionable recommendations based on factor score.
        
        Analyzes the calculated score and customer context to provide specific,
        actionable suggestions for improving this health factor.
        
        Args:
            score: The calculated FactorScore containing score and metadata
            customer: The customer entity for additional context
            
        Returns:
            List[str]: List of actionable recommendation strings tailored to
                      the customer's current performance in this factor
        """
        pass