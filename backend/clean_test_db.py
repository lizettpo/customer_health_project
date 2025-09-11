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
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

def main():
    """Clean the test database"""
    try:
        print("SQLite in-memory database is automatically clean on each test run")
        print("No manual cleanup needed!")
        
    except Exception as e:
        print(f"Error cleaning test database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()