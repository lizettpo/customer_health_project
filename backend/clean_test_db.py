#!/usr/bin/env python3
"""
Utility script to clean the test database
Usage: python clean_test_db.py
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set test environment
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "postgresql://postgres:password123@localhost:5434/customer_health_test"

def main():
    """Clean the test database"""
    try:
        # Import after setting environment variables
        from tests.conftest import clean_database
        
        print("Cleaning test database...")
        clean_database()
        print("Test database cleaned successfully!")
        
    except Exception as e:
        print(f"Error cleaning test database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()