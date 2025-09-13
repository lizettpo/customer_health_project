from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from database import SessionLocal, engine, Base
from services.customer_service import CustomerService
from services.health_score_service import HealthScoreService
from domain.exceptions import CustomerNotFoundError, DomainError, InvalidEventDataError
from schemas import CustomerListResponse, HealthScoreDetailResponse, CustomerEventCreate

# Configure logging with file output
import os
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Configure logging with both file and console output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # File handler with rotation
        RotatingFileHandler(
            os.path.join(logs_dir, 'app.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        ),
        # Console handler
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create database tables (skip during testing)
import time

app = FastAPI(
    title="Customer Health Score API",
    description="Clean Architecture API for customer health scores",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Service dependencies
def get_customer_service(db: Session = Depends(get_db)) -> CustomerService:
    return CustomerService(db)

def get_health_service(db: Session = Depends(get_db)) -> HealthScoreService:
    return HealthScoreService(db)

# Exception handlers
@app.exception_handler(CustomerNotFoundError)
async def customer_not_found_handler(request, exc: CustomerNotFoundError):
    return JSONResponse(status_code=404, content={"error": "Customer not found", "detail": str(exc)})

@app.exception_handler(InvalidEventDataError)
async def invalid_event_data_handler(request, exc: InvalidEventDataError):
    logger.warning(f"Invalid event data: {exc}")
    return JSONResponse(status_code=400, content={"success": False, "error": "Invalid event data", "detail": str(exc.message)})

@app.exception_handler(DomainError)
async def domain_error_handler(request, exc: DomainError):
    logger.error(f"Domain error: {exc}")
    return JSONResponse(status_code=400, content={"success": False, "error": "Domain error", "detail": str(exc)})


@app.on_event("startup")
async def startup_event():
    """Ensure tables exist, then optionally seed sample data and recalculate health scores."""
    import os

    logger.info("🚀 Starting Customer Health Score API...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Database URL: {os.getenv('DATABASE_URL', 'sqlite:///./data/customer_health.db')}")

    # 2a) Import models FIRST so Base knows the tables
    # Make sure data/models.py defines all your ORM classes and imports Base from database.py
    from data import models  # noqa: F401 (import just for side-effects / table registration)

    # 2b) Create tables for the CURRENT database (SQLite here)
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created/verified")

    # 2c) Skip seeding during tests
    if os.getenv("TESTING"):
        logger.info("⚠️  Skipping sample data population during testing")
        return

    # 2d) Populate sample data if empty
    from sample_data import populate_sample_data
    from data.models import Customer

    db = SessionLocal()
    try:
        customer_count = db.query(Customer).count()
        if customer_count == 0:
            logger.info("📊 Database empty - populating with sample data...")
            populate_sample_data(db)
            logger.info("✅ Sample data populated successfully!")
        else:
            logger.info(f"📈 Database already contains {customer_count} customers")

        # 2e) Skip health score recalculation on startup to avoid timeouts
        # Health scores are calculated on-demand and via background tasks
        logger.info("⏩ Health scores calculated on-demand for optimal startup performance")
        logger.info("🎉 API startup completed successfully!")

    except Exception as e:
        logger.error(f"❌ Error during startup: {e}", exc_info=True)
    finally:
        db.close()


@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown logging"""
    logger.info("🛑 Customer Health Score API shutting down...")
    logger.info("👋 Goodbye!")


# API Routes
@app.get("/")
async def root():
    return JSONResponse(content={"success": True, "data": {"message": "Customer Health Score API", "docs": "/docs"}})

@app.get("/api/customers", response_model=List[CustomerListResponse])
async def get_customers(
    health_status: Optional[str] = None,
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Get all customers with their health scores"""
    logger.info(f"Fetching customers with health_status filter: {health_status}")
    try:
        customers = customer_service.get_customers_with_health_scores(
            health_status=health_status
        )
        logger.info(f"Successfully fetched {len(customers)} customers")
        return JSONResponse(content={"success": True, "data": customers})
    except Exception as e:
        logger.error(f"Error fetching customers: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"success": False, "error": "Server error", "detail": "Failed to fetch customers"})

@app.get("/api/customers/{customer_id}/health", response_model=HealthScoreDetailResponse)
async def get_customer_health_detail(
    customer_id: int,
    health_service: HealthScoreService = Depends(get_health_service)
):
    """Get detailed health breakdown for a customer"""
    logger.info(f"Fetching health detail for customer {customer_id}")
    try:
        health_detail = health_service.get_customer_health_detail(customer_id)
        logger.info(f"Successfully calculated health score for customer {customer_id}: {health_detail.get('overall_score', 'N/A')}")
        return JSONResponse(content={"success": True, "data": health_detail})
    except CustomerNotFoundError:
        logger.warning(f"Customer {customer_id} not found")
        return JSONResponse(status_code=404, content={"success": False, "error": "Customer not found", "detail": "Customer not found"})
    except Exception as e:
        logger.error(f"Error getting health detail for customer {customer_id}: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"success": False, "error": "Server error", "detail": "Failed to get health detail"})

@app.post("/api/customers/{customer_id}/events")
async def record_customer_event(
    customer_id: int,
    event: CustomerEventCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Record a customer activity event.

    This endpoint records various types of customer events that affect health scoring,
    such as API calls, logins, payments, feature usage, and support tickets.

    Path Parameters:
        customer_id (int): Unique identifier of the customer

    Request Body:
        event (CustomerEventCreate): Event data containing:
            - event_type: Type of event ('api_call', 'login', 'payment', 'feature_use', 'support_ticket')
            - event_data: Event-specific data dictionary (optional)
            - timestamp: Event timestamp (optional, defaults to current time)

    Returns:
        200: Event recorded successfully with confirmation data
        404: Customer not found
        500: Server error during event recording

    Example:
        POST /api/customers/123/events
        {
            "event_type": "api_call",
            "event_data": {
                "endpoint": "/api/users",
                "method": "GET",
                "response_code": 200
            }
        }
    """
    logger.info(f"Recording {event.event_type} event for customer {customer_id}")
    try:
        customer_service = CustomerService(db)
        result = customer_service.record_event(
            customer_id=customer_id,
            event_type=event.event_type,
            event_data=event.event_data,
            timestamp=event.timestamp
        )

        # Skip background health score recalculation to avoid SQLite lock contention
        # Health scores are calculated on-demand when requested
        logger.info(f"Successfully recorded {event.event_type} event for customer {customer_id}")
        return JSONResponse(content={"success": True, "data": result, "message": "Event recorded successfully"})
    except InvalidEventDataError as e:
        logger.warning(f"Invalid event data for customer {customer_id}: {e}")
        return JSONResponse(status_code=400, content={"success": False, "error": "Invalid event data", "detail": str(e.message)})
    except CustomerNotFoundError:
        logger.warning(f"Attempted to record event for non-existent customer {customer_id}")
        return JSONResponse(status_code=404, content={"success": False, "error": "Customer not found", "detail": "Customer not found"})
    except Exception as e:
        logger.error(f"Error recording event for customer {customer_id}: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"success": False, "error": "Server error", "detail": "Failed to record event"})

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(health_service: HealthScoreService = Depends(get_health_service)):
    """
    Get dashboard statistics.

    Retrieves aggregated statistics for the customer health dashboard,
    including customer counts by health status and distribution percentages.

    Returns:
        200: Dashboard statistics containing:
            - total_customers: Total number of customers
            - healthy_customers: Count of customers with healthy status (75+)
            - at_risk_customers: Count of customers at risk (50-74)
            - critical_customers: Count of customers in critical state (<50)
            - distribution: Percentage breakdown by status
            - last_updated: Timestamp of data retrieval
        500: Server error during statistics retrieval

    Example Response:
        {
            "success": true,
            "data": {
                "total_customers": 100,
                "healthy_customers": 60,
                "at_risk_customers": 30,
                "critical_customers": 10,
                "distribution": {
                    "healthy_percent": 60.0,
                    "at_risk_percent": 30.0,
                    "critical_percent": 10.0
                },
                "last_updated": "2024-01-15T10:30:00Z"
            }
        }
    """
    logger.info("Fetching dashboard statistics")
    try:
        stats = health_service.get_dashboard_stats()
        logger.info(f"Successfully generated dashboard stats: {stats.get('total_customers', 0)} total customers")
        return JSONResponse(content={"success": True, "data": stats})
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"success": False, "error": "Server error", "detail": "Failed to get dashboard stats"})


async def recalculate_health_score(customer_id: int, db: Session):
    """Background task to recalculate health score"""
    try:
        health_service = HealthScoreService(db)
        health_service.calculate_and_save_health_score(customer_id)
        logger.info(f"Recalculated health score for customer {customer_id}")
    except Exception as e:
        logger.error(f"Failed to recalculate health score for customer {customer_id}: {e}")
        
@app.get("/api/dashboard")
async def serve_dashboard():
    """Serve the React dashboard interface"""
    return FileResponse('static/index.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)