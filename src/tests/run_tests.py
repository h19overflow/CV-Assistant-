"""
Test runner script for Resume System.
Provides easy commands to run different types of tests.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command: list, description: str):
    """Run a command and handle the output."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print('='*60)

    try:
        result = subprocess.run(command, check=True, capture_output=False)
        print(f"\n✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"\n✗ Command not found: {command[0]}")
        print("Make sure pytest is installed: pip install pytest")
        return False

def main():
    """Main test runner."""
    # Change to project root directory
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)

    if len(sys.argv) < 2:
        print("Usage: python src/tests/run_tests.py <test_type>")
        print("\nAvailable test types:")
        print("  all         - Run all tests")
        print("  unit        - Run only unit tests")
        print("  integration - Run only integration tests")
        print("  auth        - Run only authentication tests")
        print("  coverage    - Run tests with coverage report")
        print("  fast        - Run tests without slow tests")
        return

    test_type = sys.argv[1].lower()

    # Base pytest command
    base_cmd = ["python", "-m", "pytest", "src/tests/"]

    commands = {
        "all": {
            "cmd": base_cmd + ["-v"],
            "desc": "All tests"
        },
        "unit": {
            "cmd": base_cmd + ["-v", "-m", "unit", "src/tests/unit/"],
            "desc": "Unit tests only"
        },
        "integration": {
            "cmd": base_cmd + ["-v", "-m", "integration", "src/tests/integration/"],
            "desc": "Integration tests only"
        },
        "auth": {
            "cmd": base_cmd + ["-v", "-m", "auth"],
            "desc": "Authentication tests only"
        },
        "coverage": {
            "cmd": base_cmd + ["-v", "--cov=src/backend", "--cov-report=term-missing", "--cov-report=html"],
            "desc": "All tests with coverage report"
        },
        "fast": {
            "cmd": base_cmd + ["-v", "-m", "not slow"],
            "desc": "Fast tests only (excluding slow tests)"
        }
    }

    if test_type not in commands:
        print(f"Unknown test type: {test_type}")
        print(f"Available types: {', '.join(commands.keys())}")
        return

    # Install test dependencies if needed
    print("Checking test dependencies...")
    install_cmd = ["python", "-m", "pip", "install", "-r", "src/tests/requirements.txt"]
    subprocess.run(install_cmd, capture_output=True)

    # Run the selected tests
    test_info = commands[test_type]
    success = run_command(test_info["cmd"], test_info["desc"])

    if success:
        print(f"\n🎉 {test_info['desc']} passed!")
        if test_type == "coverage":
            print("\n📊 Coverage report generated in 'htmlcov/' directory")
            print("Open 'htmlcov/index.html' in your browser to view detailed coverage")
    else:
        print(f"\n❌ {test_info['desc']} failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()