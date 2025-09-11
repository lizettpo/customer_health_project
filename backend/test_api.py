#!/usr/bin/env python3
"""
Test API endpoint directly
"""

import sys
import traceback
from fastapi.testclient import TestClient
from main import app

def test_api_endpoint():
    """Test the API endpoint directly"""
    client = TestClient(app)
    
    try:
        print("Testing API endpoint /api/customers/1/health...")
        response = client.get("/api/customers/1/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        print("Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_api_endpoint()