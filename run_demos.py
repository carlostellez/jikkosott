"""
Demo runner for the Tech Lead assessment.

This script provides an easy way to run all the demonstrations
and examples included in the assessment.
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors gracefully."""
    print(f"\n{'='*60}")
    print(f"RUNNING: {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def main():
    """Run all demonstration scripts."""
    print("TECH LEAD ASSESSMENT - DEMO RUNNER")
    print("="*60)
    
    # Check if we're in the right directory
    if not os.path.exists("app/main.py"):
        print("ERROR: Please run this script from the project root directory")
        sys.exit(1)
    
    demos = [
        ("python algorithms/frequent_customers.py", "Algorithm Demo: Frequent Customer Analysis"),
        ("python algorithms/transport_routes.py", "Algorithm Demo: Transport Route Management"),
        ("python system_design/distributed_architecture.py", "System Design: Distributed Architecture"),
        ("pytest tests/ -v", "Test Suite: Unit and Integration Tests"),
    ]
    
    success_count = 0
    total_count = len(demos)
    
    for command, description in demos:
        if run_command(command, description):
            success_count += 1
        else:
            print(f"FAILED: {description}")
    
    print(f"\n{'='*60}")
    print("DEMO RUNNER SUMMARY")
    print(f"{'='*60}")
    print(f"Successful demos: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("✅ All demonstrations completed successfully!")
        print("\nTo start the API server, run:")
        print("python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("\nThen visit: http://localhost:8000/docs")
    else:
        print("❌ Some demonstrations failed. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
