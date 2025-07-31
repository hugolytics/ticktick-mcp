"""
Unit tests for the task tools module.
"""

from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from datetime import datetime, timedelta

from ticktick_mcp.tools.task_tools import (
    list_tasks,
    create_task,
    update_task,
    delete_task,
    get_task_details,
    mark_task_complete,
    mark_task_incomplete,
    search_tasks,
)


class TestListTasks:
    """Test the list_tasks function."""

    @pytest.mark.asyncio
    async def test_list_tasks_basic(self, fake_ticktick_client):
        """Test basic task listing."""
        # Setup mock response
        mock_tasks = [
            {"id": "1", "title": "Task 1", "status": 0},
            {"id": "2", "title": "Task 2", "status": 1},
        ]
        fake_ticktick_client.task.get.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await list_tasks()

        assert len(result) == 2
        assert result[0]["title"] == "Task 1"
        assert result[1]["title"] == "Task 2"
        fake_ticktick_client.task.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_tasks_with_limit(self, fake_ticktick_client):
        """Test task listing with limit parameter."""
        mock_tasks = [{"id": str(i), "title": f"Task {i}"} for i in range(10)]
        fake_ticktick_client.task.get.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await list_tasks(limit=5)

        assert len(result) == 5
        fake_ticktick_client.task.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_tasks_with_project_id(self, fake_ticktick_client):
        """Test task listing with project filter."""
        mock_tasks = [{"id": "1", "title": "Project Task", "projectId": "proj123"}]
        fake_ticktick_client.task.get.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await list_tasks(project_id="proj123")

        assert len(result) == 1
        assert result[0]["projectId"] == "proj123"

    @pytest.mark.asyncio
    async def test_list_tasks_client_error(self, fake_ticktick_client):
        """Test handling of client errors."""
        fake_ticktick_client.task.get.side_effect = Exception("API Error")

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            with pytest.raises(Exception, match="API Error"):
                await list_tasks()


class TestCreateTask:
    """Test the create_task function."""

    @pytest.mark.asyncio
    async def test_create_task_basic(self, fake_ticktick_client):
        """Test basic task creation."""
        mock_task = {"id": "new123", "title": "New Task", "status": 0}
        fake_ticktick_client.task.create.return_value = mock_task

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await create_task("New Task")

        assert result["title"] == "New Task"
        assert result["id"] == "new123"
        fake_ticktick_client.task.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_task_with_details(self, fake_ticktick_client):
        """Test task creation with all details."""
        mock_task = {
            "id": "detailed123",
            "title": "Detailed Task",
            "content": "Task description",
            "dueDate": "2024-12-31T23:59:59Z",
            "priority": 1,
            "projectId": "proj456",
        }
        fake_ticktick_client.task.create.return_value = mock_task

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await create_task(
                title="Detailed Task",
                content="Task description",
                due_date="2024-12-31",
                priority=1,
                project_id="proj456",
            )

        assert result["title"] == "Detailed Task"
        assert result["content"] == "Task description"
        assert result["priority"] == 1

    @pytest.mark.asyncio
    async def test_create_task_invalid_due_date(self, fake_ticktick_client):
        """Test task creation with invalid due date format."""
        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            with pytest.raises(ValueError, match="Invalid date format"):
                await create_task("Task", due_date="invalid-date")


class TestUpdateTask:
    """Test the update_task function."""

    @pytest.mark.asyncio
    async def test_update_task_basic(self, fake_ticktick_client):
        """Test basic task update."""
        mock_task = {"id": "update123", "title": "Updated Task"}
        fake_ticktick_client.task.update.return_value = mock_task

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await update_task("update123", title="Updated Task")

        assert result["title"] == "Updated Task"
        fake_ticktick_client.task.update.assert_called_once_with(
            "update123", title="Updated Task"
        )

    @pytest.mark.asyncio
    async def test_update_task_multiple_fields(self, fake_ticktick_client):
        """Test updating multiple task fields."""
        mock_task = {
            "id": "multi123",
            "title": "Multi Update",
            "content": "New content",
            "priority": 2,
        }
        fake_ticktick_client.task.update.return_value = mock_task

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await update_task(
                "multi123", title="Multi Update", content="New content", priority=2
            )

        assert result["title"] == "Multi Update"
        assert result["content"] == "New content"
        assert result["priority"] == 2

    @pytest.mark.asyncio
    async def test_update_task_nonexistent(self, fake_ticktick_client):
        """Test updating non-existent task."""
        fake_ticktick_client.task.update.side_effect = Exception("Task not found")

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            with pytest.raises(Exception, match="Task not found"):
                await update_task("nonexistent", title="New Title")


class TestDeleteTask:
    """Test the delete_task function."""

    @pytest.mark.asyncio
    async def test_delete_task_success(self, fake_ticktick_client):
        """Test successful task deletion."""
        fake_ticktick_client.task.delete.return_value = True

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await delete_task("delete123")

        assert result is True
        fake_ticktick_client.task.delete.assert_called_once_with("delete123")

    @pytest.mark.asyncio
    async def test_delete_task_failure(self, fake_ticktick_client):
        """Test failed task deletion."""
        fake_ticktick_client.task.delete.side_effect = Exception("Delete failed")

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            with pytest.raises(Exception, match="Delete failed"):
                await delete_task("delete123")


class TestGetTaskDetails:
    """Test the get_task_details function."""

    @pytest.mark.asyncio
    async def test_get_task_details_success(self, fake_ticktick_client):
        """Test successful task detail retrieval."""
        mock_task = {
            "id": "detail123",
            "title": "Detailed Task",
            "content": "Full description",
            "status": 0,
            "priority": 1,
            "createdTime": "2024-01-01T00:00:00Z",
            "modifiedTime": "2024-01-02T00:00:00Z",
        }
        fake_ticktick_client.task.get_by_id.return_value = mock_task

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await get_task_details("detail123")

        assert result["title"] == "Detailed Task"
        assert result["content"] == "Full description"
        fake_ticktick_client.task.get_by_id.assert_called_once_with("detail123")

    @pytest.mark.asyncio
    async def test_get_task_details_not_found(self, fake_ticktick_client):
        """Test task detail retrieval for non-existent task."""
        fake_ticktick_client.task.get_by_id.return_value = None

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await get_task_details("nonexistent")

        assert result is None


class TestMarkTaskComplete:
    """Test the mark_task_complete function."""

    @pytest.mark.asyncio
    async def test_mark_task_complete_success(self, fake_ticktick_client):
        """Test successfully marking task as complete."""
        mock_task = {"id": "complete123", "title": "Task", "status": 2}
        fake_ticktick_client.task.complete.return_value = mock_task

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await mark_task_complete("complete123")

        assert result["status"] == 2
        fake_ticktick_client.task.complete.assert_called_once_with("complete123")


class TestMarkTaskIncomplete:
    """Test the mark_task_incomplete function."""

    @pytest.mark.asyncio
    async def test_mark_task_incomplete_success(self, fake_ticktick_client):
        """Test successfully marking task as incomplete."""
        mock_task = {"id": "incomplete123", "title": "Task", "status": 0}
        fake_ticktick_client.task.incomplete.return_value = mock_task

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await mark_task_incomplete("incomplete123")

        assert result["status"] == 0
        fake_ticktick_client.task.incomplete.assert_called_once_with("incomplete123")


class TestSearchTasks:
    """Test the search_tasks function."""

    @pytest.mark.asyncio
    async def test_search_tasks_by_title(self, fake_ticktick_client):
        """Test searching tasks by title."""
        mock_tasks = [
            {"id": "search1", "title": "Important meeting", "content": ""},
            {"id": "search2", "title": "Meeting notes", "content": ""},
        ]
        fake_ticktick_client.task.search.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await search_tasks("meeting")

        assert len(result) == 2
        assert all("meeting" in task["title"].lower() for task in result)
        fake_ticktick_client.task.search.assert_called_once_with("meeting")

    @pytest.mark.asyncio
    async def test_search_tasks_no_results(self, fake_ticktick_client):
        """Test searching with no results."""
        fake_ticktick_client.task.search.return_value = []

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await search_tasks("nonexistent")

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_search_tasks_with_limit(self, fake_ticktick_client):
        """Test searching with result limit."""
        mock_tasks = [{"id": str(i), "title": f"Result {i}"} for i in range(10)]
        fake_ticktick_client.task.search.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await search_tasks("result", limit=3)

        assert len(result) == 3


class TestTaskToolsErrorHandling:
    """Test error handling across task tools."""

    @pytest.mark.asyncio
    async def test_client_connection_error(self, fake_ticktick_client):
        """Test handling of client connection errors."""
        fake_ticktick_client.task.get.side_effect = ConnectionError("Network error")

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            with pytest.raises(ConnectionError, match="Network error"):
                await list_tasks()

    @pytest.mark.asyncio
    async def test_authentication_error(self, fake_ticktick_client):
        """Test handling of authentication errors."""
        fake_ticktick_client.task.get.side_effect = Exception("Authentication failed")

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            with pytest.raises(Exception, match="Authentication failed"):
                await list_tasks()


class TestTaskToolsLogging:
    """Test logging behavior in task tools."""

    @pytest.mark.asyncio
    async def test_task_operations_log_appropriately(
        self, mock_logging, fake_ticktick_client
    ):
        """Test that task operations generate appropriate log messages."""
        fake_ticktick_client.task.get.return_value = []

        with patch(
            "ticktick_mcp.tools.task_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            await list_tasks()

        # Check for expected log messages
        log_messages = [log["message"] for log in mock_logging]
        assert any("Listing tasks" in msg for msg in log_messages)
