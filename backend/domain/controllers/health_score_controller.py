"""
Controller Layer - Health Score Controller
Loads data into memory and coordinates it with domain calculations
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime

from data.repositories import CustomerRepository, EventRepository, HealthScoreRepository
from domain.calculators import HealthScoreCalculator
from domain.exceptions import CustomerNotFoundError


class HealthScoreController:
    """Controller that LOADS DATA and coordinates with domain logic"""

    def __init__(self, db: Session):
        self.customer_repo = CustomerRepository(db)
        self.event_repo = EventRepository(db)
        self.health_score_repo = HealthScoreRepository(db)
        self.calculator = HealthScoreCalculator()

        # Cache for loaded data
        self._dashboard_data = None
        self._last_dashboard_load = None
        self._initialized = True
    
    def get_customer_health_detail(self, customer_id: int) -> Dict[str, Any]:
        """
        Get customer health detail from memory store
        """
        from domain.memory_store import memory_store

        health_detail = memory_store.get_customer_health_detail(customer_id)
        if not health_detail:
            raise CustomerNotFoundError(f"Customer {customer_id} not found")

        return health_detail
    
    def get_dashboard_statistics(self) -> Dict[str, Any]:
        """
        Get dashboard statistics from memory store
        """
        from domain.memory_store import memory_store
        return memory_store.get_dashboard_stats()
    
    def bulk_calculate_health_scores(self, customer_ids: List[int]) -> Dict[str, Any]:
        """
        LOADS BULK DATA: Load multiple customers and events, batch calculate
        """

        loaded_customers = {}
        for customer_id in customer_ids:
            customer = self.customer_repo.get_by_id(customer_id)
            if customer:
                loaded_customers[customer_id] = customer

        loaded_events = {}
        for customer_id in loaded_customers.keys():
            events = self.event_repo.get_recent_events(customer_id, days=90)
            loaded_events[customer_id] = events

        calculation_results = []
        for customer_id, customer in loaded_customers.items():
            events = loaded_events[customer_id]

            health_score = self.calculator.calculate_health_score(customer, events)

            saved_score = self.health_score_repo.save_health_score(health_score)
            calculation_results.append({
                "customer_id": customer_id,
                "score": saved_score.score,
                "status": saved_score.status
            })

        return {
            "processed_customers": len(calculation_results),
            "results": calculation_results,
            "completed_at": datetime.utcnow()
        }
    
    def get_latest_health_score(self, customer_id: int):
        """
        LOADS DATA: Get latest health score
        """
        # 🔥 LOAD HEALTH SCORE DATA
        return self.health_score_repo.get_latest_by_customer(customer_id)
    
    def calculate_and_save_health_score(self, customer_id: int):
        """
        Calculate and save health score for a single customer
        """
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"Customer {customer_id} not found")

        events = self.event_repo.get_recent_events(customer_id, days=90)

        health_score = self.calculator.calculate_health_score(customer, events)

        return self.health_score_repo.save_health_score(health_score)
    
    def recalculate_all_health_scores(self) -> int:
        """
        Recalculate health scores for all customers using memory store
        Returns the number of customers processed
        """
        from domain.memory_store import memory_store
        return memory_store.recalculate_all_health_scores()