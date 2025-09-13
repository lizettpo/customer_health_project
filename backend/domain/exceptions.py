"""
Domain Layer - Custom Exceptions as Enums
All domain-specific exceptions organized as enums
"""

from enum import Enum


class DomainError(Exception):
    """
    Base exception for all domain errors.
    
    This is the base class for all domain-specific exceptions in the system.
    It provides structured error handling with error codes, messages, and additional details.
    
    Attributes:
        error_code: Enum value representing the specific error type
        message: Human-readable error message
        details: Additional error context as a dictionary
    """
    
    def __init__(self, error_code, message: str = None, details: dict = None):
        """
        Initialize domain error.
        
        Args:
            error_code: Enum value from one of the error code classes
            message: Optional custom error message. If None, uses error_code.value
            details: Optional dictionary with additional error context
        """
        self.error_code = error_code
        self.message = message or error_code.value
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self):
        """
        String representation of the error.
        
        Returns:
            str: Formatted error string with error code name and message
        """
        return f"[{self.error_code.name}] {self.message}"


class CustomerErrorCode(Enum):
    """
    Customer-related error codes.
    
    These error codes are used when customer operations fail due to various reasons
    such as validation, access control, or data integrity issues.
    """
    CUSTOMER_NOT_FOUND = "Customer not found"
    INVALID_CUSTOMER_DATA = "Invalid customer data provided"
    CUSTOMER_EMAIL_EXISTS = "Customer email already exists"
    CUSTOMER_INACTIVE = "Customer account is inactive"
    CUSTOMER_ACCESS_DENIED = "Access denied for customer"


class HealthScoreErrorCode(Enum):
    """Health score calculation error codes"""
    CALCULATION_FAILED = "Health score calculation failed"
    INVALID_SCORE_RANGE = "Health score must be between 0 and 100"
    INSUFFICIENT_DATA = "Insufficient data for health score calculation"
    FACTOR_WEIGHTS_INVALID = "Factor weights must sum to 1.0"
    SCORE_SAVE_FAILED = "Failed to save health score"


class EventErrorCode(Enum):
    """Event-related error codes"""
    INVALID_EVENT_TYPE = "Invalid event type"
    INVALID_EVENT_DATA = "Invalid event data format"
    EVENT_TIMESTAMP_INVALID = "Event timestamp is invalid"
    EVENT_SAVE_FAILED = "Failed to save event"
    EVENT_NOT_FOUND = "Event not found"


class FactorErrorCode(Enum):
    """Health factor calculation error codes"""
    LOGIN_CALCULATION_FAILED = "Login frequency calculation failed"
    FEATURE_CALCULATION_FAILED = "Feature adoption calculation failed"
    SUPPORT_CALCULATION_FAILED = "Support ticket calculation failed"
    PAYMENT_CALCULATION_FAILED = "Payment timeliness calculation failed"
    API_CALCULATION_FAILED = "API usage calculation failed"
    FACTOR_NOT_FOUND = "Health factor not found"
    FACTOR_CONFIG_INVALID = "Health factor configuration invalid"


class DataErrorCode(Enum):
    """Data layer error codes"""
    DATABASE_CONNECTION_FAILED = "Database connection failed"
    QUERY_EXECUTION_FAILED = "Database query execution failed"
    DATA_INTEGRITY_ERROR = "Data integrity constraint violation"
    REPOSITORY_ERROR = "Repository operation failed"
    TRANSACTION_FAILED = "Database transaction failed"


# Specific Exception Classes using the enums
class CustomerNotFoundError(DomainError):
    """
    Raised when a customer is not found.
    
    This exception is typically raised during database queries when attempting
    to retrieve a customer that doesn't exist in the system.
    """
    
    def __init__(self, customer_id: int = None, message: str = None):
        """
        Initialize customer not found error.
        
        Args:
            customer_id: The ID of the customer that was not found
            message: Optional custom error message
        """
        details = {"customer_id": customer_id} if customer_id else {}
        custom_message = message or f"Customer {customer_id} not found" if customer_id else None
        super().__init__(CustomerErrorCode.CUSTOMER_NOT_FOUND, custom_message, details)


class InvalidCustomerDataError(DomainError):
    """Raised when customer data is invalid"""
    
    def __init__(self, field: str = None, value: any = None, message: str = None):
        details = {"field": field, "value": value} if field else {}
        custom_message = message or f"Invalid customer data: {field} = {value}" if field else None
        super().__init__(CustomerErrorCode.INVALID_CUSTOMER_DATA, custom_message, details)


class InvalidHealthScoreError(DomainError):
    """Raised when health score calculation fails"""
    
    def __init__(self, score: float = None, reason: str = None):
        details = {"score": score, "reason": reason}
        custom_message = f"Invalid health score: {score} - {reason}" if score and reason else None
        super().__init__(HealthScoreErrorCode.CALCULATION_FAILED, custom_message, details)


class InvalidEventDataError(DomainError):
    """Raised when event data is invalid"""
    
    def __init__(self, event_type: str = None, field: str = None, message: str = None):
        details = {"event_type": event_type, "field": field}
        custom_message = message or f"Invalid event data for {event_type}: {field}" if event_type and field else None
        super().__init__(EventErrorCode.INVALID_EVENT_DATA, custom_message, details)


class FactorCalculationError(DomainError):
    """Raised when a health factor calculation fails"""
    
    def __init__(self, factor_name: str, error_code: FactorErrorCode = None, reason: str = None):
        details = {"factor_name": factor_name, "reason": reason}
        error_code = error_code or FactorErrorCode.LOGIN_CALCULATION_FAILED  # Default
        custom_message = f"Factor calculation failed for {factor_name}: {reason}" if reason else None
        super().__init__(error_code, custom_message, details)


class DatabaseError(DomainError):
    """Raised when database operations fail"""
    
    def __init__(self, operation: str = None, table: str = None, error_code: DataErrorCode = None):
        details = {"operation": operation, "table": table}
        error_code = error_code or DataErrorCode.REPOSITORY_ERROR
        custom_message = f"Database error during {operation} on {table}" if operation and table else None
        super().__init__(error_code, custom_message, details)


# Helper functions to create specific exceptions
def customer_not_found(customer_id: int) -> CustomerNotFoundError:
    """Helper to create customer not found exception"""
    return CustomerNotFoundError(customer_id)


def invalid_customer_email(email: str) -> InvalidCustomerDataError:
    """Helper to create invalid email exception"""
    return InvalidCustomerDataError("email", email, f"Invalid email format: {email}")


def invalid_health_score_range(score: float) -> InvalidHealthScoreError:
    """Helper to create invalid score range exception"""
    return InvalidHealthScoreError(score, "Score must be between 0 and 100")


def factor_calculation_failed(factor_name: str, reason: str) -> FactorCalculationError:
    """Helper to create factor calculation error"""
    factor_error_map = {
        "login_frequency": FactorErrorCode.LOGIN_CALCULATION_FAILED,
        "feature_adoption": FactorErrorCode.FEATURE_CALCULATION_FAILED,
        "support_tickets": FactorErrorCode.SUPPORT_CALCULATION_FAILED,
        "payment_timeliness": FactorErrorCode.PAYMENT_CALCULATION_FAILED,
        "api_usage": FactorErrorCode.API_CALCULATION_FAILED
    }
    error_code = factor_error_map.get(factor_name, FactorErrorCode.FACTOR_NOT_FOUND)
    return FactorCalculationError(factor_name, error_code, reason)


def database_operation_failed(operation: str, table: str = None) -> DatabaseError:
    """Helper to create database operation error"""
    return DatabaseError(operation, table, DataErrorCode.QUERY_EXECUTION_FAILED)