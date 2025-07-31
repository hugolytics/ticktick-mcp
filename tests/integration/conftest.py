"""
Integration test configuration.
"""
# Import the HTTP server fixture
from .conftest_http import http_server

__all__ = ["http_server"]
