"""Pytest configuration and fixtures for OpenRefine MCP tests."""

from pathlib import Path
import pytest


def pytest_configure(config):
    """Configure pytest-vcr settings."""
    config.addinivalue_line(
        "markers", "vcr: mark test to record HTTP interactions with VCR"
    )


@pytest.fixture(scope="session")
def vcr_config():
    """VCR configuration for pytest-vcr."""
    return {
        "cassette_library_dir": str(Path(__file__).parent / "cassettes"),
        "record_mode": "once",
        "match_on": ["method", "scheme", "host", "port", "path", "query"],
        "filter_headers": ["authorization"],
        "serializer": "yaml",
    }
