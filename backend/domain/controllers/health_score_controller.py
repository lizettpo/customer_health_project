"""
Controller Layer - Health Score Controller
Loads data into memory and coordinates it with domain calculations
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime

from data.repositories import HealthScoreRepository
from domain.calculators import HealthScoreCalculator
from domain.exceptions import CustomerNotFoundError


class HealthScoreController:
    """Controller that uses memory store for all operations"""

    def __init__(self, db: Session):
        # Only need health score repo for database writes
        self.health_score_repo = HealthScoreRepository(db)
        self.calculator = HealthScoreCalculator()

        # Get global memory store instance
        from domain.memory_store import memory_store
        self.memory_store = memory_store
    
    def get_customer_health_detail(self, customer_id: int) -> Dict[str, Any]:
        """
        Get customer health detail from memory store
        """
        health_detail = self.memory_store.get_customer_health_detail(customer_id)
        if not health_detail:
            raise CustomerNotFoundError(f"Customer {customer_id} not found")

        return health_detail
    
    def get_dashboard_statistics(self) -> Dict[str, Any]:
        """
        Get dashboard statistics from memory store
        """
        return self.memory_store.get_dashboard_stats()
    
    def bulk_calculate_health_scores(self, customer_ids: List[int]) -> Dict[str, Any]:
        """
        Bulk calculate health scores using memory store for multiple customers
        """
        calculation_results = []

        with self.memory_store._data_lock:
            for customer_id in customer_ids:
                # Get customer from memory store
                customer = self.memory_store.get_customer_by_id(customer_id)
                if not customer:
                    continue  # Skip customers not found

                # Get events from memory store
                events = self.memory_store.events.get(customer_id, [])

                try:
                    health_score = self.calculator.calculate_health_score(customer, events)

                    # Save to database
                    saved_score = self.health_score_repo.save_health_score(health_score)

                    # Update memory store
                    self.memory_store.health_scores[customer_id] = saved_score

                    calculation_results.append({
                        "customer_id": customer_id,
                        "score": saved_score.score,
                        "status": saved_score.status
                    })
                except Exception as e:
                    # Log error but continue processing other customers
                    continue

        return {
            "processed_customers": len(calculation_results),
            "results": calculation_results,
            "completed_at": datetime.utcnow()
        }
    
    def get_latest_health_score(self, customer_id: int):
        """
        Get latest health score from memory store
        """
        return self.memory_store.health_scores.get(customer_id)
    
    def calculate_and_save_health_score(self, customer_id: int):
        """
        Calculate and save health score for a single customer using memory store
        """
        customer = self.memory_store.get_customer_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"Customer {customer_id} not found")

        # Get events from memory store
        events = self.memory_store.events.get(customer_id, [])

        health_score = self.calculator.calculate_health_score(customer, events)

        # Save to database
        saved_score = self.health_score_repo.save_health_score(health_score)

        # Update memory store
        with self.memory_store._data_lock:
            self.memory_store.health_scores[customer_id] = saved_score

        return saved_score
    
    def recalculate_all_health_scores(self) -> int:
        """
        Recalculate health scores for all customers using memory store
        Returns the number of customers processed
        """
        return self.memory_store.recalculate_all_health_scores()