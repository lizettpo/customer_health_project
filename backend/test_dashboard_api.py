#!/usr/bin/env python3
"""
Test dashboard API endpoint directly
"""

import requests
import traceback

def test_dashboard_api():
    """Test the dashboard API endpoint"""
    try:
        print("Testing dashboard API endpoint...")
        response = requests.get("http://localhost:8000/api/dashboard/stats", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: Dashboard API working")
            print(f"Response: {data}")
        else:
            print(f"ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        print("Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_dashboard_api()