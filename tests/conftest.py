"""
Pytest configuration and fixtures for API tests.
Provides test client and sample activities data with isolation between tests.
"""

import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture providing a FastAPI TestClient for making requests.
    """
    return TestClient(app)


@pytest.fixture
def mock_activities(monkeypatch):
    """
    Fixture providing isolated activities data for each test.
    Uses deep copy to prevent state leakage between tests.
    """
    isolated_activities = copy.deepcopy(activities)
    monkeypatch.setattr("src.app.activities", isolated_activities)
    return isolated_activities
