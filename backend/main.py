from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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

# Create database tables
Base.metadata.create_all(bind=engine)

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
    return HTTPException(status_code=404, detail=str(exc))

@app.exception_handler(DomainError)
async def domain_error_handler(request, exc: DomainError):
    logger.error(f"Domain error: {exc}")
    return HTTPException(status_code=400, detail=str(exc))

@app.on_event("startup")
async def startup_event():
    """Initialize database with sample data"""
    from sample_data import populate_sample_data
    
    db = SessionLocal()
    try:
        from data.models import Customer
        customer_count = db.query(Customer).count()
        if customer_count == 0:
            logger.info("Populating database with sample data...")
            populate_sample_data(db)
            logger.info("Sample data populated successfully!")
        else:
            logger.info(f"Database already contains {customer_count} customers")
    finally:
        db.close()

# API Routes
@app.get("/")
async def root():
    return {"message": "Customer Health Score API", "docs": "/docs"}

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
        return customers
    except Exception as e:
        logger.error(f"Error fetching customers: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch customers")

@app.get("/api/customers/{customer_id}/health", response_model=HealthScoreDetailResponse)
async def get_customer_health_detail(customer_id: int, db: Session = Depends(get_db)):
    """Get detailed health breakdown for a customer"""
    try:
        health_service = HealthScoreService(db)
        health_detail = health_service.get_customer_health_detail(customer_id)
        return health_detail
    except CustomerNotFoundError:
        raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        logger.error(f"Error getting health detail: {e}")
        raise HTTPException(status_code=500, detail="Failed to get health detail")

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
        
        return result
    except CustomerNotFoundError:
        raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        logger.error(f"Error recording event: {e}")
        raise HTTPException(status_code=500, detail="Failed to record event")

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    try:
        health_service = HealthScoreService(db)
        stats = health_service.get_dashboard_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard stats")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

async def recalculate_health_score(customer_id: int, db: Session):
    """Background task to recalculate health score"""
    try:
        health_service = HealthScoreService(db)
        health_service.calculate_and_save_health_score(customer_id)
        logger.info(f"Recalculated health score for customer {customer_id}")
    except Exception as e:
        logger.error(f"Failed to recalculate health score for customer {customer_id}: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)