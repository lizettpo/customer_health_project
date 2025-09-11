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
    _instance = None
    _initialized = False
    
    def __new__(cls, db: Session = None):
        if cls._instance is None:
            cls._instance = super(HealthScoreController, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, db: Session):
        if not self._initialized:
            self.customer_repo = CustomerRepository(db)
            self.event_repo = EventRepository(db)
            self.health_score_repo = HealthScoreRepository(db)
            self.calculator = HealthScoreCalculator()
            
            # Cache for loaded data
            self._dashboard_data = None
            self._last_dashboard_load = None
            HealthScoreController._initialized = True
    
    def get_customer_health_detail(self, customer_id: int) -> Dict[str, Any]:
        """
        LOADS ALL DATA: Customer, events, calculates health, loads history - coordinates everything
        """
        
        # 🔥 LOAD CUSTOMER DATA
        loaded_customer = self.customer_repo.get_by_id(customer_id)
        if not loaded_customer:
            raise CustomerNotFoundError(f"Customer {customer_id} not found")
        
        # 🔥 LOAD EVENTS DATA
        loaded_events = self.event_repo.get_recent_events(customer_id, days=90)
        
        # 🔥 COORDINATE WITH DOMAIN - Calculate health score using loaded data
        calculated_health_score = self.calculator.calculate_health_score(loaded_customer, loaded_events)
        
        # 🔥 SAVE CALCULATED DATA
        saved_health_score = self.health_score_repo.save_health_score(calculated_health_score)
        
        # 🔥 LOAD HISTORICAL DATA
        loaded_historical_scores = self.health_score_repo.get_historical_scores(customer_id, limit=30)
        
        # 🔥 COORDINATE ALL LOADED DATA - Combine everything in memory
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
            "historical_scores": [
                {
                    "score": hs.score,
                    "status": hs.status,
                    "calculated_at": hs.calculated_at.isoformat() if hs.calculated_at else None
                }
                for hs in loaded_historical_scores
            ],
            "recommendations": saved_health_score.recommendations,
            "data_summary": {
                "events_analyzed": len(loaded_events),
                "history_points": len(loaded_historical_scores),
                "customer_segment": loaded_customer.segment
            }
        }
        
        return coordinated_data
    
    def get_dashboard_statistics(self) -> Dict[str, Any]:
        """
        LOADS AND CACHES DATA: Load all dashboard data once, coordinate in memory
        """
        
        # Check if we have cached data (cache for 10 seconds for fresher data)
        now = datetime.utcnow()
        if (self._dashboard_data and self._last_dashboard_load and 
            (now - self._last_dashboard_load).total_seconds() < 10):
            return self._dashboard_data
        
        # 🔥 LOAD ALL DASHBOARD DATA AT ONCE
        loaded_total_customers = self.customer_repo.count()
        loaded_healthy_count = self.health_score_repo.count_by_status("healthy")
        loaded_at_risk_count = self.health_score_repo.count_by_status("at_risk")
        loaded_critical_count = self.health_score_repo.count_by_status("critical")
        loaded_average_score = self.health_score_repo.get_average_score()
        
        # 🔥 COORDINATE LOADED DATA - Calculate additional metrics in memory
        total_with_scores = loaded_healthy_count + loaded_at_risk_count + loaded_critical_count
        health_coverage = (total_with_scores / loaded_total_customers * 100) if loaded_total_customers > 0 else 0
        
        # 🔥 CACHE THE COORDINATED DATA
        self._dashboard_data = {
            "total_customers": loaded_total_customers,
            "healthy_customers": loaded_healthy_count,
            "at_risk_customers": loaded_at_risk_count,
            "critical_customers": loaded_critical_count,
            "average_health_score": round(loaded_average_score, 2),
            "health_coverage_percentage": round(health_coverage, 1),
            "distribution": {
                "healthy_percent": round((loaded_healthy_count / total_with_scores * 100), 1) if total_with_scores > 0 else 0,
                "at_risk_percent": round((loaded_at_risk_count / total_with_scores * 100), 1) if total_with_scores > 0 else 0,
                "critical_percent": round((loaded_critical_count / total_with_scores * 100), 1) if total_with_scores > 0 else 0
            },
            "last_updated": now.isoformat()
        }
        self._last_dashboard_load = now
        
        return self._dashboard_data
    
    def bulk_calculate_health_scores(self, customer_ids: List[int]) -> Dict[str, Any]:
        """
        LOADS BULK DATA: Load multiple customers and events, batch calculate
        """
        
        # 🔥 LOAD ALL CUSTOMERS DATA AT ONCE
        loaded_customers = {}
        for customer_id in customer_ids:
            customer = self.customer_repo.get_by_id(customer_id)
            if customer:
                loaded_customers[customer_id] = customer
        
        # 🔥 LOAD ALL EVENTS DATA AT ONCE
        loaded_events = {}
        for customer_id in loaded_customers.keys():
            events = self.event_repo.get_recent_events(customer_id, days=90)
            loaded_events[customer_id] = events
        
        # 🔥 COORDINATE WITH DOMAIN - Batch calculate all scores
        calculation_results = []
        for customer_id, customer in loaded_customers.items():
            events = loaded_events[customer_id]
            
            # Calculate using domain logic
            health_score = self.calculator.calculate_health_score(customer, events)
            
            # Save result
            saved_score = self.health_score_repo.save_health_score(health_score)
            calculation_results.append({
                "customer_id": customer_id,
                "score": saved_score.score,
                "status": saved_score.status
            })
        
        # 🔥 COORDINATE RESULTS - Summary of batch operation
        return {
            "processed_customers": len(calculation_results),
            "results": calculation_results,
            "average_score": sum(r["score"] for r in calculation_results) / len(calculation_results) if calculation_results else 0,
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
        # 🔥 LOAD CUSTOMER DATA
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"Customer {customer_id} not found")
        
        # 🔥 LOAD EVENTS DATA
        events = self.event_repo.get_recent_events(customer_id, days=90)
        
        # 🔥 CALCULATE HEALTH SCORE
        health_score = self.calculator.calculate_health_score(customer, events)
        
        # 🔥 SAVE HEALTH SCORE
        return self.health_score_repo.save_health_score(health_score)
    
    def recalculate_all_health_scores(self) -> int:
        """
        Recalculate health scores for all customers in the database
        Returns the number of customers processed
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # 🔥 LOAD ALL CUSTOMERS
        all_customers = self.customer_repo.get_all()
        processed_count = 0
        
        logger.info(f"Starting health score recalculation for {len(all_customers)} customers")
        
        for customer in all_customers:
            try:
                # 🔥 LOAD EVENTS FOR EACH CUSTOMER
                events = self.event_repo.get_recent_events(customer.id, days=90)
                
                # 🔥 CALCULATE HEALTH SCORE
                health_score = self.calculator.calculate_health_score(customer, events)
                
                # 🔥 SAVE HEALTH SCORE
                self.health_score_repo.save_health_score(health_score)
                processed_count += 1
                
                if processed_count % 10 == 0:
                    logger.info(f"Processed {processed_count}/{len(all_customers)} customers")
                    
            except Exception as e:
                logger.error(f"Failed to calculate health score for customer {customer.id}: {e}")
                continue
        
        logger.info(f"Completed health score recalculation. Processed {processed_count} customers")
        return processed_count