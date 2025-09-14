#!/usr/bin/env python3
"""
Test runner script for ScottLMS
Supports running frontend, backend, or all tests
"""

import subprocess
import sys
import argparse
import os


def run_command(cmd, description):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Run ScottLMS tests")
    parser.add_argument(
        "--type", 
        choices=["frontend", "backend", "all"], 
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    pytest_cmd = ["python", "-m", "pytest"]
    if args.verbose:
        pytest_cmd.append("-v")
    if args.coverage:
        pytest_cmd.extend(["--cov-report=html", "--cov-report=term-missing"])
    
    success = True
    
    if args.type in ["frontend", "all"]:
        # Run frontend tests from project root
        frontend_cmd = pytest_cmd + ["tests/test_frontend_config.py", "tests/test_frontend_utils.py"]
        if args.coverage:
            frontend_cmd.extend(["--cov=frontend"])
        
        success &= run_command(frontend_cmd, "Frontend Tests")
    
    if args.type in ["backend", "all"]:
        # Run backend tests from backend directory
        backend_cmd = pytest_cmd + ["../tests/test_backend_main.py", "../tests/test_backend_models.py"]
        if args.coverage:
            backend_cmd.extend(["--cov=backend"])
        
        # Change to backend directory for backend tests
        original_dir = os.getcwd()
        try:
            os.chdir("backend")
            success &= run_command(backend_cmd, "Backend Tests")
        finally:
            os.chdir(original_dir)
    
    if success:
        print(f"\n{'='*60}")
        print("✅ All tests passed!")
        print(f"{'='*60}")
        sys.exit(0)
    else:
        print(f"\n{'='*60}")
        print("❌ Some tests failed!")
        print(f"{'='*60}")
        sys.exit(1)


if __name__ == "__main__":
    main()
