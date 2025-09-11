"""
Data Layer - Repository Implementations
Database operations and data access
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from data.models import Customer as CustomerModel, CustomerEvent as CustomerEventModel, HealthScore as HealthScoreModel
from domain.models import Customer, CustomerEvent, HealthScore, FactorScore


class CustomerRepository:
    """Repository for customer data operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID"""
        db_customer = self.db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
        if not db_customer:
            return None
        return self._to_domain_model(db_customer)
    
    def get_all(self) -> List[Customer]:
        """Get all customers with pagination"""
        query = self.db.query(CustomerModel)
     
        
        db_customers = query.all()
        return [self._to_domain_model(customer) for customer in db_customers]
    
    def get_by_health_status(self, status: str) -> List[Customer]:
        """Get customers by health status"""
        # Get latest health scores by status
        subquery = self.db.query(
            HealthScoreModel.customer_id,
            func.max(HealthScoreModel.calculated_at).label('latest_calc')
        ).group_by(HealthScoreModel.customer_id).subquery()
        
        latest_scores = self.db.query(HealthScoreModel).join(
            subquery,
            (HealthScoreModel.customer_id == subquery.c.customer_id) &
            (HealthScoreModel.calculated_at == subquery.c.latest_calc)
        ).filter(HealthScoreModel.status == status).all()
        
        customer_ids = [score.customer_id for score in latest_scores]
        
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
        """Save a health score to database"""
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
        """Get latest health score for a customer"""
        db_score = self.db.query(HealthScoreModel).filter(
            HealthScoreModel.customer_id == customer_id
        ).order_by(desc(HealthScoreModel.calculated_at)).first()
        
        if not db_score:
            return None
        
        return self._to_domain_model(db_score)
    
    def get_historical_scores(self, customer_id: int, limit: int = 30) -> List[HealthScore]:
        """Get historical health scores for a customer"""
        db_scores = self.db.query(HealthScoreModel).filter(
            HealthScoreModel.customer_id == customer_id
        ).order_by(desc(HealthScoreModel.calculated_at)).limit(limit).all()
        
        return [self._to_domain_model(score) for score in db_scores]
    
    def count_by_status(self, status: str) -> int:
        """Count customers by health status"""
        # Get latest scores and count by status
        subquery = self.db.query(
            HealthScoreModel.customer_id,
            func.max(HealthScoreModel.calculated_at).label('latest_calc')
        ).group_by(HealthScoreModel.customer_id).subquery()
        
        count = self.db.query(HealthScoreModel).join(
            subquery,
            (HealthScoreModel.customer_id == subquery.c.customer_id) &
            (HealthScoreModel.calculated_at == subquery.c.latest_calc)
        ).filter(HealthScoreModel.status == status).count()
        
        return count
    
    def get_average_score(self) -> float:
        """Get average health score across all customers"""
        # Get latest score for each customer
        subquery = self.db.query(
            HealthScoreModel.customer_id,
            func.max(HealthScoreModel.calculated_at).label('latest_calc')
        ).group_by(HealthScoreModel.customer_id).subquery()
        
        latest_scores = self.db.query(HealthScoreModel.score).join(
            subquery,
            (HealthScoreModel.customer_id == subquery.c.customer_id) &
            (HealthScoreModel.calculated_at == subquery.c.latest_calc)
        ).all()
        
        if not latest_scores:
            return 0.0
        
        total_score = sum(score[0] for score in latest_scores)
        return total_score / len(latest_scores)
    
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