"""
Domain Layer - Custom Exceptions
All domain-specific exceptions
"""


class DomainError(Exception):
    """Base exception for all domain errors"""
    pass


class CustomerNotFoundError(DomainError):
    """Raised when a customer is not found"""
    pass


class InvalidHealthScoreError(DomainError):
    """Raised when health score calculation fails"""
    pass


class InvalidEventDataError(DomainError):
    """Raised when event data is invalid"""
    pass


class FactorCalculationError(DomainError):
    """Raised when a health factor calculation fails"""
    pass


class InvalidCustomerDataError(DomainError):
    """Raised when customer data is invalid"""
    pass