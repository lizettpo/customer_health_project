#!/usr/bin/env python3
"""
Test runner script for the customer health project
Runs all tests with coverage reporting
"""
import subprocess
import sys
import os

def run_tests():
    """Run all tests with coverage reporting"""
    print("Running Customer Health Project Tests")
    print("=" * 50)
    
    # Set test environment
    os.environ["TESTING"] = "true"
    
    try:
        # Run tests with coverage
        cmd = [
            sys.executable, "-m", "pytest", 
            "tests/",
            "--verbose",
            "--cov=.",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-fail-under=85",
            "--tb=short"
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=False, capture_output=False)
        
        if result.returncode == 0:
            print("\nAll tests passed!")
            print("Coverage report generated in htmlcov/ directory")
        else:
            print(f"\nTests failed with return code: {result.returncode}")
            
        return result.returncode
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)