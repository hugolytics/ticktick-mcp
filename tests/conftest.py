"""
Test fixtures and utilities for ticktick-mcp tests.
"""

import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator
from unittest.mock import MagicMock, Mock, patch

import pytest


class DummyMCP:
    """Mock MCP instance that records method calls without executing them."""

    def __init__(self, name: str = "test-server"):
        self.name = name
        self.tools = {}
        self.run_calls = []
        self.metadata = {"name": name, "version": "test"}

    def run(self, transport: str = "stdio", host: str = "0.0.0.0", port: int = 8150):
        """Record run call parameters."""
        self.run_calls.append({"transport": transport, "host": host, "port": port})

    def tool(self, name: str = None, description: str = None):
        """Mock tool decorator."""

        def decorator(func):
            tool_name = name or func.__name__
            self.tools[tool_name] = {"function": func, "description": description}
            return func

        return decorator


class FakeTickTickClient:
    """Fake TickTick client for testing without real API calls."""

    def __init__(self):
        self.authenticated = False
        self.tasks = []
        self.projects = []
        self.call_log = []

    def authenticate(self) -> bool:
        """Simulate authentication."""
        self.call_log.append("authenticate")
        self.authenticated = True
        return True

    def get_tasks(self, project_id: str = None) -> list:
        """Return fake tasks."""
        self.call_log.append(f"get_tasks(project_id={project_id})")
        if project_id:
            return [t for t in self.tasks if t.get("projectId") == project_id]
        return self.tasks.copy()

    def create_task(self, title: str, **kwargs) -> dict:
        """Create a fake task."""
        task = {
            "id": f"task_{len(self.tasks)}",
            "title": title,
            "completed": False,
            "projectId": kwargs.get("projectId", "default"),
            **kwargs,
        }
        self.tasks.append(task)
        self.call_log.append(f"create_task(title={title})")
        return task

    def update_task(self, task_id: str, **kwargs) -> dict:
        """Update a fake task."""
        self.call_log.append(f"update_task(task_id={task_id})")
        for task in self.tasks:
            if task["id"] == task_id:
                task.update(kwargs)
                return task
        raise ValueError(f"Task {task_id} not found")

    def delete_task(self, task_id: str) -> bool:
        """Delete a fake task."""
        self.call_log.append(f"delete_task(task_id={task_id})")
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                del self.tasks[i]
                return True
        return False


class FakeTickTickClientSingleton:
    """Fake singleton that returns the same FakeTickTickClient instance."""

    _instance = None
    _initialized = False

    @classmethod
    def get(cls):
        """Return the singleton instance."""
        if cls._instance is None:
            cls._instance = FakeTickTickClient()
        return cls._instance

    @classmethod
    def reset(cls):
        """Reset the singleton for testing."""
        cls._instance = None
        cls._initialized = False


@pytest.fixture
def clean_env(monkeypatch):
    """
    Factory fixture.

    * Clears all TICKTICK_* and SERVER_* variables for the duration
      of the test.
    * Returns a helper with .set(**envs) and .clear(*names) so tests
      can push additional env-vars on demand.

    This keeps tests hermetic without manual os.environ surgery.
    """
    prefixes = ("TICKTICK_", "SERVER_")
    saved = {k: v for k, v in os.environ.items() if k.startswith(prefixes)}

    # wipe current vars
    for k in saved:
        monkeypatch.delenv(k, raising=False)

    class _EnvMgr:
        def set(self, **kwargs):
            for k, v in kwargs.items():
                monkeypatch.setenv(k, str(v))

        def clear(self, *names):
            for name in names:
                monkeypatch.delenv(name, raising=False)

    yield _EnvMgr()

    # restore originals
    for k in list(os.environ):
        if k.startswith(prefixes):
            monkeypatch.delenv(k, raising=False)
    for k, v in saved.items():
        monkeypatch.setenv(k, v)


@pytest.fixture
def dummy_mcp(monkeypatch) -> DummyMCP:
    """
    Fixture that replaces the real MCP instance with a DummyMCP
    that records method calls without executing them.
    """
    dummy = DummyMCP()

    # Monkeypatch the mcp instance in the mcp_instance module
    monkeypatch.setattr("ticktick_mcp.mcp_instance.mcp", dummy)

    # Also patch any imports of mcp in other modules
    monkeypatch.setattr("src.main.mcp", dummy)

    return dummy


@pytest.fixture
def fake_client(monkeypatch) -> FakeTickTickClient:
    """
    Fixture that provides a fake TickTick client that doesn't make real API calls.
    """
    fake_singleton = FakeTickTickClientSingleton()
    fake_singleton.reset()  # Ensure clean state

    # Monkeypatch the singleton class
    monkeypatch.setattr("ticktick_mcp.client.TickTickClientSingleton", fake_singleton)

    return fake_singleton.get()


@pytest.fixture
def tmp_config_dir(tmp_path, monkeypatch) -> Path:
    """
    Fixture that creates a temporary directory for config and token cache
    and points the config system to use it.
    """
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    # Monkeypatch the config directory path
    monkeypatch.setattr("ticktick_mcp.config.dotenv_dir_path", config_dir)

    return config_dir


@pytest.fixture
def sample_tasks() -> list:
    """Fixture providing sample task data for testing."""
    return [
        {
            "id": "task_1",
            "title": "Test Task 1",
            "content": "This is a test task",
            "completed": False,
            "projectId": "project_1",
            "createdTime": "2025-01-01T10:00:00Z",
            "modifiedTime": "2025-01-01T10:00:00Z",
        },
        {
            "id": "task_2",
            "title": "Test Task 2",
            "content": "Another test task",
            "completed": True,
            "projectId": "project_1",
            "createdTime": "2025-01-02T10:00:00Z",
            "modifiedTime": "2025-01-02T10:00:00Z",
        },
        {
            "id": "task_3",
            "title": "Test Task 3",
            "content": "Third test task",
            "completed": False,
            "projectId": "project_2",
            "createdTime": "2025-01-03T10:00:00Z",
            "modifiedTime": "2025-01-03T10:00:00Z",
        },
    ]


@pytest.fixture
def mock_logging(monkeypatch):
    """Fixture that mocks logging to capture log messages in tests."""
    logs = []

    def mock_log(level, msg, *args, **kwargs):
        logs.append({"level": level, "message": msg % args if args else msg})

    monkeypatch.setattr(
        "logging.info",
        lambda msg, *args, **kwargs: mock_log("INFO", msg, *args, **kwargs),
    )
    monkeypatch.setattr(
        "logging.error",
        lambda msg, *args, **kwargs: mock_log("ERROR", msg, *args, **kwargs),
    )
    monkeypatch.setattr(
        "logging.warning",
        lambda msg, *args, **kwargs: mock_log("WARNING", msg, *args, **kwargs),
    )

    return logs


@pytest.fixture(autouse=True)
def reset_singletons():
    """Auto-use fixture that resets singleton state between tests."""
    yield
    # Reset any singleton state here
    FakeTickTickClientSingleton.reset()


@pytest.fixture(autouse=True, scope="session")
def patch_fake_client(monkeypatch):
    """Ensure HTTP-spawned process also uses fake client."""
    from ticktick_mcp.client import FakeTickTickClientSingleton as _fake
    monkeypatch.setattr("ticktick_mcp.client.TickTickClientSingleton", _fake)


@pytest.fixture
def mock_env_file(tmp_path):
    """Fixture that creates a temporary .env file with test credentials."""
    env_file = tmp_path / ".env"
    env_content = """
TICKTICK_CLIENT_ID=test_client_id
TICKTICK_CLIENT_SECRET=test_client_secret
TICKTICK_REDIRECT_URI=http://localhost:8080/callback
TICKTICK_USERNAME=test@example.com
TICKTICK_PASSWORD=test_password
SERVER_TRANSPORT=stdio
SERVER_HOST=0.0.0.0
SERVER_PORT=8150
"""
    env_file.write_text(env_content.strip())
    return env_file
