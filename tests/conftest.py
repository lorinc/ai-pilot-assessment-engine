"""Pytest configuration and shared fixtures."""

import pytest
import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Set mock mode by default ONLY if not already set
# This allows real GCP tests to override by setting env vars before pytest
if "MOCK_LLM" not in os.environ:
    os.environ["MOCK_LLM"] = "true"
if "MOCK_FIREBASE" not in os.environ:
    os.environ["MOCK_FIREBASE"] = "true"
if "GCP_PROJECT_ID" not in os.environ:
    os.environ["GCP_PROJECT_ID"] = "test-project"
if "GCP_LOCATION" not in os.environ:
    os.environ["GCP_LOCATION"] = "us-central1"
if "GEMINI_MODEL" not in os.environ:
    os.environ["GEMINI_MODEL"] = "gemini-1.5-flash"


@pytest.fixture(scope="session")
def test_data_dir():
    """Get test data directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def mock_env(monkeypatch):
    """Set up mock environment variables for tests that explicitly request it.
    
    Note: This is NOT autouse, so tests must explicitly request this fixture
    if they want to force mock mode.
    """
    monkeypatch.setenv("MOCK_LLM", "true")
    monkeypatch.setenv("MOCK_FIREBASE", "true")
    monkeypatch.setenv("GCP_PROJECT_ID", "test-project")
    monkeypatch.setenv("GCP_LOCATION", "us-central1")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-1.5-flash")
    monkeypatch.setenv("FIREBASE_CREDENTIALS_PATH", "")
