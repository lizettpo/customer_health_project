#!/usr/bin/env python3
"""
Debug script for health detail endpoint
"""

import sys
import traceback
from database import SessionLocal
from services.health_score_service import HealthScoreService

def test_health_detail():
    """Test the health detail functionality"""
    db = SessionLocal()
    try:
        health_service = HealthScoreService(db)
        
        # Test with customer ID 1
        print("Testing health detail for customer ID 1...")
        health_detail = health_service.get_customer_health_detail(1)
        print("SUCCESS: Health detail retrieved")
        print(f"Customer: {health_detail['customer_name']}")
        print(f"Score: {health_detail['overall_score']}")
        print(f"Status: {health_detail['status']}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        print("Full traceback:")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_health_detail()