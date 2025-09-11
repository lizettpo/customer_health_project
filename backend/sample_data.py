from calendar import monthrange
from data.models import Customer, CustomerEvent, HealthScore  # ensure HealthScore is imported

def _billing_day(created_at: datetime, day: datetime) -> bool:
    last_dom = monthrange(day.year, day.month)[1]
    bill_dom = min(created_at.day, last_dom)
    return day >= created_at and day.day == bill_dom

def populate_sample_data(db: Session):
    customers = []
    start_date = datetime.utcnow() - timedelta(days=120)

    for i in range(55):
        company_info = companies_data[i] if i < len(companies_data) else {
            "name": fake.company(),
            "segment": random.choice(["enterprise", "smb", "startup"]),
            "industry": random.choice(["Technology","Finance","Healthcare","Retail","Manufacturing","Education"]),
            "employees": random.randint(5, 10000),
            "revenue": random.randint(300, 100000)
        }

        customer = Customer(
            name=fake.name(),
            email=fake.unique.email(),  # ensure uniqueness
            company=company_info["name"],
            segment=company_info["segment"].lower(),  # normalize if your enum expects lowercase
            industry=company_info["industry"],
            employee_count=company_info["employees"],
            monthly_revenue=company_info["revenue"],
            plan_type=_get_plan_type(company_info["segment"].lower()),
            created_at=start_date + timedelta(days=random.randint(0, 30)),
            last_activity=start_date  # will be updated after events
        )
        db.add(customer)
        customers.append(customer)

    db.commit()  # get IDs

    for customer in customers:
        last_ts = _generate_customer_events(db, customer, start_date)

        # Persist health level (example via HealthScore table)
        status, score = _derive_health_status_and_score(customer)
        db.add(HealthScore(
            customer_id=customer.id,
            score=score,
            status=status,
            factors={},             # or fill with your factor breakdown
            recommendations=[],
            calculated_at=datetime.utcnow()
        ))

        # Make last_activity consistent with generated data
        customer.last_activity = last_ts or customer.created_at
        db.add(customer)

    db.commit()

def _generate_customer_events(db: Session, customer: Customer, start_date: datetime):
    health_profile = _determine_health_profile(customer)

    # start generating no earlier than the customer's creation
    current_date = max(start_date, customer.created_at).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = datetime.utcnow()
    last_event_ts = None

    while current_date < end_date:
        # Login
        if _should_generate_event(health_profile, "login", current_date):
            ts = current_date + timedelta(hours=random.randint(8, 18))
            db.add(CustomerEvent(customer_id=customer.id, event_type="login",
                                 event_data={"ip_address": fake.ipv4(), "user_agent": "web"},
                                 timestamp=ts))
            last_event_ts = max(last_event_ts or ts, ts)

        # Feature use
        if _should_generate_event(health_profile, "feature_use", current_date):
            features = ["dashboard","analytics","reports","user_management","api_keys","integrations",
                        "billing","notifications","advanced_search","export_data","collaboration","automation"]
            pool = features if health_profile == "healthy" else (features[:8] if health_profile == "at_risk" else features[:4])
            for feature in random.sample(pool, random.randint(2, 5) if health_profile=="healthy"
                                                else random.randint(1, 3) if health_profile=="at_risk"
                                                else random.randint(1, 2)):
                ts = current_date + timedelta(hours=random.randint(9, 17))
                db.add(CustomerEvent(customer_id=customer.id, event_type="feature_use",
                                     event_data={"feature_name": feature, "duration_minutes": random.randint(2, 30)},
                                     timestamp=ts))
                last_event_ts = max(last_event_ts, ts) if last_event_ts else ts

        # Support ticket
        if _should_generate_event(health_profile, "support_ticket", current_date):
            priorities = ["low","medium","high","urgent"]
            w = {"healthy":[0.4,0.4,0.15,0.05],"at_risk":[0.2,0.3,0.3,0.2],"critical":[0.1,0.2,0.4,0.3]}[health_profile]
            ts = current_date + timedelta(hours=random.randint(10, 16))
            db.add(CustomerEvent(customer_id=customer.id, event_type="support_ticket",
                                 event_data={"ticket_type": random.choice(["bug_report","feature_request","billing_question","technical_issue","account_help"]),
                                             "priority": random.choices(priorities, weights=w)[0],
                                             "status": random.choice(["open","in_progress","resolved"])},
                                 timestamp=ts))
            last_event_ts = max(last_event_ts, ts) if last_event_ts else ts

        # Payment (monthly with end-of-month fallback)
        if _billing_day(customer.created_at, current_date):
            ts = current_date + timedelta(hours=random.randint(1, 5))
            db.add(CustomerEvent(customer_id=customer.id, event_type="payment",
                                 event_data={"amount": customer.monthly_revenue,
                                             "status": _get_payment_status(health_profile),
                                             "payment_method": random.choice(["credit_card","bank_transfer","check"]),
                                             "invoice_id": f"INV-{random.randint(10000, 99999)}"},
                                 timestamp=ts))
            last_event_ts = max(last_event_ts, ts) if last_event_ts else ts

        # API calls
        if _should_generate_event(health_profile, "api_call", current_date):
            for _ in range(_get_api_calls_per_day(customer.segment, health_profile)):
                ts = current_date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
                db.add(CustomerEvent(customer_id=customer.id, event_type="api_call",
                                     event_data={"endpoint": random.choice(["/api/users","/api/data","/api/analytics","/api/reports","/api/integrations","/api/webhooks","/api/billing"]),
                                                 "method": random.choice(["GET","POST","PUT","DELETE"]),
                                                 "response_code": random.choices([200,201,400,401,500], weights=[0.7,0.1,0.1,0.05,0.05])[0],
                                                 "response_time_ms": random.randint(50, 2000)},
                                     timestamp=ts))
                last_event_ts = max(last_event_ts, ts) if last_event_ts else ts

        current_date += timedelta(days=1)

    return last_event_ts

def _derive_health_status_and_score(customer: Customer):
    # Example: map segments/usage tendencies to a score distribution
    profile = _determine_health_profile(customer)
    if profile == "healthy":
        return "healthy", random.randint(80, 100)
    if profile == "at_risk":
        return "at_risk", random.randint(50, 79)
    return "critical", random.randint(20, 49)

