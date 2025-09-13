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
        LOADS ALL DATA: Customer, events, calculates health using same method as list view
        """

        # 🔥 LOAD CUSTOMER DATA
        loaded_customer = self.customer_repo.get_by_id(customer_id)
        if not loaded_customer:
            raise CustomerNotFoundError(f"Customer {customer_id} not found")

        # 🔥 LOAD EVENTS DATA
        loaded_events = self.event_repo.get_recent_events(customer_id, days=90)

        # 🔥 USE SAME CALCULATION METHOD as customer list
        saved_health_score = self.calculate_and_save_health_score(customer_id)

        # 🔥 COORDINATE ALL LOADED DATA - Combine everything in memory (no historical data needed)
        coordinated_data = {
            "customer_id": loaded_customer.id,
            "customer_name": loaded_customer.name,
            "overall_score": saved_health_score.score,
            "status": saved_health_score.status,
            "factors": {
                name: {
                    "score": factor.score,
                    "value": factor.value,
                    "description": factor.description,
                    "trend": factor.trend,
                    **factor.metadata
                }
                for name, factor in saved_health_score.factors.items()
            },
            "calculated_at": saved_health_score.calculated_at.isoformat() if saved_health_score.calculated_at else None,
            "recommendations": saved_health_score.recommendations,
            "data_summary": {
                "events_analyzed": len(loaded_events),
                "customer_segment": loaded_customer.segment
            }
        }

        return coordinated_data
    
    def get_dashboard_statistics(self) -> Dict[str, Any]:
        """
        Get dashboard statistics using optimized single query
        """
        # Use optimized single query instead of multiple queries
        stats = self.health_score_repo.get_dashboard_stats()

        # Calculate additional metrics
        total_with_scores = stats["healthy_customers"] + stats["at_risk_customers"] + stats["critical_customers"]

        return {
            "total_customers": stats["total_customers"],
            "healthy_customers": stats["healthy_customers"],
            "at_risk_customers": stats["at_risk_customers"],
            "critical_customers": stats["critical_customers"],

            "distribution": {
                "healthy_percent": round((stats["healthy_customers"] / total_with_scores * 100), 1) if total_with_scores > 0 else 0,
                "at_risk_percent": round((stats["at_risk_customers"] / total_with_scores * 100), 1) if total_with_scores > 0 else 0,
                "critical_percent": round((stats["critical_customers"] / total_with_scores * 100), 1) if total_with_scores > 0 else 0
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
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
        Recalculate health scores for all customers in the database
        Returns the number of customers processed
        """
        import logging
        logger = logging.getLogger(__name__)

        all_customers = self.customer_repo.get_all()
        processed_count = 0

        logger.info(f"Starting health score recalculation for {len(all_customers)} customers")

        for customer in all_customers:
            try:
                events = self.event_repo.get_recent_events(customer.id, days=90)

                health_score = self.calculator.calculate_health_score(customer, events)

                self.health_score_repo.save_health_score(health_score)
                processed_count += 1

                if processed_count % 10 == 0:
                    logger.info(f"Processed {processed_count}/{len(all_customers)} customers")

            except Exception as e:
                logger.error(f"Failed to calculate health score for customer {customer.id}: {e}")
                continue

        logger.info(f"Completed health score recalculation. Processed {processed_count} customers")
        return processed_count