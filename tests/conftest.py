"""
Pytest configuration and fixtures for FastAPI application tests.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities

# Store the original activities state
ORIGINAL_ACTIVITIES = {
    activity_name: {
        "description": activity_data["description"],
        "schedule": activity_data["schedule"],
        "max_participants": activity_data["max_participants"],
        "participants": activity_data["participants"].copy()
    }
    for activity_name, activity_data in activities.items()
}


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient for the FastAPI application.
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_app():
    """
    Fixture that resets the app state before each test.
    This ensures test isolation by restoring the original activities.
    Runs automatically before each test due to autouse=True.
    """
    # Setup: Reset to original state before test
    activities.clear()
    for activity_name, activity_data in ORIGINAL_ACTIVITIES.items():
        activities[activity_name] = {
            "description": activity_data["description"],
            "schedule": activity_data["schedule"],
            "max_participants": activity_data["max_participants"],
            "participants": activity_data["participants"].copy()
        }
    
    # Yield control to test
    yield
    
    # Teardown: Reset after test (optional but good practice)
    activities.clear()
    for activity_name, activity_data in ORIGINAL_ACTIVITIES.items():
        activities[activity_name] = {
            "description": activity_data["description"],
            "schedule": activity_data["schedule"],
            "max_participants": activity_data["max_participants"],
            "participants": activity_data["participants"].copy()
        }
