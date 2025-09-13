"""
In-Memory Data Store
Loads all data at startup and keeps it in memory for instant access
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from threading import Lock
import logging

from sqlalchemy.orm import Session
from data.repositories import CustomerRepository, EventRepository, HealthScoreRepository
from domain.models import Customer, CustomerEvent, HealthScore
from domain.calculators import HealthScoreCalculator

logger = logging.getLogger(__name__)


class MemoryStore:
    """
    Global in-memory data store that loads everything at startup.

    All API calls serve data from memory for instant response.
    Updates go to both memory and database.
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        # Thread safety
        self._data_lock = Lock()

        # In-memory data
        self.customers: Dict[int, Customer] = {}
        self.events: Dict[int, List[CustomerEvent]] = {}  # customer_id -> events
        self.health_scores: Dict[int, HealthScore] = {}  # customer_id -> latest score

        # Utilities
        self.calculator = HealthScoreCalculator()
        self._db_session = None
        self._repos = None

        self._initialized = True
        logger.info("MemoryStore initialized")

    def set_database(self, db: Session):
        """Set database session and repositories"""
        self._db_session = db
        self._repos = {
            'customer': CustomerRepository(db),
            'event': EventRepository(db),
            'health_score': HealthScoreRepository(db)
        }

    def load_all_data(self):
        """Load ALL data from database into memory at startup"""
        if not self._repos:
            raise RuntimeError("Database not set. Call set_database() first.")

        with self._data_lock:
            logger.info("Loading all data into memory...")
            start_time = datetime.utcnow()

            # 1. Load all customers
            customers = self._repos['customer'].get_all()
            self.customers = {c.id: c for c in customers}

            # 2. Load all events (last 90 days for each customer)
            self.events = {}
            for customer_id in self.customers.keys():
                events = self._repos['event'].get_recent_events(customer_id, days=90)
                self.events[customer_id] = events

            # 3. Load all health scores
            self.health_scores = {}
            for customer_id in self.customers.keys():
                score = self._repos['health_score'].get_latest_by_customer(customer_id)
                if score:
                    self.health_scores[customer_id] = score

            load_time = (datetime.utcnow() - start_time).total_seconds()

            logger.info(f"Data loaded in {load_time:.2f}s: "
                       f"{len(self.customers)} customers, "
                       f"{sum(len(events) for events in self.events.values())} events, "
                       f"{len(self.health_scores)} health scores")

    def get_all_customers(self, health_status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all customers with health scores from memory"""
        result = []

        for customer in self.customers.values():
            # Filter by health status if requested
            if health_status:
                health_score = self.health_scores.get(customer.id)
                if not health_score or health_score.status != health_status:
                    continue

            # Get health score
            health_score = self.health_scores.get(customer.id)

            customer_data = {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "company": customer.company,
                "segment": customer.segment,
                "created_at": customer.created_at.isoformat() if customer.created_at else None,
                "last_activity": customer.last_activity.isoformat() if customer.last_activity else None,
                "health_score": health_score.score if health_score else 0,
                "health_status": health_score.status if health_score else "unknown"
            }
            result.append(customer_data)

        return result

    def get_customer_by_id(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID from memory"""
        return self.customers.get(customer_id)

    def get_customer_health_detail(self, customer_id: int) -> Dict[str, Any]:
        """Get customer health detail from memory"""
        customer = self.customers.get(customer_id)
        if not customer:
            return None

        events = self.events.get(customer_id, [])
        health_score = self.health_scores.get(customer_id)

        if not health_score:
            return None

        return {
            "customer_id": customer.id,
            "customer_name": customer.name,
            "overall_score": health_score.score,
            "status": health_score.status,
            "factors": {
                name: {
                    "score": factor.score,
                    "value": factor.value,
                    "description": factor.description,
                    "trend": factor.trend,
                    **factor.metadata
                }
                for name, factor in health_score.factors.items()
            },
            "calculated_at": health_score.calculated_at.isoformat() if health_score.calculated_at else None,
            "recommendations": health_score.recommendations,
            "data_summary": {
                "events_analyzed": len(events),
                "customer_segment": customer.segment
            }
        }

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics from memory"""
        total_customers = len(self.customers)
        healthy_customers = 0
        at_risk_customers = 0
        critical_customers = 0

        for health_score in self.health_scores.values():
            if health_score.status == "healthy":
                healthy_customers += 1
            elif health_score.status == "at_risk":
                at_risk_customers += 1
            elif health_score.status == "critical":
                critical_customers += 1

        total_with_scores = healthy_customers + at_risk_customers + critical_customers

        return {
            "total_customers": total_customers,
            "healthy_customers": healthy_customers,
            "at_risk_customers": at_risk_customers,
            "critical_customers": critical_customers,
            "distribution": {
                "healthy_percent": round((healthy_customers / total_with_scores * 100), 1) if total_with_scores > 0 else 0,
                "at_risk_percent": round((at_risk_customers / total_with_scores * 100), 1) if total_with_scores > 0 else 0,
                "critical_percent": round((critical_customers / total_with_scores * 100), 1) if total_with_scores > 0 else 0
            },
            "last_updated": datetime.utcnow().isoformat()
        }

    def add_customer_event(self, customer_id: int, event_type: str,
                          event_data: Dict[str, Any], timestamp: datetime = None) -> Dict[str, Any]:
        """
        Add new event: Save to database + Update memory + Recalculate health score
        """
        if not self._repos:
            raise RuntimeError("Database not set")

        customer = self.customers.get(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        timestamp = timestamp or datetime.utcnow()

        with self._data_lock:
            # 1. Save to database
            saved_event = self._repos['event'].create_event(
                customer_id=customer_id,
                event_type=event_type,
                event_data=event_data,
                timestamp=timestamp
            )

            # 2. Update customer last activity in database
            self._repos['customer'].update_last_activity(customer_id, timestamp)

            # 3. Update memory - add event
            if customer_id not in self.events:
                self.events[customer_id] = []
            self.events[customer_id].insert(0, saved_event)  # Add at beginning

            # Keep only last 90 days in memory
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            self.events[customer_id] = [
                e for e in self.events[customer_id]
                if e.timestamp >= cutoff_date
            ]

            # 4. Update customer last activity in memory
            customer.last_activity = timestamp

            # 5. Recalculate health score
            events = self.events[customer_id]
            new_health_score = self.calculator.calculate_health_score(customer, events)

            # 6. Save health score to database
            saved_health_score = self._repos['health_score'].save_health_score(new_health_score)

            # 7. Update health score in memory
            self.health_scores[customer_id] = saved_health_score

            logger.info(f"Added {event_type} event for customer {customer_id}, "
                       f"new health score: {saved_health_score.score}")

            return {
                "message": "Event recorded successfully",
                "event_id": saved_event.id,
                "customer_id": customer_id,
                "customer_name": customer.name,
                "event_type": event_type,
                "timestamp": timestamp.isoformat(),
                "new_health_score": saved_health_score.score,
                "new_health_status": saved_health_score.status
            }

    def get_customer_events(self, customer_id: int, days: int = 90) -> List[Dict[str, Any]]:
        """Get customer events from memory"""
        events = self.events.get(customer_id, [])

        # Filter by days if different from default 90
        if days != 90:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            events = [e for e in events if e.timestamp >= cutoff_date]

        return [
            {
                "id": event.id,
                "event_type": event.event_type,
                "event_data": event.event_data,
                "timestamp": event.timestamp.isoformat() if event.timestamp else None
            }
            for event in events
        ]

    def recalculate_all_health_scores(self) -> int:
        """Recalculate all health scores and update both memory and database"""
        if not self._repos:
            raise RuntimeError("Database not set")

        processed_count = 0

        with self._data_lock:
            for customer_id, customer in self.customers.items():
                try:
                    events = self.events.get(customer_id, [])

                    # Calculate new health score
                    health_score = self.calculator.calculate_health_score(customer, events)

                    # Save to database
                    saved_score = self._repos['health_score'].save_health_score(health_score)

                    # Update memory
                    self.health_scores[customer_id] = saved_score

                    processed_count += 1

                except Exception as e:
                    logger.error(f"Failed to recalculate health score for customer {customer_id}: {e}")
                    continue

        logger.info(f"Recalculated health scores for {processed_count} customers")
        return processed_count


# Global instance
memory_store = MemoryStore()