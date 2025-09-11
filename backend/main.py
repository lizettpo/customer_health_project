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
from domain.exceptions import CustomerNotFoundError, DomainError
from schemas import CustomerListResponse, HealthScoreDetailResponse, CustomerEventCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables (skip during testing)
import os
import os
import time
# if not os.getenv("TESTING"):
#     max_retries = 5
#     for attempt in range(max_retries):
#         try:
#             Base.metadata.create_all(bind=engine)
#             logger.info("Database tables created successfully")
#             break
#         except Exception as e:
#             if attempt < max_retries - 1:
#                 logger.warning(f"Database connection failed (attempt {attempt + 1}/{max_retries}): {e}")
#                 logger.info("Waiting for database to be ready...")
#                 time.sleep(5)
#             else:
#                 logger.error(f"Failed to connect to database after {max_retries} attempts: {e}")
#                 raise

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

# Exception handlers
@app.exception_handler(CustomerNotFoundError)
async def customer_not_found_handler(request, exc: CustomerNotFoundError):
    return JSONResponse(status_code=404, content={"error": "Customer not found", "detail": str(exc)})

@app.exception_handler(DomainError)
async def domain_error_handler(request, exc: DomainError):
    logger.error(f"Domain error: {exc}")
    return JSONResponse(status_code=400, content={"error": "Domain error", "detail": str(exc)})

# @app.on_event("startup")
# async def startup_event():
#     """Initialize database with sample data"""
#     # Skip sample data population during testing
#     if os.getenv("TESTING"):
#         logger.info("Skipping sample data population during testing")
#         return
        
#     from sample_data import populate_sample_data
    
#     db = SessionLocal()
#     try:
#         from data.models import Customer
#         customer_count = db.query(Customer).count()
#         if customer_count == 0:
#             logger.info("Populating database with sample data...")
#             populate_sample_data(db)
#             logger.info("Sample data populated successfully!")
#         else:
#             logger.info(f"Database already contains {customer_count} customers")
#     except Exception as e:
#         # Handle case where tables don't exist (e.g., during testing)
#         logger.info(f"Skipping sample data population: {e}")
#     finally:
#         db.close()

@app.on_event("startup")
async def startup_event():
    """Ensure tables exist, then optionally seed sample data."""
    import os

    # 2a) Import models FIRST so Base knows the tables
    # Make sure data/models.py defines all your ORM classes and imports Base from database.py
    from data import models  # noqa: F401 (import just for side-effects / table registration)

    # 2b) Create tables for the CURRENT database (SQLite here)
    Base.metadata.create_all(bind=engine)
    logger.info("Ensured DB tables exist.")

    # 2c) Skip seeding during tests
    if os.getenv("TESTING"):
        logger.info("Skipping sample data population during testing")
        return

    # 2d) Populate sample data if empty
    from sample_data import populate_sample_data
    from data.models import Customer

    db = SessionLocal()
    try:
        customer_count = db.query(Customer).count()
        if customer_count == 0:
            logger.info("Populating database with sample data...")
            populate_sample_data(db)
            logger.info("Sample data populated successfully!")
        else:
            logger.info(f"Database already contains {customer_count} customers")
    except Exception as e:
        logger.info(f"Skipping sample data population: {e}")
    finally:
        db.close()


# API Routes
@app.get("/")
async def root():
    return JSONResponse(content={"success": True, "data": {"message": "Customer Health Score API", "docs": "/docs"}})

@app.get("/api/customers", response_model=List[CustomerListResponse])
async def get_customers(
    limit: Optional[int] = 100,
    offset: Optional[int] = 0,
    health_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all customers with their health scores"""
    try:
        customer_service = CustomerService(db)
        customers = customer_service.get_customers_with_health_scores(
            limit=limit,
            offset=offset,
            health_status=health_status
        )
        return JSONResponse(content={"success": True, "data": customers})
    except Exception as e:
        logger.error(f"Error fetching customers: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": "Server error", "detail": "Failed to fetch customers"})

@app.get("/api/customers/{customer_id}/health", response_model=HealthScoreDetailResponse)
async def get_customer_health_detail(customer_id: int, db: Session = Depends(get_db)):
    """Get detailed health breakdown for a customer"""
    try:
        health_service = HealthScoreService(db)
        health_detail = health_service.get_customer_health_detail(customer_id)
        return JSONResponse(content={"success": True, "data": health_detail})
    except CustomerNotFoundError:
        return JSONResponse(status_code=404, content={"success": False, "error": "Customer not found", "detail": "Customer not found"})
    except Exception as e:
        logger.error(f"Error getting health detail: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": "Server error", "detail": "Failed to get health detail"})

@app.post("/api/customers/{customer_id}/events")
async def record_customer_event(
    customer_id: int,
    event: CustomerEventCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Record a customer activity event"""
    try:
        customer_service = CustomerService(db)
        result = customer_service.record_event(
            customer_id=customer_id,
            event_type=event.event_type,
            event_data=event.event_data,
            timestamp=event.timestamp
        )
        
        # Recalculate health score in background
        background_tasks.add_task(recalculate_health_score, customer_id, db)
        
        return JSONResponse(content={"success": True, "data": result, "message": "Event recorded successfully"})
    except CustomerNotFoundError:
        return JSONResponse(status_code=404, content={"success": False, "error": "Customer not found", "detail": "Customer not found"})
    except Exception as e:
        logger.error(f"Error recording event: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": "Server error", "detail": "Failed to record event"})

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    try:
        health_service = HealthScoreService(db)
        stats = health_service.get_dashboard_stats()
        return JSONResponse(content={"success": True, "data": stats})
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": "Server error", "detail": "Failed to get dashboard stats"})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(content={"success": True, "data": {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}})

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