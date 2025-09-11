"""
Sample data generation for the application
"""

import random
import json
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.orm import Session

# Import database models
from data.models import Customer, CustomerEvent

fake = Faker()
Faker.seed(42)  # For reproducible data
random.seed(42)

def populate_sample_data(db: Session):
    """Generate realistic sample data for 50+ customers with 3+ months of history"""
    
    # Company data for realistic customer profiles
    companies_data = [
        # Enterprise customers
        {"name": "TechCorp Solutions", "segment": "enterprise", "industry": "Technology", "employees": 5000, "revenue": 50000},
        {"name": "Global Finance Inc", "segment": "enterprise", "industry": "Finance", "employees": 12000, "revenue": 100000},
        {"name": "MedTech Industries", "segment": "enterprise", "industry": "Healthcare", "employees": 3500, "revenue": 75000},
        {"name": "RetailChain LLC", "segment": "enterprise", "industry": "Retail", "employees": 8000, "revenue": 45000},
        {"name": "Manufacturing Plus", "segment": "enterprise", "industry": "Manufacturing", "employees": 6000, "revenue": 60000},
        
        # SMB customers
        {"name": "Local Marketing Agency", "segment": "smb", "industry": "Marketing", "employees": 45, "revenue": 5000},
        {"name": "Downtown Law Firm", "segment": "smb", "industry": "Legal", "employees": 25, "revenue": 8000},
        {"name": "Creative Design Studio", "segment": "smb", "industry": "Design", "employees": 30, "revenue": 4500},
        {"name": "Regional Consulting", "segment": "smb", "industry": "Consulting", "employees": 60, "revenue": 12000},
        {"name": "Mid-Size Software Co", "segment": "smb", "industry": "Technology", "employees": 120, "revenue": 15000},
        
        # Startup customers
        {"name": "AI Startup Alpha", "segment": "startup", "industry": "AI/ML", "employees": 8, "revenue": 500},
        {"name": "FinTech Beta", "segment": "startup", "industry": "Finance", "employees": 12, "revenue": 800},
        {"name": "Health App Gamma", "segment": "startup", "industry": "Healthcare", "employees": 6, "revenue": 300},
        {"name": "EdTech Delta", "segment": "startup", "industry": "Education", "employees": 15, "revenue": 1200},
        {"name": "Green Energy Epsilon", "segment": "startup", "industry": "Energy", "employees": 10, "revenue": 600},
    ]
    
    customers = []
    start_date = datetime.utcnow() - timedelta(days=120)  # 4 months of history
    
    # Create diverse customer base (50+ customers)
    for i in range(55):
        if i < len(companies_data):
            company_info = companies_data[i]
        else:
            # Generate additional companies
            company_info = {
                "name": fake.company(),
                "segment": random.choice(["enterprise", "smb", "startup"]),
                "industry": random.choice(["Technology", "Finance", "Healthcare", "Retail", "Manufacturing", "Education"]),
                "employees": random.randint(5, 10000),
                "revenue": random.randint(300, 100000)
            }
        
        # Create customer with realistic data
        customer = Customer(
            name=fake.name(),
            email=fake.email(),
            company=company_info["name"],
            segment=company_info["segment"],
            industry=company_info["industry"],
            employee_count=company_info["employees"],
            monthly_revenue=company_info["revenue"],
            plan_type=_get_plan_type(company_info["segment"]),
            created_at=start_date + timedelta(days=random.randint(0, 30)),
            last_activity=datetime.utcnow() - timedelta(days=random.randint(0, 7))
        )
        
        db.add(customer)
        customers.append(customer)
    
    # Commit customers first to get IDs
    db.commit()
    
    # Generate realistic event history for each customer
    for customer in customers:
        _generate_customer_events(db, customer, start_date)
    
    db.commit()

def _get_plan_type(segment: str) -> str:
    """Get appropriate plan type based on segment"""
    if segment == "enterprise":
        return random.choice(["enterprise", "pro"])
    elif segment == "smb":
        return random.choice(["pro", "basic"])
    else:  # startup
        return random.choice(["basic", "pro"])

def _generate_customer_events(db: Session, customer: Customer, start_date: datetime):
    """Generate realistic event history for a customer"""
    
    # Determine customer health profile (affects event generation)
    health_profile = _determine_health_profile(customer)
    
    current_date = start_date
    end_date = datetime.utcnow()
    
    # Generate events over time
    while current_date < end_date:
        # Login events - frequency based on health profile
        if _should_generate_event(health_profile, "login", current_date):
            db.add(CustomerEvent(
                customer_id=customer.id,
                event_type="login",
                event_data={"ip_address": fake.ipv4(), "user_agent": "web"},
                timestamp=current_date + timedelta(hours=random.randint(8, 18))
            ))
        
        # Feature usage events
        if _should_generate_event(health_profile, "feature_use", current_date):
            features = [
                "dashboard", "analytics", "reports", "user_management", 
                "api_keys", "integrations", "billing", "notifications",
                "advanced_search", "export_data", "collaboration", "automation"
            ]
            
            # Healthy customers use more diverse features
            if health_profile == "healthy":
                selected_features = random.sample(features, random.randint(2, 5))
            elif health_profile == "at_risk":
                selected_features = random.sample(features, random.randint(1, 3))
            else:  # critical
                selected_features = random.sample(features[:4], random.randint(1, 2))
            
            for feature in selected_features:
                db.add(CustomerEvent(
                    customer_id=customer.id,
                    event_type="feature_use",
                    event_data={"feature_name": feature, "duration_minutes": random.randint(2, 30)},
                    timestamp=current_date + timedelta(hours=random.randint(9, 17))
                ))
        
        # Support ticket events
        if _should_generate_event(health_profile, "support_ticket", current_date):
            ticket_types = ["bug_report", "feature_request", "billing_question", "technical_issue", "account_help"]
            priorities = ["low", "medium", "high", "urgent"]
            
            priority_weights = {
                "healthy": [0.4, 0.4, 0.15, 0.05],
                "at_risk": [0.2, 0.3, 0.3, 0.2],
                "critical": [0.1, 0.2, 0.4, 0.3]
            }
            
            db.add(CustomerEvent(
                customer_id=customer.id,
                event_type="support_ticket",
                event_data={
                    "ticket_type": random.choice(ticket_types),
                    "priority": random.choices(priorities, weights=priority_weights[health_profile])[0],
                    "status": random.choice(["open", "in_progress", "resolved"])
                },
                timestamp=current_date + timedelta(hours=random.randint(10, 16))
            ))
        
        # Payment events - monthly billing cycles
        if current_date.day == customer.created_at.day and current_date >= customer.created_at:
            payment_status = _get_payment_status(health_profile)
            
            db.add(CustomerEvent(
                customer_id=customer.id,
                event_type="payment",
                event_data={
                    "amount": customer.monthly_revenue,
                    "status": payment_status,
                    "payment_method": random.choice(["credit_card", "bank_transfer", "check"]),
                    "invoice_id": f"INV-{random.randint(10000, 99999)}"
                },
                timestamp=current_date + timedelta(hours=random.randint(1, 5))
            ))
        
        # API usage events
        if _should_generate_event(health_profile, "api_call", current_date):
            api_endpoints = [
                "/api/users", "/api/data", "/api/analytics", "/api/reports",
                "/api/integrations", "/api/webhooks", "/api/billing"
            ]
            
            # Generate multiple API calls per day for active customers
            num_calls = _get_api_calls_per_day(customer.segment, health_profile)
            
            for _ in range(num_calls):
                db.add(CustomerEvent(
                    customer_id=customer.id,
                    event_type="api_call",
                    event_data={
                        "endpoint": random.choice(api_endpoints),
                        "method": random.choice(["GET", "POST", "PUT", "DELETE"]),
                        "response_code": random.choices([200, 201, 400, 401, 500], weights=[0.7, 0.1, 0.1, 0.05, 0.05])[0],
                        "response_time_ms": random.randint(50, 2000)
                    },
                    timestamp=current_date + timedelta(
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    )
                ))
        
        current_date += timedelta(days=1)

def _determine_health_profile(customer: Customer) -> str:
    """Determine health profile based on customer characteristics"""
    if customer.segment == "enterprise":
        return random.choices(["healthy", "at_risk", "critical"], weights=[0.7, 0.2, 0.1])[0]
    elif customer.segment == "smb":
        return random.choices(["healthy", "at_risk", "critical"], weights=[0.5, 0.35, 0.15])[0]
    else:  # startup
        return random.choices(["healthy", "at_risk", "critical"], weights=[0.4, 0.4, 0.2])[0]

def _should_generate_event(health_profile: str, event_type: str, current_date: datetime) -> bool:
    """Determine if an event should be generated"""
    probabilities = {
        "login": {"healthy": 0.8, "at_risk": 0.4, "critical": 0.15},
        "feature_use": {"healthy": 0.7, "at_risk": 0.3, "critical": 0.1},
        "support_ticket": {"healthy": 0.05, "at_risk": 0.15, "critical": 0.3},
        "api_call": {"healthy": 0.9, "at_risk": 0.6, "critical": 0.2}
    }
    
    # Weekend adjustments
    if current_date.weekday() >= 5:
        for profile in probabilities[event_type]:
            probabilities[event_type][profile] *= 0.3
    
    return random.random() < probabilities[event_type][health_profile]

def _get_payment_status(health_profile: str) -> str:
    """Get payment status based on health profile"""
    if health_profile == "healthy":
        return random.choices(["paid_on_time", "paid_late"], weights=[0.95, 0.05])[0]
    elif health_profile == "at_risk":
        return random.choices(["paid_on_time", "paid_late"], weights=[0.8, 0.2])[0]
    else:  # critical
        return random.choices(["paid_on_time", "paid_late", "overdue"], weights=[0.6, 0.3, 0.1])[0]

def _get_api_calls_per_day(segment: str, health_profile: str) -> int:
    """Get number of API calls per day"""
    base_calls = {"enterprise": 50, "smb": 20, "startup": 8}
    multipliers = {"healthy": 1.0, "at_risk": 0.6, "critical": 0.3}
    
    calls = int(base_calls[segment] * multipliers[health_profile])
    return random.randint(max(1, calls - 5), calls + 10)