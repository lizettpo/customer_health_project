"""
Domain Layer - Abstract Base Class for Health Factors

This module defines the abstract base class for all health factor implementations
in the Customer Health Scoring System. Health factors are pluggable components
that analyze specific aspects of customer behavior and contribute to the overall
health score calculation.

Design Principles:
- Strategy Pattern: Interchangeable scoring algorithms
- Template Method: Consistent calculation workflow
- Single Responsibility: Each factor analyzes one behavioral aspect
- Open/Closed Principle: Easy to add new factors without modifying existing code

Health Factor Architecture:
Each health factor is a self-contained component that:
1. Analyzes customer events and metadata
2. Produces a standardized score (0-100)
3. Provides calculation metadata and trends
4. Generates actionable recommendations
5. Maintains consistent weight in overall calculation

Available Health Factors:
- APIUsageFactor: API call frequency and patterns (weight: 0.30)
- LoginFrequencyFactor: User engagement and activity (weight: 0.20)
- PaymentTimelinessFactor: Payment behavior and history (weight: 0.25)
- FeatureAdoptionFactor: Feature usage and adoption (weight: 0.15)
- SupportTicketsFactor: Support interaction patterns (weight: 0.10)

Implementation Guidelines:
- Score calculation should be deterministic and repeatable
- Handle edge cases (no data, invalid data) gracefully
- Provide meaningful recommendations based on score ranges
- Consider customer segment in expectations and scoring
- Use appropriate time windows for event analysis

Usage:
    from domain.health_factors import APIUsageFactor

    factor = APIUsageFactor()
    score = factor.calculate_score(customer, recent_events)
    recommendations = factor.generate_recommendations(score, customer)

Author: Customer Health Team
Architecture Pattern: Strategy Pattern + Template Method
Layer: Domain Layer (Clean Architecture)
"""

from abc import ABC, abstractmethod
from typing import List, Optional
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