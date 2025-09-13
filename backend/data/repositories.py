"""
Data Layer - Repository Implementations
Database operations and data access
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from data.models import Customer as CustomerModel, CustomerEvent as CustomerEventModel, HealthScore as HealthScoreModel
from domain.models import Customer, CustomerEvent, HealthScore, FactorScore


class CustomerRepository:
    """
    Repository for customer data operations.
    
    Handles all database operations related to customers, providing a clean
    interface between the domain layer and the database. Converts between
    database models and domain entities.
    """
    
    def __init__(self, db: Session):
        """
        Initialize customer repository.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """
        Get customer by ID.
        
        Args:
            customer_id: Unique customer identifier
            
        Returns:
            Optional[Customer]: Customer domain entity if found, None otherwise
        """
        db_customer = self.db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
        if not db_customer:
            return None
        return self._to_domain_model(db_customer)
    
    def get_all(self) -> List[Customer]:
        """
        Get all customers.
        
        Returns:
            List[Customer]: List of all customer domain entities
        """
        query = self.db.query(CustomerModel)
        db_customers = query.all()
        return [self._to_domain_model(customer) for customer in db_customers]
    
    def get_by_health_status(self, status: str) -> List[Customer]:
        """
        Get customers by health status.
        
        Retrieves customers whose latest health score has the specified status.
        
        Args:
            status: Health status to filter by ('healthy', 'at_risk', 'critical')
            
        Returns:
            List[Customer]: List of customer domain entities with matching health status
        """
        # Get health scores by status (one per customer)
        health_scores = self.db.query(HealthScoreModel).filter(
            HealthScoreModel.status == status
        ).all()
        
        customer_ids = [score.customer_id for score in health_scores]
        
        if not customer_ids:
            return []
        
        db_customers = self.db.query(CustomerModel).filter(CustomerModel.id.in_(customer_ids)).all()
        return [self._to_domain_model(customer) for customer in db_customers]
    
    def update_last_activity(self, customer_id: int, timestamp: datetime) -> None:
        """Update customer's last activity timestamp"""
        self.db.query(CustomerModel).filter(CustomerModel.id == customer_id).update({
            CustomerModel.last_activity: timestamp
        })
        self.db.commit()
    
    def count(self) -> int:
        """Get total count of customers"""
        return self.db.query(CustomerModel).count()
    
    def _to_domain_model(self, db_customer: CustomerModel) -> Customer:
        """Convert database model to domain model"""
        return Customer(
            id=db_customer.id,
            name=db_customer.name,
            email=db_customer.email,
            company=db_customer.company,
            segment=db_customer.segment,
            industry=db_customer.industry,
            employee_count=db_customer.employee_count,
            monthly_revenue=db_customer.monthly_revenue,
            plan_type=db_customer.plan_type,
            created_at=db_customer.created_at,
            last_activity=db_customer.last_activity
        )


class EventRepository:
    """Repository for customer event data operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_event(
        self,
        customer_id: int,
        event_type: str,
        event_data: dict,
        timestamp: datetime
    ) -> CustomerEvent:
        """Create and save a new customer event"""
        db_event = CustomerEventModel(
            customer_id=customer_id,
            event_type=event_type,
            event_data=event_data,
            timestamp=timestamp
        )
        
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        
        return self._to_domain_model(db_event)
    
    def get_recent_events(self, customer_id: int, days: int = 90) -> List[CustomerEvent]:
        """Get recent events for a customer"""
        since = datetime.utcnow() - timedelta(days=days)
        db_events = self.db.query(CustomerEventModel).filter(
            CustomerEventModel.customer_id == customer_id,
            CustomerEventModel.timestamp >= since
        ).order_by(desc(CustomerEventModel.timestamp)).all()
        
        return [self._to_domain_model(event) for event in db_events]
    
    def _to_domain_model(self, db_event: CustomerEventModel) -> CustomerEvent:
        """Convert database model to domain model"""
        return CustomerEvent(
            id=db_event.id,
            customer_id=db_event.customer_id,
            event_type=db_event.event_type,
            event_data=db_event.event_data or {},
            timestamp=db_event.timestamp
        )


class HealthScoreRepository:
    """Repository for health score data operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save_health_score(self, health_score: HealthScore) -> HealthScore:
        """Save a health score to database - updates existing or creates new (one per customer only)"""
        # Convert factor scores to JSON format
        factors_json = {}
        for name, factor_score in health_score.factors.items():
            factors_json[name] = {
                "score": factor_score.score,
                "value": factor_score.value,
                "description": factor_score.description,
                "trend": factor_score.trend,
                **factor_score.metadata
            }
        
        # Check if health score already exists for this customer
        existing_score = self.db.query(HealthScoreModel).filter(
            HealthScoreModel.customer_id == health_score.customer_id
        ).first()
        
        if existing_score:
            # UPDATE existing record
            existing_score.score = health_score.score
            existing_score.status = health_score.status
            existing_score.factors = factors_json
            existing_score.recommendations = health_score.recommendations
            existing_score.calculated_at = health_score.calculated_at
            
            self.db.commit()
            self.db.refresh(existing_score)
            return self._to_domain_model(existing_score)
        else:
            # CREATE new record (first time)
            db_score = HealthScoreModel(
                customer_id=health_score.customer_id,
                score=health_score.score,
                status=health_score.status,
                factors=factors_json,
                recommendations=health_score.recommendations,
                calculated_at=health_score.calculated_at
            )
            self.db.add(db_score)
            self.db.commit()
            self.db.refresh(db_score)
            return self._to_domain_model(db_score)
    
    def get_latest_by_customer(self, customer_id: int) -> Optional[HealthScore]:
        """Get health score for a customer (one per customer)"""
        db_score = self.db.query(HealthScoreModel).filter(
            HealthScoreModel.customer_id == customer_id
        ).first()
        
        if not db_score:
            return None
        
        return self._to_domain_model(db_score)
    
    def get_historical_scores(self, customer_id: int, limit: int = 30) -> List[HealthScore]:
        """Get health score for a customer (only one exists per customer)"""
        db_score = self.db.query(HealthScoreModel).filter(
            HealthScoreModel.customer_id == customer_id
        ).first()
        
        if not db_score:
            return []
        
        return [self._to_domain_model(db_score)]
    
    def count_by_status(self, status: str) -> int:
        """Count customers by health status"""
        return self.db.query(HealthScoreModel).filter(
            HealthScoreModel.status == status
        ).count()
    
    def get_dashboard_stats(self) -> Dict[str, int]:
        """Get all dashboard stats in a single optimized query"""
        from sqlalchemy import func, case
        from data.models import Customer
        
        # Single query to get all counts
        result = self.db.query(
            func.count(Customer.id).label('total_customers'),
            func.sum(case((HealthScoreModel.status == 'healthy', 1), else_=0)).label('healthy_count'),
            func.sum(case((HealthScoreModel.status == 'at_risk', 1), else_=0)).label('at_risk_count'),
            func.sum(case((HealthScoreModel.status == 'critical', 1), else_=0)).label('critical_count')
        ).outerjoin(HealthScoreModel, Customer.id == HealthScoreModel.customer_id).first()
        
        return {
            'total_customers': result.total_customers or 0,
            'healthy_customers': result.healthy_count or 0,
            'at_risk_customers': result.at_risk_count or 0,
            'critical_customers': result.critical_count or 0
        }
    
    def get_average_score(self) -> float:
        """Get average health score across all customers"""
        scores = self.db.query(HealthScoreModel.score).all()
        
        if not scores:
            return 0.0
        
        total_score = sum(score[0] for score in scores)
        return total_score / len(scores)
    
    def _to_domain_model(self, db_score: HealthScoreModel) -> HealthScore:
        """Convert database model to domain model"""
        # Convert JSON factors back to FactorScore objects
        factors = {}
        if db_score.factors:
            for name, factor_data in db_score.factors.items():
                # Extract metadata (everything except score, value, description, trend)
                metadata = {k: v for k, v in factor_data.items() 
                           if k not in ['score', 'value', 'description', 'trend']}
                
                factors[name] = FactorScore(
                    score=factor_data.get('score', 0.0),
                    value=factor_data.get('value', 0),
                    description=factor_data.get('description', ''),
                    trend=factor_data.get('trend'),
                    metadata=metadata
                )
        
        return HealthScore(
            id=db_score.id,
            customer_id=db_score.customer_id,
            score=db_score.score,
            status=db_score.status,
            factors=factors,
            recommendations=db_score.recommendations or [],
            calculated_at=db_score.calculated_at
        )