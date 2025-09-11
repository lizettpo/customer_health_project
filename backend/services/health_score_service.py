"""
Service Layer - Health Score Service
Pure orchestration - calls controllers only
"""

from sqlalchemy.orm import Session
from typing import Dict, Any

from domain.controllers.health_score_controller import HealthScoreController


class HealthScoreService:
    """Service layer for health score operations - pure orchestration"""
    _instance = None
    _initialized = False
    
    def __new__(cls, db: Session = None):
        if cls._instance is None:
            cls._instance = super(HealthScoreService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, db: Session):
        if not self._initialized:
            self.health_score_controller = HealthScoreController(db)
            HealthScoreService._initialized = True
    
    def get_customer_health_detail(self, customer_id: int) -> Dict[str, Any]:
        """Get detailed health breakdown"""
        return self.health_score_controller.get_customer_health_detail(customer_id)
    
    def calculate_and_save_health_score(self, customer_id: int):
        """Calculate and save health score"""
        return self.health_score_controller.calculate_and_save_health_score(customer_id)
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        return self.health_score_controller.get_dashboard_statistics()
    
    def recalculate_all_health_scores(self) -> int:
        """Recalculate health scores for all customers"""
        return self.health_score_controller.recalculate_all_health_scores()